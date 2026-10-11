"""Deterministic W41 evaluation; no search, penalties or exception rewriting."""
from app.models.linkage_evaluation import (
    AngleSweepPlan, ConstraintOutcome, DesignEvaluationRequest,
    DesignEvaluationResult, EvaluationMetric,
)
from app.models.linkage_motion import MotionSweepInput
from app.services.linkage_optimization_adapters import build_closure_task_from_design
from app.services.linkage_closure import solve_closure
from app.services.linkage_motion import sweep_rear_link_angles


def evaluate_design(request: DesignEvaluationRequest) -> DesignEvaluationResult:
    request = DesignEvaluationRequest.model_validate(request.model_dump(mode="python"))
    sweep = isinstance(request.plan, AngleSweepPlan)
    constraint_id = "FULL_REGULAR_SAMPLES" if sweep else "SELECTED_POSE"
    if request.case.domain != "SYNTHETIC_MATH" or request.case.readiness != "READY":
        return DesignEvaluationResult(
            request=request, execution_status="NOT_RUN", case_readiness=request.case.readiness,
            feasibility_status="NOT_EVALUATED",
            objective_status="OBJECTIVE_NOT_CONFIGURED" if request.objective is None else "NOT_EVALUABLE",
            constraints=[ConstraintOutcome(constraint_id=constraint_id, status="NOT_EVALUATED",
                                           reason="Case NOT_SOLVER_READY; no solver called")],
        )
    task = build_closure_task_from_design(request.candidate)
    closure = solve_closure(task)
    motion = None
    sample_index = None
    if sweep and closure.closure_state == "TWO_SOLUTIONS" and closure.selection_status == "SELECTED":
        motion = sweep_rear_link_angles(MotionSweepInput(
            reference_task=task, direction=request.plan.direction,
            angle_samples_deg=request.plan.angle_samples_deg,
        ))
        feasibility = "FEASIBLE" if motion.termination == "COMPLETED" else "INFEASIBLE"
        reason = motion.termination
        if feasibility == "INFEASIBLE":
            sample_index = len(motion.samples) - 1
    elif closure.selection_status == "BRANCH_AMBIGUOUS":
        feasibility, reason = "BRANCH_UNRESOLVED", "W39 branch unresolved"
    elif sweep:
        feasibility, reason, sample_index = "INFEASIBLE", "First pose is not a selected regular double solution", 0
    else:
        feasibility = "FEASIBLE" if closure.selected_pose is not None else "INFEASIBLE"
        reason = closure.closure_state
    objective_value = None
    metrics = []
    objective_status = "OBJECTIVE_NOT_CONFIGURED"
    if request.objective is not None:
        objective_status = "NOT_EVALUABLE"
        if feasibility == "FEASIBLE":
            xs = [s.closure_result.selected_pose.front_link_shield.x_mm.value for s in motion.samples]
            objective_value = max(xs) - min(xs)
            metrics = [EvaluationMetric(name="SAMPLED_C_X_RANGE", unit="mm", value=objective_value)]
            objective_status = "COMPUTED"
    return DesignEvaluationResult(
        request=request, execution_status="COMPLETED", case_readiness=request.case.readiness,
        feasibility_status=feasibility, objective_status=objective_status,
        constraints=[ConstraintOutcome(constraint_id=constraint_id,
                                       status="PASS" if feasibility == "FEASIBLE" else "FAIL",
                                       reason=reason, sample_index=sample_index)],
        closure_result=closure, motion_result=motion,
        objective_value=objective_value, metrics=metrics,
    )
