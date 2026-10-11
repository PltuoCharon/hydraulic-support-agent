"""W41-D4 synthetic mathematical evaluation contract."""
from math import isfinite
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from app.models.linkage_closure import ClosureResult
from app.models.linkage_geometry import DegreeParameter
from app.models.linkage_motion import MotionDirection, MotionSegmentResult
from app.models.linkage_optimization import (
    CandidateContract, CandidateDesignInput, DesignCase, _parameter,
)


class SinglePosePlan(CandidateContract):
    mode: Literal["SINGLE_POSE_SELECTED"] = "SINGLE_POSE_SELECTED"
    source_text: str = Field(min_length=1)


class AngleSweepPlan(CandidateContract):
    mode: Literal["FULL_SAMPLED_REGULAR_MOTION"] = "FULL_SAMPLED_REGULAR_MOTION"
    direction: MotionDirection
    angle_samples_deg: list[DegreeParameter] = Field(min_length=2)
    source_text: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_angles(self) -> Self:
        for angle in self.angle_samples_deg:
            _parameter(angle)
        values = [angle.value for angle in self.angle_samples_deg]
        for previous, current in zip(values, values[1:]):
            if not (current > previous if self.direction == "INCREASING" else current < previous):
                raise ValueError("angles must be strictly monotonic in the declared direction")
        return self


EvaluationPlan = Annotated[SinglePosePlan | AngleSweepPlan, Field(discriminator="mode")]


class ObjectiveSpec(CandidateContract):
    name: Literal["SAMPLED_C_X_RANGE"]
    direction: Literal["MINIMIZE"] = "MINIMIZE"
    unit: Literal["mm"] = "mm"


class DesignEvaluationRequest(CandidateContract):
    case: DesignCase
    candidate: CandidateDesignInput | None = None
    plan: EvaluationPlan | None = None
    objective: ObjectiveSpec | None  # Explicit null is the default workflow.

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if self.candidate is not None and self.candidate.case != self.case:
            raise ValueError("outer case must match candidate.case")
        if self.case.domain == "SYNTHETIC_MATH" and self.case.readiness == "READY":
            if self.candidate is None or self.plan is None:
                raise ValueError("ready synthetic evaluation requires candidate and plan")
        if self.plan is not None and not self.plan.source_text.strip():
            raise ValueError("plan source must not be blank")
        if self.objective is not None and not isinstance(self.plan, AngleSweepPlan):
            raise ValueError("SAMPLED_C_X_RANGE requires full sampled motion")
        if isinstance(self.plan, AngleSweepPlan) and self.candidate is not None:
            config = self.candidate.configuration
            if config.reference_branch is None:
                raise ValueError("sampled motion requires explicit W39 branch")
            if self.plan.angle_samples_deg[0].value != config.rear_link_angle_deg.value:
                raise ValueError("first angle must equal candidate reference angle")
        return self


class ConstraintOutcome(CandidateContract):
    constraint_id: Literal["SELECTED_POSE", "FULL_REGULAR_SAMPLES"]
    status: Literal["PASS", "FAIL", "NOT_EVALUATED"]
    reason: str = Field(min_length=1)
    sample_index: int | None = Field(default=None, ge=0)


class EvaluationMetric(CandidateContract):
    name: Literal["SAMPLED_C_X_RANGE"]
    unit: Literal["mm"] = "mm"
    scope: Literal["FULL_REQUESTED_ANGLE_SAMPLES"] = "FULL_REQUESTED_ANGLE_SAMPLES"
    value: float = Field(strict=True, ge=0)

    @model_validator(mode="after")
    def finite(self) -> Self:
        if not isfinite(self.value):
            raise ValueError("metric must be finite")
        return self


class DesignEvaluationResult(CandidateContract):
    request: DesignEvaluationRequest  # Domain, case, plan, bounds and provenance snapshot.
    execution_status: Literal["NOT_RUN", "COMPLETED"]
    case_readiness: Literal["READY", "NOT_SOLVER_READY"]
    feasibility_status: Literal["NOT_EVALUATED", "FEASIBLE", "INFEASIBLE", "BRANCH_UNRESOLVED"]
    objective_status: Literal["OBJECTIVE_NOT_CONFIGURED", "COMPUTED", "NOT_EVALUABLE"]
    constraints: list[ConstraintOutcome] = Field(min_length=1, max_length=1)
    closure_result: ClosureResult | None = None  # Single pose or actual first-pose preflight.
    motion_result: MotionSegmentResult | None = None
    objective_value: float | None = Field(default=None, strict=True)
    metrics: list[EvaluationMetric] = Field(default_factory=list, max_length=1)

    @model_validator(mode="after")
    def validate_combinations(self) -> Self:
        request = self.request
        constraint = self.constraints[0]
        sweep = isinstance(request.plan, AngleSweepPlan)
        expected_id = "FULL_REGULAR_SAMPLES" if sweep else "SELECTED_POSE"
        if constraint.constraint_id != expected_id:
            raise ValueError("constraint must match plan")
        ready = request.case.domain == "SYNTHETIC_MATH" and request.case.readiness == "READY"
        if self.case_readiness != request.case.readiness:
            raise ValueError("readiness must match case")
        if not ready:
            if (self.execution_status != "NOT_RUN" or self.feasibility_status != "NOT_EVALUATED"
                    or self.closure_result is not None or self.motion_result is not None
                    or constraint.status != "NOT_EVALUATED" or self.metrics):
                raise ValueError("unready case must not contain evaluated data")
        else:
            if self.execution_status != "COMPLETED" or self.closure_result is None:
                raise ValueError("completed evaluation requires actual closure result")
            closure = self.closure_result
            config = request.candidate.configuration
            if closure.selected_pose is not None:
                pose = closure.selected_pose
                if pose.rear_link_angle_deg != config.rear_link_angle_deg:
                    raise ValueError("closure angle must match candidate configuration")
                if closure.closure_state == "TWO_SOLUTIONS" and pose.branch != config.reference_branch:
                    raise ValueError("closure branch must match candidate configuration")
            if closure.selection_status == "BRANCH_AMBIGUOUS" and config.reference_branch is not None:
                raise ValueError("configured branch must be resolved by W39")
            if self.motion_result is not None:
                if not sweep or closure != self.motion_result.samples[0].closure_result:
                    raise ValueError("motion must agree with first-pose preflight")
                motion = self.motion_result
                config = request.candidate.configuration
                if (motion.requested_angle_count != len(request.plan.angle_samples_deg)
                        or motion.direction != request.plan.direction
                        or motion.reference_branch != config.reference_branch
                        or motion.reference_angle_deg.value != config.rear_link_angle_deg.value
                        or [s.requested_angle_deg for s in motion.samples]
                        != request.plan.angle_samples_deg[:len(motion.samples)]):
                    raise ValueError("motion must match requested plan")
                feasible = motion.termination == "COMPLETED"
                expected = "FEASIBLE" if feasible else "INFEASIBLE"
            elif sweep:
                if closure.closure_state == "TWO_SOLUTIONS" and closure.selection_status == "SELECTED":
                    raise ValueError("regular first pose requires actual sweep result")
                expected = "BRANCH_UNRESOLVED" if closure.selection_status == "BRANCH_AMBIGUOUS" else "INFEASIBLE"
            else:
                expected = ("BRANCH_UNRESOLVED" if closure.selection_status == "BRANCH_AMBIGUOUS"
                            else "FEASIBLE" if closure.selected_pose is not None else "INFEASIBLE")
            if self.feasibility_status != expected or constraint.status != ("PASS" if expected == "FEASIBLE" else "FAIL"):
                raise ValueError("feasibility and constraints must agree with actual results")
        expected_index = None
        if ready and sweep and self.feasibility_status == "INFEASIBLE":
            expected_index = len(self.motion_result.samples) - 1 if self.motion_result else 0
        if constraint.sample_index != expected_index:
            raise ValueError("constraint index must match actual failed sample")
        expected_objective = ("OBJECTIVE_NOT_CONFIGURED" if request.objective is None
                              else "COMPUTED" if ready and self.feasibility_status == "FEASIBLE"
                              else "NOT_EVALUABLE")
        if self.objective_status != expected_objective:
            raise ValueError("objective status inconsistent with request/results")
        if expected_objective == "COMPUTED":
            if self.motion_result is None or len(self.metrics) != 1 or self.objective_value is None:
                raise ValueError("computed objective requires complete motion and metric")
            xs = [s.closure_result.selected_pose.front_link_shield.x_mm.value
                  for s in self.motion_result.samples]
            actual = max(xs) - min(xs)
            if not isfinite(actual) or self.objective_value != actual or self.metrics[0].value != actual:
                raise ValueError("objective must equal full sampled C x range")
        elif self.objective_value is not None or self.metrics:
            raise ValueError("uncomputed objective must be null with no metric")
        return self
