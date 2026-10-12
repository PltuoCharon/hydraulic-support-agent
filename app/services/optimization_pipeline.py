"""Uniform optimization-candidate entrypoint, reusing the W41 D5/D4 chain."""

from collections.abc import Iterable

from app.models.optimization_contract import OptimizationCandidate
from app.models.optimization_pipeline import (
    OptimizationEvaluationRecord, OptimizationPipelineResult, failure_reason,
    pipeline_violations, select_best_record,
)
from app.services import linkage_optimization_evaluation as w41


def _request(candidate):
    previous = candidate.evaluation_record
    if previous is not None and previous.request is not None:
        return previous.request.model_dump(mode="python"), "REPLAY"
    comparison = candidate.problem.comparison_contract
    if comparison is None:
        # Engineering metadata only; do not fill missing geometry or promote readiness.
        return dict(case=dict(
            case_id=candidate.problem.case_id, domain=candidate.problem.domain,
            readiness=candidate.problem.readiness,
            source_text="OptimizationProblem metadata; pipeline readiness gate; no geometry supplied",
            engineering_verified=False,
        ), objective=None), "READINESS_GATE"
    raw = dict(
        case=comparison.case.model_dump(mode="python"), candidate=None,
        plan=comparison.plan.model_dump(mode="python"),
        objective=comparison.objective.model_dump(mode="python"),
    )
    if candidate.design_vector is None:
        # Original invalid raw input is not retained by D5. Explicitly validate
        # the missing design instead of pretending to replay or inventing one.
        return raw, "MISSING_DESIGN"
    raw["candidate"] = dict(
        case=comparison.case.model_dump(mode="python"),
        design={v.variable_name: dict(
            value=v.value, unit=v.unit, source_text=v.source,
            origin="USER_INPUT", evidence_status="PARTIAL",
            formula_ids=[], calculation_record_ids=[],
        ) for v in candidate.design_vector},
        bounds=comparison.bounds.model_dump(mode="python"),
        configuration=comparison.configuration.model_dump(mode="python"),
    )
    return raw, "DESIGN_VECTOR"


class OptimizationEvaluationPipeline:
    def evaluate_candidate(self, candidate: OptimizationCandidate) -> OptimizationEvaluationRecord:
        candidate = OptimizationCandidate.model_validate(candidate)
        raw, mode = _request(candidate)
        record = w41.evaluate_candidate_safely(candidate.candidate_id, raw, candidate.problem.comparison_contract)
        evaluated = OptimizationCandidate.from_w41(candidate.problem, record)
        success = evaluated.ranking_eligible
        return OptimizationEvaluationRecord(
            candidate_id=candidate.candidate_id, evaluation_status="SUCCESS" if success else "FAILED",
            objective_values=evaluated.objective_values, feasible=success,
            violations=pipeline_violations(candidate, evaluated), input_candidate=candidate,
            evaluated_candidate=evaluated, request_mode=mode, failure_reason=failure_reason(evaluated),
        )

    def evaluate_candidates(self, candidates: Iterable[OptimizationCandidate]) -> OptimizationPipelineResult:
        snapshots = tuple(OptimizationCandidate.model_validate(c) for c in candidates)
        if len({c.candidate_id for c in snapshots}) != len(snapshots):
            raise ValueError("pipeline candidate identifiers must be unique")
        if snapshots:
            problem = snapshots[0].problem
            if any(c.problem != problem for c in snapshots):
                raise ValueError("pipeline batch requires identical problems and comparison conditions")
            if len(snapshots) > problem.evaluation_budget:
                raise ValueError("pipeline batch exceeds problem candidate budget")
        records = tuple(self.evaluate_candidate(c) for c in snapshots)
        best = self.select_best_candidate(records)
        successes = sum(r.evaluation_status == "SUCCESS" for r in records)
        return OptimizationPipelineResult(
            records=records, total_candidates=len(records), evaluated_candidates=len(records),
            successful_candidates=successes, failed_candidates=len(records) - successes,
            best_candidate_id=best.candidate_id if best is not None else None,
            best_objective=best.objective_values[0] if best is not None else None,
        )

    def select_best_candidate(self, records: Iterable[OptimizationEvaluationRecord]) -> OptimizationEvaluationRecord | None:
        snapshots = tuple(OptimizationEvaluationRecord.model_validate(r) for r in records)
        if len({r.candidate_id for r in snapshots}) != len(snapshots):
            raise ValueError("best selection requires unique record identifiers")
        if snapshots and any(r.input_candidate.problem != snapshots[0].input_candidate.problem for r in snapshots):
            raise ValueError("best selection requires one comparable problem")
        return select_best_record(snapshots)
