"""W41-D5 peripheral records; no solver, penalty or timeout execution."""

from math import isfinite
from typing import Literal, Self

from pydantic import Field, model_validator

from app.models.linkage_evaluation import (
    AngleSweepPlan, DesignEvaluationRequest, DesignEvaluationResult, ObjectiveSpec,
)
from app.models.linkage_optimization import (
    CandidateContract, DesignCase, DesignVariableBounds, FixedEvaluationConfig,
)
from app.models.overall_design import StrictModel


# TIMEOUT is reserved in the vocabulary, but forbidden in executable records.
FailureCode = Literal[
    "NO_SOLUTION", "DEGENERATE", "INVALID_INPUT", "NUMERICAL_ERROR",
    "SERVICE_ERROR", "TIMEOUT",
]
CandidateOutcome = Literal[
    "FEASIBLE", "NO_SOLUTION", "DEGENERATE", "INVALID_INPUT",
    "NUMERICAL_ERROR", "SERVICE_ERROR", "TIMEOUT", "BRANCH_UNRESOLVED",
    "NOT_SOLVER_READY", "FULL_MOTION_INFEASIBLE",
]
ComparisonStatus = Literal["NOT_CONFIGURED", "COMPATIBLE", "INCOMPATIBLE"]


class TimeoutCapability(StrictModel):
    status: Literal["NOT_IMPLEMENTED"] = "NOT_IMPLEMENTED"
    can_interrupt: Literal[False] = False


class InputTrace(StrictModel):
    """Digest of supported input; raw invalid data and secrets are not persisted."""

    representation: Literal["TYPED_REQUEST", "MAPPING", "JSON_TEXT", "UNSUPPORTED"]
    sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


class EvaluationError(StrictModel):
    code: Literal["INVALID_INPUT", "NUMERICAL_ERROR", "SERVICE_ERROR"]
    stage: Literal["INPUT_VALIDATION", "EVALUATOR_EXECUTION"]
    exception_type: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$", max_length=100)
    diagnostic: Literal[
        "INPUT_VALIDATION_FAILED", "ARITHMETIC_EXCEPTION_DURING_EVALUATION",
        "INTERNAL_EVALUATION_EXCEPTION",
    ]

    @model_validator(mode="after")
    def validate_classification(self) -> Self:
        expected = {
            "INVALID_INPUT": ("INPUT_VALIDATION", "INPUT_VALIDATION_FAILED"),
            "NUMERICAL_ERROR": (
                "EVALUATOR_EXECUTION", "ARITHMETIC_EXCEPTION_DURING_EVALUATION",
            ),
            "SERVICE_ERROR": ("EVALUATOR_EXECUTION", "INTERNAL_EVALUATION_EXCEPTION"),
        }
        if (self.stage, self.diagnostic) != expected[self.code]:
            raise ValueError("error classification must agree with execution stage")
        return self


class ComparisonContract(CandidateContract):
    """Exact declared conditions, including provenance; AB/BC/CD are excluded."""

    case: DesignCase
    objective: ObjectiveSpec
    plan: AngleSweepPlan
    configuration: FixedEvaluationConfig
    bounds: DesignVariableBounds

    @model_validator(mode="after")
    def validate_conditions(self) -> Self:
        if self.case.domain != "SYNTHETIC_MATH" or self.case.readiness != "READY":
            raise ValueError("comparison requires a ready synthetic case")
        if self.bounds.domain != self.case.domain:
            raise ValueError("comparison bounds domain must match case")
        if self.configuration.reference_branch is None:
            raise ValueError("comparison requires explicit branch")
        if not self.plan.source_text.strip():
            raise ValueError("comparison plan source must not be blank")
        if self.plan.angle_samples_deg[0].value != self.configuration.rear_link_angle_deg.value:
            raise ValueError("comparison first angle must match reference angle")
        return self

    @classmethod
    def from_request(cls, request: DesignEvaluationRequest) -> "ComparisonContract":
        request = DesignEvaluationRequest.model_validate(request.model_dump(mode="python"))
        if request.candidate is None or request.objective is None or not isinstance(request.plan, AngleSweepPlan):
            raise ValueError("comparison requires candidate, objective and angle plan")
        return cls.model_validate(dict(
            case=request.case.model_dump(), objective=request.objective.model_dump(),
            plan=request.plan.model_dump(),
            configuration=request.candidate.configuration.model_dump(),
            bounds=request.candidate.bounds.model_dump(),
        ))


def comparison_status(
    request: DesignEvaluationRequest | None, contract: ComparisonContract | None,
) -> ComparisonStatus:
    if contract is None:
        return "NOT_CONFIGURED"
    if request is None:
        return "INCOMPATIBLE"
    try:
        actual = ComparisonContract.from_request(request)
    except ValueError:
        return "INCOMPATIBLE"
    return "COMPATIBLE" if actual == contract else "INCOMPATIBLE"


class SamplingCoverage(StrictModel):
    """Recorded discrete attempts, never continuous-domain coverage."""

    requested_count: int | None = Field(default=None, strict=True, gt=0)
    recorded_count: int | None = Field(default=None, strict=True, ge=0)
    regular_selected_count: int | None = Field(default=None, strict=True, ge=0)
    recorded_ratio: float | None = Field(default=None, strict=True, ge=0, le=1)
    scope: Literal["DISCRETE_REQUESTED_SAMPLES"] = "DISCRETE_REQUESTED_SAMPLES"

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        if (self.recorded_count is None) != (self.regular_selected_count is None):
            raise ValueError("recorded and regular counts must both be known or unknown")
        if self.recorded_count is not None:
            if self.regular_selected_count > self.recorded_count:
                raise ValueError("regular count cannot exceed recorded count")
            if self.requested_count is not None and self.recorded_count > self.requested_count:
                raise ValueError("recorded count cannot exceed requested count")
        expected = (self.recorded_count / self.requested_count
                    if self.recorded_count is not None and self.requested_count is not None else None)
        if self.recorded_ratio != expected:
            raise ValueError("recorded ratio must agree with known counts")
        return self


def sampling_coverage(
    request: DesignEvaluationRequest | None, result: DesignEvaluationResult | None,
) -> SamplingCoverage:
    requested = None
    if request is not None:
        if isinstance(request.plan, AngleSweepPlan):
            requested = len(request.plan.angle_samples_deg)
        elif request.plan is not None:
            requested = 1
    if result is None:
        return SamplingCoverage(requested_count=requested)
    if result.execution_status == "NOT_RUN":
        recorded, regular = 0, 0
    else:
        closures = ([s.closure_result for s in result.motion_result.samples]
                    if result.motion_result is not None else [result.closure_result])
        recorded = len(closures)  # First-pose preflight is one real attempt.
        regular = sum(c.closure_state == "TWO_SOLUTIONS" and c.selection_status == "SELECTED"
                      and c.selected_pose is not None for c in closures)
    return SamplingCoverage(
        requested_count=requested, recorded_count=recorded,
        regular_selected_count=regular,
        recorded_ratio=recorded / requested if requested is not None else None,
    )


def mathematical_outcome(result: DesignEvaluationResult) -> CandidateOutcome:
    if result.execution_status == "NOT_RUN":
        return "NOT_SOLVER_READY"
    if result.feasibility_status == "BRANCH_UNRESOLVED":
        return "BRANCH_UNRESOLVED"
    if result.feasibility_status == "FEASIBLE":
        return "FEASIBLE"
    final = (result.motion_result.samples[-1].closure_result
             if result.motion_result is not None else result.closure_result)
    if final.closure_state in ("NO_SOLUTION", "DEGENERATE"):
        return final.closure_state
    return "FULL_MOTION_INFEASIBLE"


class CandidateEvaluationRecord(CandidateContract):
    candidate_id: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,128}$")
    input_trace: InputTrace
    request: DesignEvaluationRequest | None = None
    result: DesignEvaluationResult | None = None
    error: EvaluationError | None = None
    outcome: CandidateOutcome
    full_motion_infeasible: bool = Field(strict=True)
    objective_computed: bool = Field(strict=True)
    comparison_contract: ComparisonContract | None = None
    comparison_status: ComparisonStatus
    ranking_eligible: bool = Field(strict=True)
    coverage: SamplingCoverage
    constraint_violation_status: Literal["UNDEFINED"] = "UNDEFINED"
    constraint_violation_value: None = None
    source_assessment: Literal["NOT_INDEPENDENTLY_VERIFIED"] = "NOT_INDEPENDENTLY_VERIFIED"
    timeout: TimeoutCapability = Field(default_factory=TimeoutCapability)

    @model_validator(mode="after")
    def validate_record(self) -> Self:
        if (self.result is None) == (self.error is None):
            raise ValueError("record requires exactly one actual result or error")
        if self.result is not None:
            if self.request is None or self.request != self.result.request:
                raise ValueError("request snapshot must agree with actual result")
            expected_outcome = mathematical_outcome(self.result)
        else:
            expected_outcome = self.error.code
            if (self.error.stage == "INPUT_VALIDATION") != (self.request is None):
                raise ValueError("only independently validated input may have a request snapshot")
        if self.outcome != expected_outcome:
            raise ValueError("outcome must agree with actual result or error; TIMEOUT is not implemented")
        full_failure = (self.result is not None and isinstance(self.request.plan, AngleSweepPlan)
                        and self.result.feasibility_status == "INFEASIBLE")
        computed = self.result is not None and self.result.objective_status == "COMPUTED"
        compared = comparison_status(self.request, self.comparison_contract)
        eligible = (computed and self.result.feasibility_status == "FEASIBLE"
                    and self.result.objective_value is not None
                    and isfinite(self.result.objective_value) and compared == "COMPATIBLE")
        if (self.full_motion_infeasible, self.objective_computed, self.comparison_status,
                self.ranking_eligible) != (full_failure, computed, compared, eligible):
            raise ValueError("derived flags must agree with actual evaluation and comparison contract")
        if self.coverage != sampling_coverage(self.request, self.result):
            raise ValueError("coverage must agree with actual recorded results")
        return self
