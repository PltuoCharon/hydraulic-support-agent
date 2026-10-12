"""Immutable pipeline evidence and aggregates over existing W41 evaluation."""

from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from app.models.optimization_contract import (
    ConstraintViolation, ExperimentModel, ObjectiveValue, OptimizationCandidate,
)


def pipeline_violations(original: OptimizationCandidate, evaluated: OptimizationCandidate):
    if evaluated.ranking_eligible:
        return ()
    # Keep original failure evidence as well as the new W41 classification.
    violations = []
    for violation in (*original.constraint_violations, *evaluated.constraint_violations):
        if violation not in violations:
            violations.append(violation)
    return tuple(violations)


def failure_reason(candidate: OptimizationCandidate) -> str | None:
    if candidate.ranking_eligible:
        return None
    record = candidate.evaluation_record
    detail = record.error.diagnostic if record.error is not None else record.result.constraints[0].reason
    return f"{record.outcome}: {detail}"


class OptimizationEvaluationRecord(ExperimentModel):
    candidate_id: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,128}$")
    evaluation_status: Literal["SUCCESS", "FAILED"]
    objective_values: tuple[ObjectiveValue, ...]
    feasible: bool
    violations: tuple[ConstraintViolation, ...]
    source: Literal["W41_EVALUATOR"] = "W41_EVALUATOR"
    input_candidate: OptimizationCandidate
    evaluated_candidate: OptimizationCandidate
    request_mode: Literal["REPLAY", "DESIGN_VECTOR", "MISSING_DESIGN", "READINESS_GATE"]
    failure_reason: str | None

    @field_validator("violations", mode="before")
    @classmethod
    def immutable_violations(cls, value):
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def consistent_evidence(self) -> Self:
        original, evaluated = self.input_candidate, self.evaluated_candidate
        if self.candidate_id != original.candidate_id or self.candidate_id != evaluated.candidate_id:
            raise ValueError("record identifier must agree with both candidate snapshots")
        if original.problem != evaluated.problem or evaluated.evaluation_record is None:
            raise ValueError("pipeline record requires new W41 evidence for the same problem")
        if evaluated.design_vector is not None and evaluated.design_vector != original.design_vector:
            raise ValueError("pipeline cannot replace candidate design variables")
        expected_mode = (
            "REPLAY" if original.evaluation_record is not None and original.evaluation_record.request is not None
            else "READINESS_GATE" if original.problem.comparison_contract is None
            else "MISSING_DESIGN" if original.design_vector is None else "DESIGN_VECTOR"
        )
        if self.request_mode != expected_mode:
            raise ValueError("request mode must identify the available original evidence")
        if expected_mode == "REPLAY" and evaluated.evaluation_record.request != original.evaluation_record.request:
            raise ValueError("replay must preserve the complete original evaluation request")
        success = evaluated.ranking_eligible
        if (self.evaluation_status, self.feasible) != ("SUCCESS" if success else "FAILED", success):
            raise ValueError("success and feasibility require actual comparable W41 evaluation")
        if self.objective_values != evaluated.objective_values:
            raise ValueError("objective values must equal newly evaluated W41 metrics")
        if self.violations != pipeline_violations(original, evaluated) or self.failure_reason != failure_reason(evaluated):
            raise ValueError("failure reasons and violations must retain actual evidence")
        return self


def select_best_record(records):
    """Select only successful feasible evidence, with stable ties by input order."""
    eligible = [r for r in records if r.evaluation_status == "SUCCESS" and r.feasible]
    return min(eligible, key=lambda r: r.objective_values[0].value) if eligible else None


class OptimizationPipelineResult(ExperimentModel):
    records: tuple[OptimizationEvaluationRecord, ...]
    total_candidates: int = Field(ge=0)
    evaluated_candidates: int = Field(ge=0)
    successful_candidates: int = Field(ge=0)
    failed_candidates: int = Field(ge=0)
    best_candidate_id: str | None
    best_objective: ObjectiveValue | None

    @field_validator("records", mode="before")
    @classmethod
    def immutable_records(cls, value):
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def aggregate_evidence(self) -> Self:
        records = self.records
        if len({r.candidate_id for r in records}) != len(records):
            raise ValueError("pipeline record identifiers must be unique")
        if records:
            problem = records[0].input_candidate.problem
            if any(r.input_candidate.problem != problem for r in records):
                raise ValueError("one pipeline batch must use one problem and comparison contract")
            if len(records) > problem.evaluation_budget:
                raise ValueError("pipeline batch exceeds problem candidate budget")
        successes = sum(r.evaluation_status == "SUCCESS" for r in records)
        if (self.total_candidates, self.evaluated_candidates, self.successful_candidates, self.failed_candidates) != (
            len(records), len(records), successes, len(records) - successes,
        ):
            raise ValueError("pipeline counts must agree with actual W41 attempt records")
        best = select_best_record(records)
        if (self.best_candidate_id, self.best_objective) != (
            best.candidate_id if best is not None else None,
            best.objective_values[0] if best is not None else None,
        ):
            raise ValueError("best must come from a successful feasible record with the minimum objective")
        return self
