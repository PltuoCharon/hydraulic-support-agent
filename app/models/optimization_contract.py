"""W42-D2 immutable experiment records; no optimization algorithm or solver."""

from math import isfinite
from typing import Literal, Self

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.models.overall_design import StrictModel
from app.models.linkage_optimization import DESIGN_VARIABLE_ORDER
from app.models.linkage_optimization_evaluation import CandidateEvaluationRecord, ComparisonContract


VariableName = Literal["rear_link_length_mm", "shield_beam_effective_length_mm", "front_link_length_mm"]
ObjectiveName = Literal["SAMPLED_C_X_RANGE"]
Identifier = str


class ExperimentModel(StrictModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")

    @model_validator(mode="before")
    @classmethod
    def explicit_literals(cls, data):
        if isinstance(data, dict):
            # JSON arrays and caller lists become immutable copies, never numeric coercion.
            data = dict(data)
            for name in ("variable_names", "bounds", "objective_names", "objective_units", "constraints",
                         "design_vector", "objective_values", "constraint_violations", "candidates", "objective_vector"):
                if isinstance(data.get(name), list):
                    data[name] = tuple(data[name])
            if "engineering_verified" in data and data["engineering_verified"] is not False:
                raise ValueError("engineering_verified must be literal false")
            if "version" in data and (type(data["version"]) is not int or data["version"] != 1):
                raise ValueError("version must be integer 1")
        return data

    @model_validator(mode="after")
    def finite_and_nonblank(self) -> Self:
        for name in type(self).model_fields:
            value = getattr(self, name)
            if isinstance(value, float) and not isfinite(value):
                raise ValueError("numeric fields must be finite")
            if isinstance(value, str) and not value.strip():
                raise ValueError("text fields must not be blank")
        return self


class VariableBounds(ExperimentModel):
    variable_name: VariableName
    lower: float = Field(gt=0)
    upper: float = Field(gt=0)
    unit: Literal["mm"]
    source: str = Field(min_length=1)

    @model_validator(mode="after")
    def interval(self) -> Self:
        if self.lower >= self.upper:
            raise ValueError("bounds require lower < upper")
        return self


class VariableValue(ExperimentModel):
    variable_name: VariableName
    value: float = Field(gt=0)
    unit: Literal["mm"]
    source: str = Field(min_length=1)


class ObjectiveValue(ExperimentModel):
    objective_name: ObjectiveName
    value: float = Field(ge=0)
    unit: Literal["mm"]
    direction: Literal["MINIMIZE"] = "MINIMIZE"


class ConstraintViolation(ExperimentModel):
    constraint_name: str = Field(min_length=1)
    status: Literal[
        "INVALID_INPUT", "NO_SOLUTION", "DEGENERATE", "OUT_OF_RANGE",
        "FULL_MOTION_INFEASIBLE", "BRANCH_UNRESOLVED", "NUMERICAL_ERROR", "SERVICE_ERROR",
    ]
    violation_value: float | None
    unit: Literal["mm"] | None
    severity: Literal["ERROR"] = "ERROR"
    source: Literal["W41_D5_RECORD", "DECLARED_BOUNDS"]

    @model_validator(mode="after")
    def quantitative_scope(self) -> Self:
        if self.status == "OUT_OF_RANGE":
            if (self.violation_value is None or self.violation_value <= 0 or self.unit != "mm"
                    or self.source != "DECLARED_BOUNDS"):
                raise ValueError("OUT_OF_RANGE requires a positive declared-bound exceedance in mm")
        elif self.violation_value is not None or self.unit is not None or self.source != "W41_D5_RECORD":
            raise ValueError("W41 failures have undefined violation magnitude, never a penalty")
        return self


class OptimizationProblem(ExperimentModel):
    version: Literal[1] = 1
    problem_id: Identifier = Field(pattern=r"^[A-Za-z0-9_.-]{1,128}$")
    case_id: str = Field(min_length=1)
    domain: Literal["SYNTHETIC_MATH", "ENGINEERING_REFERENCE"]
    readiness: Literal["READY", "NOT_SOLVER_READY"]
    variable_names: tuple[VariableName, ...]
    bounds: tuple[VariableBounds, ...]
    objective_names: tuple[ObjectiveName, ...]
    objective_units: tuple[Literal["mm"], ...]
    constraints: tuple[Literal["FULL_REGULAR_SAMPLES"], ...]
    evaluation_budget: int = Field(gt=0)
    # Immutable serialized evidence; accessors return freshly validated models.
    comparison_contract_json: str | None
    engineering_verified: Literal[False] = False

    @field_validator("comparison_contract_json")
    @classmethod
    def canonical_comparison(cls, value):
        return ComparisonContract.model_validate_json(value).model_dump_json() if value is not None else None

    @property
    def comparison_contract(self) -> ComparisonContract | None:
        return (ComparisonContract.model_validate_json(self.comparison_contract_json)
                if self.comparison_contract_json is not None else None)

    @model_validator(mode="after")
    def scope(self) -> Self:
        if self.variable_names != DESIGN_VARIABLE_ORDER:
            raise ValueError("V1 variables are exactly AB/BC/CD in frozen order")
        if self.bounds and tuple(b.variable_name for b in self.bounds) != self.variable_names:
            raise ValueError("bounds must match variable names in order")
        if self.objective_names not in ((), ("SAMPLED_C_X_RANGE",)) or self.objective_units != ("mm",) * len(self.objective_names):
            raise ValueError("V1 supports only the explicit sampled Cx objective in mm")
        if self.constraints not in ((), ("FULL_REGULAR_SAMPLES",)):
            raise ValueError("V1 has only the full regular sampling constraint")
        if self.case_id.startswith("ER-") and self.domain != "ENGINEERING_REFERENCE":
            raise ValueError("ER cases cannot be relabelled as synthetic")
        if self.case_id.startswith("SM-") and self.domain != "SYNTHETIC_MATH":
            raise ValueError("SM cases cannot be relabelled as engineering")
        if self.domain == "ENGINEERING_REFERENCE":
            if self.readiness != "NOT_SOLVER_READY" or self.comparison_contract_json is not None:
                raise ValueError("engineering problems remain descriptive and NOT_SOLVER_READY")
            return self
        if (self.readiness != "READY" or len(self.bounds) != 3
                or self.objective_names != ("SAMPLED_C_X_RANGE",)
                or self.constraints != ("FULL_REGULAR_SAMPLES",)):
            raise ValueError("ready synthetic problems require explicit bounds, objective and constraint")
        comparison = self.comparison_contract
        if comparison is None or comparison.case.case_id != self.case_id or comparison.case.domain != self.domain:
            raise ValueError("problem requires matching W41 comparison conditions")
        for bound in self.bounds:
            actual = getattr(comparison.bounds, bound.variable_name)
            if (bound.lower, bound.upper, bound.unit) != (actual.lower.value, actual.upper.value, actual.lower.unit):
                raise ValueError("problem bounds must equal W41 comparison bounds")
        return self


def _bound_violations(problem, vector):
    if not problem.bounds or vector is None:
        return ()
    violations = []
    for value, bound in zip(vector, problem.bounds):
        excess = max(bound.lower - value.value, value.value - bound.upper, 0.0)
        if excess > 0:
            violations.append(ConstraintViolation(
                constraint_name=value.variable_name, status="OUT_OF_RANGE",
                violation_value=excess, unit="mm", source="DECLARED_BOUNDS",
            ))
    return tuple(violations)


def _record_violations(record):
    if record.ranking_eligible or record.outcome == "NOT_SOLVER_READY":
        return ()
    if record.outcome == "FEASIBLE":
        raise ValueError("feasible but unscored/incompatible W41 record does not fulfill this problem")
    name = (record.result.constraints[0].constraint_id if record.result is not None
            else record.error.stage)
    return (ConstraintViolation(
        constraint_name=name, status=record.outcome, violation_value=None,
        unit=None, source="W41_D5_RECORD",
    ),)


class OptimizationCandidate(ExperimentModel):
    candidate_id: Identifier = Field(pattern=r"^[A-Za-z0-9_.-]{1,128}$")
    problem: OptimizationProblem
    design_vector: tuple[VariableValue, ...] | None
    evaluation_status: Literal["NOT_EVALUATED", "EVALUATED", "FAILED", "NOT_SOLVER_READY"]
    objective_values: tuple[ObjectiveValue, ...] = ()
    constraint_violations: tuple[ConstraintViolation, ...] = ()
    evaluation_record_json: str | None = None

    @field_validator("evaluation_record_json")
    @classmethod
    def canonical_record(cls, value):
        return CandidateEvaluationRecord.model_validate_json(value).model_dump_json() if value is not None else None

    @property
    def evaluation_record(self) -> CandidateEvaluationRecord | None:
        return (CandidateEvaluationRecord.model_validate_json(self.evaluation_record_json)
                if self.evaluation_record_json is not None else None)

    @property
    def ranking_eligible(self) -> bool:
        return self.evaluation_status == "EVALUATED"

    @classmethod
    def from_w41(cls, problem: OptimizationProblem, record: CandidateEvaluationRecord):
        record = CandidateEvaluationRecord.model_validate(record.model_dump(mode="python"))
        candidate = record.request.candidate if record.request is not None else None
        vector = (tuple(VariableValue(
            variable_name=n, value=getattr(candidate.design, n).value,
            unit="mm", source=getattr(candidate.design, n).source_text,
        ) for n in DESIGN_VARIABLE_ORDER) if candidate is not None else None)
        return cls(
            candidate_id=record.candidate_id, problem=problem, design_vector=vector,
            evaluation_status=("EVALUATED" if record.ranking_eligible else
                               "NOT_SOLVER_READY" if record.outcome == "NOT_SOLVER_READY" else "FAILED"),
            objective_values=(tuple(ObjectiveValue(objective_name=m.name, value=m.value, unit=m.unit)
                                    for m in record.result.metrics) if record.ranking_eligible else ()),
            constraint_violations=_record_violations(record), evaluation_record_json=record.model_dump_json(),
        )

    @model_validator(mode="after")
    def evidence(self) -> Self:
        vector = self.design_vector
        if vector is not None and tuple(v.variable_name for v in vector) != self.problem.variable_names:
            raise ValueError("candidate vector must match problem variables in order")
        bound_errors = _bound_violations(self.problem, vector)
        record = self.evaluation_record
        if record is None:
            if self.objective_values:
                raise ValueError("objectives require actual W41 evaluation evidence")
            if self.evaluation_status == "NOT_EVALUATED":
                if vector is None or bound_errors or self.constraint_violations:
                    raise ValueError("pending candidate requires an in-range design and no claimed evaluation")
            elif self.evaluation_status == "FAILED" and bound_errors:
                if self.constraint_violations != bound_errors:
                    raise ValueError("bound violations must equal actual declared-bound exceedances")
            else:
                raise ValueError("evaluated status requires W41 evidence")
            return self
        if record.candidate_id != self.candidate_id or bound_errors:
            raise ValueError("candidate identity and bounds must agree with evidence")
        if self.problem.domain == "SYNTHETIC_MATH":
            if record.comparison_contract != self.problem.comparison_contract:
                raise ValueError("candidate must use the problem comparison contract")
            if record.request is not None and record.comparison_status != "COMPATIBLE":
                raise ValueError("validated candidate conditions must match the problem")
        if record.request is not None:
            if (record.request.case.case_id != self.problem.case_id or record.request.case.domain != self.problem.domain):
                raise ValueError("candidate evidence must match problem case/domain")
            if record.request.candidate is not None:
                actual = tuple(VariableValue(
                    variable_name=n, value=getattr(record.request.candidate.design, n).value,
                    unit="mm", source=getattr(record.request.candidate.design, n).source_text,
                ) for n in DESIGN_VARIABLE_ORDER)
                if vector != actual:
                    raise ValueError("design vector must equal the evaluated design")
            elif vector is not None:
                raise ValueError("no design may be fabricated for evidence without a candidate")
        elif vector is not None:
            raise ValueError("invalid raw input cannot acquire a validated design vector")
        expected_status = ("EVALUATED" if record.ranking_eligible else
                           "NOT_SOLVER_READY" if record.outcome == "NOT_SOLVER_READY" else "FAILED")
        if self.evaluation_status != expected_status or self.constraint_violations != _record_violations(record):
            raise ValueError("candidate state and failures must agree with W41 evidence")
        expected_objectives = (tuple(ObjectiveValue(objective_name=m.name, value=m.value, unit=m.unit)
                                     for m in record.result.metrics) if record.ranking_eligible else ())
        if self.objective_values != expected_objectives:
            raise ValueError("objective vector must equal actual W41 metrics; failure is never zero")
        return self


class OptimizationResult(ExperimentModel):
    problem: OptimizationProblem
    candidates: tuple[OptimizationCandidate, ...]
    best_candidate: OptimizationCandidate | None
    objective_vector: tuple[ObjectiveValue, ...]
    feasible: bool
    total_candidates: int = Field(ge=0)
    failed_candidates: int = Field(ge=0)

    @model_validator(mode="after")
    def best_evidence(self) -> Self:
        candidates = self.candidates
        if any(c.problem != self.problem or c.evaluation_status == "NOT_EVALUATED" for c in candidates):
            raise ValueError("results require completed candidate records for the same problem")
        if len({c.candidate_id for c in candidates}) != len(candidates):
            raise ValueError("result candidate ids must be unique")
        failed = sum(not c.ranking_eligible for c in candidates)
        if (self.total_candidates != len(candidates) or self.total_candidates > self.problem.evaluation_budget
                or self.failed_candidates != failed):
            raise ValueError("counts must agree with candidate records and budget")
        eligible = [c for c in candidates if c.ranking_eligible]
        if not eligible:
            if self.best_candidate is not None or self.objective_vector or self.feasible:
                raise ValueError("no evaluated feasible candidate means no best or objective")
        else:
            best = self.best_candidate
            if best is None or not best.ranking_eligible or best not in candidates:
                raise ValueError("best must be an actual evaluated eligible candidate")
            if (best.objective_values[0].value != min(c.objective_values[0].value for c in eligible)
                    or self.objective_vector != best.objective_values or not self.feasible):
                raise ValueError("best must minimize the recorded comparable objective")
        return self


class OptimizationRun(ExperimentModel):
    run_id: Identifier = Field(pattern=r"^[A-Za-z0-9_.-]{1,128}$")
    problem: OptimizationProblem
    algorithm_name: Literal["MANUAL", "GA", "PSO", "UNSPECIFIED"]
    random_seed: int | None = Field(ge=0)
    budget: int = Field(gt=0)
    candidate_count: int = Field(ge=0)
    status: Literal["NOT_STARTED", "RUNNING", "COMPLETED", "FAILED", "CANCELLED", "NOT_RUN"]
    result: OptimizationResult | None = None

    @model_validator(mode="after")
    def run_consistency(self) -> Self:
        if self.budget > self.problem.evaluation_budget or self.candidate_count > self.budget:
            raise ValueError("run counts must respect declared budgets")
        if self.problem.domain == "ENGINEERING_REFERENCE":
            if self.status != "NOT_RUN" or self.candidate_count != 0 or self.result is not None:
                raise ValueError("engineering run must remain NOT_RUN")
        elif self.status in ("NOT_STARTED", "NOT_RUN") and (self.candidate_count or self.result is not None):
                raise ValueError("unstarted or unexecuted run cannot claim candidates or a result")
        if self.status == "COMPLETED" and self.result is None:
            raise ValueError("completed run requires recorded results")
        if self.result is not None:
            if (self.result.problem != self.problem or self.result.total_candidates != self.candidate_count
                    or self.result.total_candidates > self.budget):
                raise ValueError("run result must agree with problem, counts and budget")
        return self
