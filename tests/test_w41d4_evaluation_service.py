import csv
import math
from pathlib import Path

import pytest

from app.models.linkage_evaluation import DesignEvaluationRequest, DesignEvaluationResult
from app.services import linkage_evaluation as service
from app.services.linkage_closure import solve_closure
from app.services.linkage_motion import sweep_rear_link_angles
from app.services.linkage_optimization_adapters import build_closure_task_from_design
from app.models.linkage_motion import MotionSweepInput
from test_w41d4_evaluation_models import parameter, request_payload


def evaluate(data):
    return service.evaluate_design(DesignEvaluationRequest.model_validate(data))


ROWS = list(csv.DictReader((Path(__file__).resolve().parents[1] / "docs/evidence/w39/W39D1_closure_benchmarks.csv").open()))[:6]


@pytest.mark.parametrize("row", ROWS, ids=[r["case_id"] for r in ROWS])
def test_registered_single_states(row):
    data = request_payload(branch=None, lengths=tuple(float(row[n]) for n in ("AB_mm", "BC_mm", "CD_mm")),
                           d=(float(row["D_x_mm"]), float(row["D_y_mm"])))
    data["case"]["case_id"] = row["case_id"]
    data["candidate"]["case"]["case_id"] = row["case_id"]
    result = evaluate(data)
    assert result.closure_result.closure_state == row["expected_closure_state"]
    assert result.feasibility_status == {"TWO_SOLUTIONS": "BRANCH_UNRESOLVED", "TANGENT": "FEASIBLE", "NO_SOLUTION": "INFEASIBLE", "DEGENERATE": "INFEASIBLE"}[row["expected_closure_state"]]
    assert result.objective_status == "OBJECTIVE_NOT_CONFIGURED"
    assert result.objective_value is None and result.motion_result is None


@pytest.mark.parametrize("branch", ["POSITIVE", "NEGATIVE"])
def test_selected_single_preserves_w39(branch):
    request = DesignEvaluationRequest.model_validate(request_payload(branch=branch))
    result = service.evaluate_design(request)
    assert result.feasibility_status == "FEASIBLE"
    assert result.closure_result == solve_closure(build_closure_task_from_design(request.candidate))
    assert result.closure_result.selected_pose.branch == branch
    assert result.request.candidate.configuration.tolerance == request.candidate.configuration.tolerance


@pytest.mark.parametrize("objective", [False, True])
def test_hand_calculable_full_range(objective):
    # D=(3,0), AB=1, BC=CD=3. At 0: Cx=2; at 90: Cx=1.5+sqrt(.65).
    result = evaluate(request_payload([0, 90], lengths=(1, 3, 3), d=(3, 0), objective=objective))
    assert result.feasibility_status == "FEASIBLE"
    assert result.motion_result.termination == "COMPLETED"
    if objective:
        assert result.objective_value == pytest.approx(math.sqrt(.65) - .5)
        assert result.metrics[0].scope == "FULL_REQUESTED_ANGLE_SAMPLES"
        assert result.metrics[0].unit == "mm"
    else:
        assert result.objective_value is None and result.metrics == []


@pytest.mark.parametrize("boundary", ["TANGENT", "NO_SOLUTION", "DEGENERATE"])
@pytest.mark.parametrize("objective", [False, True])
def test_real_motion_boundaries(boundary, objective):
    tangent = math.degrees(math.acos(-11 / 80))
    if boundary == "TANGENT": data = request_payload([0, 30, tangent, 120], objective=objective)
    elif boundary == "NO_SOLUTION": data = request_payload([0, 30, 120, 130], objective=objective)
    else: data = request_payload([0, 10, 20], lengths=(5, 2, 2), d=(5 * math.cos(math.radians(10)), 5 * math.sin(math.radians(10))), objective=objective)
    request = DesignEvaluationRequest.model_validate(data)
    result = service.evaluate_design(request)
    assert result.feasibility_status == "INFEASIBLE"
    assert result.motion_result.termination == boundary + "_BOUNDARY"
    assert result.motion_result.samples[-1].closure_result.closure_state == boundary
    assert result.motion_result.requested_angle_count == len(data["plan"]["angle_samples_deg"])
    expected = sweep_rear_link_angles(MotionSweepInput(reference_task=build_closure_task_from_design(request.candidate), direction=request.plan.direction, angle_samples_deg=request.plan.angle_samples_deg))
    assert result.motion_result == expected
    assert result.objective_value is None and result.metrics == []
    assert result.objective_status == ("NOT_EVALUABLE" if objective else "OBJECTIVE_NOT_CONFIGURED")


def test_tangent_at_last_requested_sample_still_infeasible():
    result = evaluate(request_payload([0, math.degrees(math.acos(-11 / 80))], objective=True))
    assert len(result.motion_result.samples) == result.motion_result.requested_angle_count
    assert result.feasibility_status == "INFEASIBLE" and result.objective_value is None


@pytest.mark.parametrize("lengths,d,state", [((5, 1, 2), (8, 0), "TANGENT"), ((5, 1, 1), (8, 0), "NO_SOLUTION"), ((5, 2, 2), (5, 0), "DEGENERATE")])
def test_first_failure_no_fake_motion(monkeypatch, lengths, d, state):
    def forbidden(*args, **kwargs): raise AssertionError("W40 must not run")
    monkeypatch.setattr(service, "sweep_rear_link_angles", forbidden)
    result = evaluate(request_payload([0, 5], lengths=lengths, d=d, objective=True))
    assert result.closure_result.closure_state == state
    assert result.motion_result is None and result.feasibility_status == "INFEASIBLE"
    assert result.constraints[0].sample_index == 0


def test_engineering_without_geometry_calls_no_solver(monkeypatch):
    def forbidden(*args, **kwargs): raise AssertionError("not ready must not compute")
    for name in ("build_closure_task_from_design", "solve_closure", "sweep_rear_link_angles"):
        monkeypatch.setattr(service, name, forbidden)
    result = evaluate(dict(case=dict(domain="ENGINEERING_REFERENCE", case_id="ER-001", readiness="NOT_SOLVER_READY", source_text="Missing engineering evidence"), objective=None))
    assert result.execution_status == "NOT_RUN"
    assert result.feasibility_status == "NOT_EVALUATED"
    assert result.motion_result is None and result.closure_result is None


@pytest.mark.parametrize("stage", ["solve_closure", "sweep_rear_link_angles"])
@pytest.mark.parametrize("error", [ValueError("numeric classification"), ArithmeticError("capacity"), RuntimeError("service invariant")])
def test_original_exception_propagates(monkeypatch, stage, error):
    def fail(*args, **kwargs): raise error
    monkeypatch.setattr(service, stage, fail)
    with pytest.raises(type(error)) as caught:
        evaluate(request_payload([0, 5]))
    assert caught.value is error


def test_determinism_roundtrip_and_independent_snapshot():
    request = DesignEvaluationRequest.model_validate(request_payload([0, 5, 10], objective=True))
    before = request.model_dump()
    first = service.evaluate_design(request)
    assert first == service.evaluate_design(request)
    assert request.model_dump() == before
    assert DesignEvaluationResult.model_validate_json(first.model_dump_json()) == first
    first.request.candidate.design.rear_link_length_mm.value = 7
    assert request.model_dump() == before


def test_preflight_and_w40_call_counts(monkeypatch):
    from app.services import linkage_motion
    counts = [0, 0]
    original_preflight, original_motion = service.solve_closure, linkage_motion.solve_closure
    def preflight(task): counts[0] += 1; return original_preflight(task)
    def motion(task): counts[1] += 1; return original_motion(task)
    monkeypatch.setattr(service, "solve_closure", preflight)
    monkeypatch.setattr(linkage_motion, "solve_closure", motion)
    evaluate(request_payload([0, 5, 10]))
    assert counts == [1, 3]


def test_mutated_request_revalidated():
    request = DesignEvaluationRequest.model_validate(request_payload())
    request.candidate.design.rear_link_length_mm.value = -1
    with pytest.raises(ValueError): service.evaluate_design(request)



def test_actual_adapter_arithmetic_capacity_exception():
    data = request_payload()
    for name in data["candidate"]["design"]:
        data["candidate"]["design"][name]["value"] = 1e308
        data["candidate"]["bounds"][name]["upper"]["value"] = 1.1e308
    with pytest.raises(ArithmeticError, match="arithmetic capacity"):
        evaluate(data)


def test_decreasing_negative_branch_full_motion():
    data = request_payload([10, 5, 0], branch="NEGATIVE", objective=True)
    data["plan"]["direction"] = "DECREASING"
    result = evaluate(data)
    assert result.feasibility_status == "FEASIBLE"
    assert result.motion_result.direction == "DECREASING"
    assert all(s.closure_result.selected_pose.branch == "NEGATIVE" for s in result.motion_result.samples)


def test_unready_synthetic_without_candidate_does_not_compute(monkeypatch):
    def forbidden(*args, **kwargs): raise AssertionError("must not compute")
    monkeypatch.setattr(service, "build_closure_task_from_design", forbidden)
    result = evaluate(dict(case=dict(domain="SYNTHETIC_MATH", case_id="SM-PENDING", readiness="NOT_SOLVER_READY", source_text="Pending fixture"), objective=None))
    assert result.execution_status == "NOT_RUN" and result.objective_value is None
