"""Independent synthetic geometry oracle; production calls are observations only.

Expected C uses polar angles and the cosine law, not production chord helpers.
Cardinal angles and named boundaries have exact algebraic anchors. All coordinate
and residual bounds are declared here before execution, independently of W39's
distance tolerance. No production result is an input to an expected-value helper.
"""

from copy import deepcopy
from math import acos, atan2, cos, hypot, radians, sin, sqrt

import pytest

from app.models.linkage_evaluation import DesignEvaluationRequest
from app.models.linkage_motion import MotionSweepInput
from app.models.linkage_optimization_evaluation import ComparisonContract
from app.services.linkage_closure import solve_closure
from app.services.linkage_evaluation import evaluate_design
from app.services.linkage_motion import sweep_rear_link_angles
from app.services.linkage_optimization_adapters import build_closure_task_from_design
from app.services.linkage_optimization_evaluation import (
    assert_comparison_compatible, evaluate_candidates,
)
from test_w41d4_evaluation_models import parameter, request_payload


def oracle_b(ab, angle):
    cardinal = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}
    if angle % 360 in cardinal:
        x, y = cardinal[angle % 360]
        return ab * x, ab * y
    return ab * cos(radians(angle)), ab * sin(radians(angle))


def oracle_geometry(lengths, d, angle):
    """Return ideal classification and branch coordinates using input only.

    Normalize before squared arithmetic; no production numerical tolerance is
    used. Exact tangencies below use cardinal angles and exact length relations.
    """
    ab, bc, cd = lengths
    b = oracle_b(ab, angle)
    vx, vy = d[0] - b[0], d[1] - b[1]
    q = hypot(vx, vy)
    if q == 0:
        return b, "DEGENERATE" if bc == cd else "NO_SOLUTION", {}
    if q > bc + cd or q < abs(bc - cd):
        return b, "NO_SOLUTION", {}
    phi = atan2(vy, vx)
    if q == bc + cd or q == abs(bc - cd):
        # Collinear solution from the signed distance along B->D.
        along = bc if q == bc + cd or bc > cd else -bc
        c = (b[0] + along * vx / q, b[1] + along * vy / q)
        return b, "TANGENT", {"TANGENT": c}
    scale = max(q, bc, cd)
    qn, rn, tn = q / scale, bc / scale, cd / scale
    alpha = acos((rn * rn + qn * qn - tn * tn) / (2 * rn * qn))
    candidates = {}
    for branch, sign in (("POSITIVE", 1), ("NEGATIVE", -1)):
        beta = phi + sign * alpha
        candidates[branch] = (b[0] + bc * cos(beta), b[1] + bc * sin(beta))
    return b, "TWO_SOLUTIONS", candidates


def explicit_anchor(angle, branch):
    sign = 1 if branch == "POSITIVE" else -1
    if angle == 0:
        return (1, 0), (2, sign * sqrt(8))
    assert angle == 90
    return (0, 1), (1.5 + sign * sqrt(.65), .5 + sign * 3 * sqrt(.65))


def point_values(point):
    return point.x_mm.value, point.y_mm.value


def assert_coordinates(actual, expected, lengths):
    # Tight floating-point bound scaled to geometry, not the solver's tolerance.
    scale = max(lengths)
    for value, target in zip(actual, expected):
        assert value == pytest.approx(target, rel=2e-13, abs=2e-14 * scale)


def residuals(b, c, d, lengths):
    ab, bc, cd = lengths
    return hypot(*b) - ab, hypot(c[0] - b[0], c[1] - b[1]) - bc, hypot(c[0] - d[0], c[1] - d[1]) - cd


def assert_pose(closure, lengths, d, angle, branch):
    b, state, candidates = oracle_geometry(lengths, d, angle)
    assert state in ("TWO_SOLUTIONS", "TANGENT")
    assert closure.closure_state == state
    expected_c = candidates[branch if state == "TWO_SOLUTIONS" else "TANGENT"]
    actual_b = point_values(closure.rear_link_shield)
    actual_c = point_values(closure.selected_pose.front_link_shield)
    assert_coordinates(actual_b, b, lengths)
    assert_coordinates(actual_c, expected_c, lengths)
    errors = residuals(actual_b, actual_c, d, lengths)
    assert max(map(abs, errors)) <= 3e-13 * max(lengths)
    cross = (d[0] - actual_b[0]) * (actual_c[1] - actual_b[1]) - (d[1] - actual_b[1]) * (actual_c[0] - actual_b[0])
    if state == "TWO_SOLUTIONS":
        assert cross > 0 if branch == "POSITIVE" else cross < 0
    return max(map(abs, errors))


def make_request(angles=None, *, lengths=(1, 3, 3), d=(3, 0), branch="POSITIVE", objective=False):
    payload = request_payload(angles, lengths=lengths, d=d, branch=branch, objective=objective)
    if angles is not None and angles[-1] < angles[0]:
        payload["plan"]["direction"] = "DECREASING"
    return DesignEvaluationRequest.model_validate(payload)


def observed_pipeline(request):
    """Run all three layers as observations; none supplies an oracle answer."""
    task = build_closure_task_from_design(request.candidate)
    raw_closure = solve_closure(task)
    evaluation = evaluate_design(request)
    comparison = ComparisonContract.from_request(request) if request.objective else None
    record = evaluate_candidates([("oracle", request)], comparison)[0]
    assert record.error is None
    assert record.source_assessment == "NOT_INDEPENDENTLY_VERIFIED"
    assert not record.request.case.engineering_verified
    assert record.result.closure_result.provenance.evidence_status == "PARTIAL"
    return raw_closure, evaluation, record


@pytest.mark.parametrize("angle", [0, 90])
@pytest.mark.parametrize("branch", ["POSITIVE", "NEGATIVE"])
def test_oracle_has_independent_explicit_coordinate_anchors(angle, branch):
    b, state, candidates = oracle_geometry((1, 3, 3), (3, 0), angle)
    expected_b, expected_c = explicit_anchor(angle, branch)
    assert state == "TWO_SOLUTIONS"
    assert_coordinates(b, expected_b, (1, 3, 3))
    assert_coordinates(candidates[branch], expected_c, (1, 3, 3))
    assert max(map(abs, residuals(b, candidates[branch], (3, 0), (1, 3, 3)))) <= 9e-13


@pytest.mark.parametrize("angle", [0, 90])
@pytest.mark.parametrize("branch", ["POSITIVE", "NEGATIVE"])
def test_single_pose_d3_w39_d4_d5_matches_explicit_oracle(angle, branch):
    request = make_request(branch=branch)
    payload = request.model_dump()
    payload["candidate"]["configuration"]["rear_link_angle_deg"] = parameter(angle, "degree")
    request = DesignEvaluationRequest.model_validate(payload)
    assert request.candidate.design.as_vector() == (1, 3, 3)
    task = build_closure_task_from_design(request.candidate)
    assert task.base_pivot_spacing_mm.value == 3
    raw, evaluation, record = observed_pipeline(request)
    b, c = explicit_anchor(angle, branch)
    for closure in (raw, evaluation.closure_result, record.result.closure_result):
        assert_pose(closure, (1, 3, 3), (3, 0), angle, branch)
        assert_coordinates(point_values(closure.rear_link_shield), b, (1, 3, 3))
        assert_coordinates(point_values(closure.selected_pose.front_link_shield), c, (1, 3, 3))
    assert evaluation.feasibility_status == record.outcome == "FEASIBLE"
    assert not record.ranking_eligible and not record.objective_computed


@pytest.mark.parametrize("angles", [[0, 45, 90], [90, 45, 0]])
@pytest.mark.parametrize("branch", ["POSITIVE", "NEGATIVE"])
def test_increasing_and_decreasing_motion_coordinates_and_objective(angles, branch):
    request = make_request(angles, branch=branch, objective=True)
    expected_x = [oracle_geometry((1, 3, 3), (3, 0), a)[2][branch][0] for a in angles]
    expected_objective = max(expected_x) - min(expected_x)
    task = build_closure_task_from_design(request.candidate)
    direct_motion = sweep_rear_link_angles(MotionSweepInput(
        reference_task=task, direction=request.plan.direction, angle_samples_deg=request.plan.angle_samples_deg,
    ))
    _, evaluation, record = observed_pipeline(request)
    for motion in (direct_motion, evaluation.motion_result, record.result.motion_result):
        assert motion.termination == "COMPLETED"
        assert len(motion.samples) == len(angles)
        for sample, angle in zip(motion.samples, angles):
            assert_pose(sample.closure_result, (1, 3, 3), (3, 0), angle, branch)
    for result in (evaluation, record.result):
        assert result.objective_value == pytest.approx(expected_objective, rel=2e-13, abs=1e-14)
    assert record.ranking_eligible and record.coverage.recorded_ratio == 1


@pytest.mark.parametrize("branch,angles,expected", [
    ("POSITIVE", [0, 90], sqrt(.65) - .5),
    ("NEGATIVE", [90, 0], sqrt(.65) + .5),
])
def test_two_angle_objective_has_closed_form_anchor(branch, angles, expected):
    _, evaluation, record = observed_pipeline(make_request(angles, branch=branch, objective=True))
    assert evaluation.objective_value == pytest.approx(expected, rel=2e-13, abs=1e-14)
    assert record.result.objective_value == pytest.approx(expected, rel=2e-13, abs=1e-14)
    for sample, angle in zip(record.result.motion_result.samples, angles):
        b, c = explicit_anchor(angle, branch)
        assert_coordinates(point_values(sample.closure_result.rear_link_shield), b, (1, 3, 3))
        assert_coordinates(point_values(sample.closure_result.selected_pose.front_link_shield), c, (1, 3, 3))


EXACT_BOUNDARIES = [
    ((1, 1, 1), (3, 0), "TANGENT", (2, 0)),
    ((1, 3, 1), (3, 0), "TANGENT", (4, 0)),
    ((1, .5, .5), (3, 0), "NO_SOLUTION", None),
    ((1, 4, 1), (3, 0), "NO_SOLUTION", None),
    ((1, 3, 3), (1, 0), "DEGENERATE", None),
    ((1, 3, 2), (1, 0), "NO_SOLUTION", None),
]


@pytest.mark.parametrize("lengths,d,state,c", EXACT_BOUNDARIES)
def test_exact_tangency_no_solution_and_coincident_centers(lengths, d, state, c):
    b, independent_state, candidates = oracle_geometry(lengths, d, 0)
    assert independent_state == state and b == (1, 0)
    if c is not None:
        assert candidates["TANGENT"] == c
    raw, evaluation, record = observed_pipeline(make_request(lengths=lengths, d=d))
    for closure in (raw, evaluation.closure_result, record.result.closure_result):
        assert closure.closure_state == state
        if c is not None:
            assert_pose(closure, lengths, d, 0, "TANGENT")
            assert_coordinates(point_values(closure.selected_pose.front_link_shield), c, lengths)
        else:
            assert closure.selected_pose is None and closure.candidates == []
    assert record.outcome == ("FEASIBLE" if state == "TANGENT" else state)
    assert record.result.objective_value is None and record.result.metrics == []
    assert record.constraint_violation_status == "UNDEFINED" and record.constraint_violation_value is None


@pytest.mark.parametrize("boundary,lengths,d,angles", [
    ("TANGENT", (1, 2, 2), (3, 0), [0, 90, 180]),
    ("NO_SOLUTION", (1, 1.5, 1.5), (3, 0), [0, 30, 90]),
    ("DEGENERATE", (1, 1, 1), (0, 1), [0, 45, 90]),
])
@pytest.mark.parametrize("middle", [False, True], ids=["last_sample", "middle_sample"])
def test_full_motion_boundary_has_independent_classification_and_no_prefix_score(boundary, lengths, d, angles, middle):
    requested = [*angles, angles[-1] + 45] if middle else angles
    states = [oracle_geometry(lengths, d, a)[1] for a in angles]
    assert states == ["TWO_SOLUTIONS", "TWO_SOLUTIONS", boundary]
    request = make_request(requested, lengths=lengths, d=d, objective=True)
    _, evaluation, record = observed_pipeline(request)
    direct = sweep_rear_link_angles(MotionSweepInput(
        reference_task=build_closure_task_from_design(request.candidate),
        direction=request.plan.direction, angle_samples_deg=request.plan.angle_samples_deg,
    ))
    for motion in (direct, evaluation.motion_result, record.result.motion_result):
        assert motion.termination == boundary + "_BOUNDARY"
        assert len(motion.samples) == 3 and motion.requested_angle_count == len(requested)
        assert [s.closure_result.closure_state for s in motion.samples] == states
        for sample, angle in zip(motion.samples[:2], angles[:2]):
            assert_pose(sample.closure_result, lengths, d, angle, "POSITIVE")
        if boundary == "TANGENT":
            assert_pose(motion.samples[-1].closure_result, lengths, d, 180, "TANGENT")
    assert evaluation.feasibility_status == "INFEASIBLE"
    assert record.outcome == ("FULL_MOTION_INFEASIBLE" if boundary == "TANGENT" else boundary)
    assert record.full_motion_infeasible and record.error is None
    assert record.coverage.recorded_count == 3 and record.coverage.regular_selected_count == 2
    assert record.coverage.recorded_ratio == 3 / len(requested)
    assert record.result.constraints[0].sample_index == 2
    for result in (evaluation, record.result):
        assert result.objective_status == "NOT_EVALUABLE"
        assert result.objective_value is None and result.metrics == []
    assert not record.ranking_eligible and record.constraint_violation_value is None


@pytest.mark.parametrize("scale,numerical_state", [(1, "TWO_SOLUTIONS"), (1e-8, "TWO_SOLUTIONS"), (1e-10, "DEGENERATE")])
@pytest.mark.parametrize("branch", ["POSITIVE", "NEGATIVE"])
def test_fixed_tolerance_scale_matrix_records_math_and_numerical_classification(scale, numerical_state, branch):
    lengths, d = (scale, 3 * scale, 3 * scale), (3 * scale, 0)
    _, ideal_state, coordinates = oracle_geometry(lengths, d, 0)
    assert ideal_state == "TWO_SOLUTIONS"
    assert_coordinates(coordinates[branch], (2 * scale, (1 if branch == "POSITIVE" else -1) * sqrt(8) * scale), lengths)
    request = make_request(lengths=lengths, d=d, branch=branch)
    assert request.candidate.configuration.tolerance.absolute_mm == 1e-9
    assert request.candidate.configuration.tolerance.relative == 1e-12
    # Independent contract arithmetic: W39's distance scale includes BC+CD=6s.
    distance_tolerance = max(1e-9, 1e-12 * 6 * scale)
    q = 2 * scale
    assert (q <= distance_tolerance) == (numerical_state == "DEGENERATE")
    raw, evaluation, record = observed_pipeline(request)
    for closure in (raw, evaluation.closure_result, record.result.closure_result):
        assert closure.closure_state == numerical_state
        assert_coordinates(point_values(closure.rear_link_shield), (scale, 0), lengths)
    if numerical_state == "TWO_SOLUTIONS":
        error = assert_pose(record.result.closure_result, lengths, d, 0, branch)
        assert record.outcome == "FEASIBLE"
        verdict = "PASS"
    else:
        error = None
        assert record.outcome == "DEGENERATE" and record.result.closure_result.selected_pose is None
        verdict = "LIMITATION"
    print(f"SCALE s={scale:g} branch={branch} ideal={ideal_state} numerical={raw.closure_state} "
          f"tau_mm={distance_tolerance:.17g} max_residual_mm={error} verdict={verdict}")


def test_extremely_small_positive_lengths_validate_without_resolution_guarantee():
    scale = 1e-100
    payload = request_payload(lengths=(scale, 3 * scale, 3 * scale), d=(3 * scale, 0))
    for bounds in payload["candidate"]["bounds"].values():
        if isinstance(bounds, dict):
            bounds["lower"] = parameter(scale / 100)
    request = DesignEvaluationRequest.model_validate(payload)
    assert all(v > 0 for v in request.candidate.design.as_vector())
    assert oracle_geometry((scale, 3 * scale, 3 * scale), (3 * scale, 0), 0)[1] == "TWO_SOLUTIONS"
    raw, evaluation, record = observed_pipeline(request)
    assert raw.closure_state == evaluation.closure_result.closure_state == "DEGENERATE"
    assert record.outcome == "DEGENERATE" and record.result.objective_value is None


def test_small_scale_sweep_cannot_promote_degenerate_preflight_to_full_objective():
    scale = 1e-10
    request = make_request([0, 90], lengths=(scale, 3 * scale, 3 * scale), d=(3 * scale, 0), objective=True)
    assert all(oracle_geometry((scale, 3 * scale, 3 * scale), (3 * scale, 0), a)[1] == "TWO_SOLUTIONS" for a in [0, 90])
    _, evaluation, record = observed_pipeline(request)
    assert evaluation.closure_result.closure_state == "DEGENERATE" and evaluation.motion_result is None
    assert record.coverage.recorded_count == 1 and record.coverage.recorded_ratio == .5
    assert record.result.objective_value is None and not record.ranking_eligible


@pytest.mark.parametrize("change", ["angles", "branch", "tolerance", "fixed_geometry"])
def test_independent_valid_results_with_incompatible_conditions_cannot_rank(change):
    baseline = make_request([0, 90], objective=True)
    payload = baseline.model_dump()
    lengths, d, angles, branch = (1, 3, 3), (3, 0), [0, 90], "POSITIVE"
    if change == "angles":
        angles = [0, 45]
        payload["plan"]["angle_samples_deg"][1] = parameter(45, "degree")
    elif change == "branch":
        branch = "NEGATIVE"
        payload["candidate"]["configuration"]["reference_branch"] = branch
    elif change == "tolerance": payload["candidate"]["configuration"]["tolerance"]["relative"] = 1e-11
    else:
        d = (4, 0)
        payload["candidate"]["configuration"]["front_link_base"]["x_mm"] = parameter(4)
    actual = evaluate_candidates([("different", payload)], ComparisonContract.from_request(baseline))[0]
    assert actual.result.feasibility_status == "FEASIBLE" and actual.objective_computed
    for sample, angle in zip(actual.result.motion_result.samples, angles):
        assert_pose(sample.closure_result, lengths, d, angle, branch)
    expected_x = [oracle_geometry(lengths, d, a)[2][branch][0] for a in angles]
    assert actual.result.objective_value == pytest.approx(max(expected_x) - min(expected_x), rel=2e-13, abs=1e-14)
    assert actual.comparison_status == "INCOMPATIBLE" and not actual.ranking_eligible
    with pytest.raises(ValueError): assert_comparison_compatible([actual])


def test_batch_independence_determinism_and_request_immutability_with_oracle():
    requests = [make_request([0, 90], objective=True), make_request([0, 90], lengths=(1, 2, 3), objective=True)]
    before = [r.model_dump() for r in requests]
    comparison = ComparisonContract.from_request(requests[0])
    contract_before = comparison.model_dump()
    items = [("first", requests[0]), ("second", requests[1])]
    first, second = evaluate_candidates(items, comparison), evaluate_candidates(items, comparison)
    assert first == second
    assert [r.model_dump() for r in requests] == before
    assert comparison.model_dump() == contract_before
    for record, lengths in zip(first, [(1, 3, 3), (1, 2, 3)]):
        assert record.ranking_eligible
        for sample, angle in zip(record.result.motion_result.samples, [0, 90]):
            assert_pose(sample.closure_result, lengths, (3, 0), angle, "POSITIVE")
        xs = [oracle_geometry(lengths, (3, 0), a)[2]["POSITIVE"][0] for a in [0, 90]]
        assert record.result.objective_value == pytest.approx(max(xs) - min(xs), rel=2e-13, abs=1e-14)
    assert_comparison_compatible(first)
    saved_second = deepcopy(first[1].model_dump())
    first[0].request.candidate.design.rear_link_length_mm.value = 7
    first[0].result.motion_result.samples[0].closure_result.selected_pose.front_link_shield.x_mm.value = 99
    assert first[1].model_dump() == saved_second
    assert [r.model_dump() for r in requests] == before and comparison.model_dump() == contract_before


def test_complete_motion_without_objective_has_no_automatic_score():
    _, evaluation, record = observed_pipeline(make_request([0, 90]))
    for sample, angle in zip(evaluation.motion_result.samples, [0, 90]):
        assert_pose(sample.closure_result, (1, 3, 3), (3, 0), angle, "POSITIVE")
    assert evaluation.feasibility_status == "FEASIBLE" and evaluation.objective_status == "OBJECTIVE_NOT_CONFIGURED"
    assert record.result.objective_value is None and record.result.metrics == []
    assert not record.objective_computed and not record.ranking_eligible


def test_unresolved_branch_retains_both_independent_mathematical_candidates():
    request = make_request(branch=None)
    b, ideal, candidates = oracle_geometry((1, 3, 3), (3, 0), 0)
    assert ideal == "TWO_SOLUTIONS"
    raw, evaluation, record = observed_pipeline(request)
    for closure in (raw, evaluation.closure_result, record.result.closure_result):
        assert closure.closure_state == "TWO_SOLUTIONS" and closure.selection_status == "BRANCH_AMBIGUOUS"
        assert closure.selected_pose is None
        assert_coordinates(point_values(closure.rear_link_shield), b, (1, 3, 3))
        assert len(closure.candidates) == 2
        for candidate in closure.candidates:
            c = point_values(candidate.point_c)
            assert_coordinates(c, candidates[candidate.branch], (1, 3, 3))
            assert max(map(abs, residuals(b, c, (3, 0), (1, 3, 3)))) <= 9e-13
    assert evaluation.feasibility_status == record.outcome == "BRANCH_UNRESOLVED"
    assert record.result.objective_value is None and not record.ranking_eligible


def test_unready_engineering_and_timeout_are_not_verified_capabilities():
    raw = dict(case=dict(domain="ENGINEERING_REFERENCE", case_id="ER-001", readiness="NOT_SOLVER_READY",
                         source_text="No independent engineering geometry"), objective=None)
    record = evaluate_candidates([("engineering", raw)])[0]
    assert record.outcome == "NOT_SOLVER_READY"
    assert record.result.closure_result is None and record.result.motion_result is None
    assert record.result.objective_value is None and not record.ranking_eligible
    assert not record.request.case.engineering_verified
    assert record.source_assessment == "NOT_INDEPENDENTLY_VERIFIED"
    assert record.timeout.status == "NOT_IMPLEMENTED" and not record.timeout.can_interrupt
