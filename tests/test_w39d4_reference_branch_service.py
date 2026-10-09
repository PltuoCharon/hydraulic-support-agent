import math

import pytest

import app.services.linkage_closure as closure_service

from app.models.linkage_closure import (
    ClosureResult,
    ClosureSelectedPose,
    ClosureSolverInput,
    ClosureSolverProvenance,
    NumericalTolerance,
)
from app.models.linkage_geometry import (
    DegreeParameter,
    EngineeringPoint2D,
    MillimetreParameter,
)
from app.services.linkage_closure import (
    derive_reference_branch,
    resolve_reference_branch,
    solve_closure,
    solve_closure_candidates,
)


def mm(
    value,
    *,
    origin="USER_INPUT",
    evidence_status="EVIDENCE_GAP",
):
    return MillimetreParameter(
        value=value,
        origin=origin,
        evidence_status=evidence_status,
    )


def deg(value):
    return DegreeParameter(
        value=value,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
    )


def point(
    x,
    y,
    *,
    role=None,
):
    return EngineeringPoint2D(
        x_mm=mm(x),
        y_mm=mm(y),
        point_role=role,
    )


def tolerance():
    return NumericalTolerance(
        absolute_mm=1e-9,
        relative=1e-12,
    )


def task(
    *,
    reference_branch=None,
):
    return ClosureSolverInput(
        front_link_base=point(
            8,
            0,
            role="front_link_base",
        ),
        rear_link_length_mm=mm(5),
        shield_beam_effective_length_mm=mm(5),
        front_link_length_mm=mm(5),
        base_pivot_spacing_mm=mm(8),
        rear_link_angle_deg=deg(0),
        reference_branch=reference_branch,
        tolerance=tolerance(),
    )


def reference_b():
    return point(
        5,
        0,
        role="rear_link_shield",
    )


def reference_d():
    return point(
        8,
        0,
        role="front_link_base",
    )


def test_reference_positive_branch():
    h = math.sqrt(
        25.0 - 1.5 * 1.5
    )

    branch = derive_reference_branch(
        reference_b=reference_b(),
        reference_c=point(
            6.5,
            h,
            role="front_link_shield",
        ),
        front_link_base=reference_d(),
        tolerance=tolerance(),
    )

    assert branch == "POSITIVE"


def test_reference_negative_branch():
    h = math.sqrt(
        25.0 - 1.5 * 1.5
    )

    branch = derive_reference_branch(
        reference_b=reference_b(),
        reference_c=point(
            6.5,
            -h,
            role="front_link_shield",
        ),
        front_link_base=reference_d(),
        tolerance=tolerance(),
    )

    assert branch == "NEGATIVE"


def test_reference_on_bd_line_is_unavailable():
    branch = derive_reference_branch(
        reference_b=reference_b(),
        reference_c=point(
            6.5,
            0,
            role="front_link_shield",
        ),
        front_link_base=reference_d(),
        tolerance=tolerance(),
    )

    assert branch is None


def test_reference_near_bd_line_within_tolerance_is_unavailable():
    branch = derive_reference_branch(
        reference_b=reference_b(),
        reference_c=point(
            6.5,
            5e-10,
            role="front_link_shield",
        ),
        front_link_base=reference_d(),
        tolerance=tolerance(),
    )

    assert branch is None


def test_reference_b_equal_d_is_unavailable():
    branch = derive_reference_branch(
        reference_b=point(
            8,
            0,
            role="rear_link_shield",
        ),
        reference_c=point(
            9,
            1,
            role="front_link_shield",
        ),
        front_link_base=reference_d(),
        tolerance=tolerance(),
    )

    assert branch is None


def test_reference_branch_rejects_nonfinite_geometry():
    with pytest.raises(
        ValueError,
        match="finite",
    ):
        derive_reference_branch(
            reference_b=reference_b(),
            reference_c=point(
                math.inf,
                1,
            ),
            front_link_base=reference_d(),
            tolerance=tolerance(),
        )


def test_positive_reference_selects_positive_candidate():
    input_task = task(
        reference_branch="POSITIVE"
    )

    d3 = solve_closure_candidates(
        input_task
    )

    resolved = resolve_reference_branch(
        task=input_task,
        result=d3,
    )

    assert (
        resolved.closure_state
        == "TWO_SOLUTIONS"
    )

    assert (
        resolved.selection_status
        == "SELECTED"
    )

    assert resolved.selected_pose is not None

    assert (
        resolved.selected_pose.branch
        == "POSITIVE"
    )

    assert (
        resolved.provenance.branch_resolution
        == "REFERENCE_POSE"
    )


def test_negative_reference_selects_negative_candidate():
    input_task = task(
        reference_branch="NEGATIVE"
    )

    d3 = solve_closure_candidates(
        input_task
    )

    resolved = resolve_reference_branch(
        task=input_task,
        result=d3,
    )

    assert resolved.selected_pose is not None

    assert (
        resolved.selected_pose.branch
        == "NEGATIVE"
    )


def test_selected_pose_reuses_exact_d3_candidate_coordinates():
    input_task = task(
        reference_branch="POSITIVE"
    )

    d3 = solve_closure_candidates(
        input_task
    )

    positive = next(
        candidate
        for candidate in d3.candidates
        if candidate.branch == "POSITIVE"
    )

    resolved = resolve_reference_branch(
        task=input_task,
        result=d3,
    )

    assert (
        resolved.selected_pose
        .rear_link_shield
        == d3.rear_link_shield
    )

    assert (
        resolved.selected_pose
        .front_link_shield
        == positive.point_c
    )

    assert [
        candidate.branch
        for candidate in resolved.candidates
    ] == [
        "POSITIVE",
        "NEGATIVE",
    ]


def test_reference_selection_preserves_both_math_candidates():
    input_task = task(
        reference_branch="NEGATIVE"
    )

    d3 = solve_closure_candidates(
        input_task
    )

    resolved = resolve_reference_branch(
        task=input_task,
        result=d3,
    )

    assert len(resolved.candidates) == 2

    assert {
        candidate.branch
        for candidate in resolved.candidates
    } == {
        "POSITIVE",
        "NEGATIVE",
    }


def test_missing_reference_keeps_two_solution_ambiguous():
    input_task = task(
        reference_branch=None
    )

    d3 = solve_closure_candidates(
        input_task
    )

    resolved = resolve_reference_branch(
        task=input_task,
        result=d3,
    )

    assert (
        resolved.selection_status
        == "BRANCH_AMBIGUOUS"
    )

    assert resolved.selected_pose is None

    assert (
        resolved.provenance.branch_resolution
        == "NONE"
    )


def test_non_two_solution_result_is_semantically_preserved():
    tangent_task = ClosureSolverInput(
        front_link_base=point(
            8,
            0,
            role="front_link_base",
        ),
        rear_link_length_mm=mm(5),
        shield_beam_effective_length_mm=mm(1),
        front_link_length_mm=mm(2),
        base_pivot_spacing_mm=mm(8),
        rear_link_angle_deg=deg(0),
        reference_branch="POSITIVE",
        tolerance=tolerance(),
    )

    d3 = solve_closure_candidates(
        tangent_task
    )

    resolved = resolve_reference_branch(
        task=tangent_task,
        result=d3,
    )

    assert resolved == d3
    assert resolved is not d3

    assert (
        resolved.closure_state
        == "TANGENT"
    )

    assert (
        resolved.provenance.branch_resolution
        == "TANGENT_UNIQUE"
    )


def test_d4_rejects_already_selected_two_solution():
    input_task = task(
        reference_branch="POSITIVE"
    )

    d3 = solve_closure_candidates(
        input_task
    )

    positive = next(
        candidate
        for candidate in d3.candidates
        if candidate.branch == "POSITIVE"
    )

    already_selected = ClosureResult(
        closure_state="TWO_SOLUTIONS",
        selection_status="SELECTED",
        rear_link_shield=d3.rear_link_shield,
        candidates=d3.candidates,
        selected_pose=ClosureSelectedPose(
            rear_link_shield=(
                d3.rear_link_shield
            ),
            front_link_shield=(
                positive.point_c
            ),
            rear_link_angle_deg=(
                input_task.rear_link_angle_deg
            ),
            branch="POSITIVE",
        ),
        provenance=ClosureSolverProvenance(
            branch_resolution=(
                "REFERENCE_POSE"
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="unresolved D3 TWO_SOLUTIONS",
    ):
        resolve_reference_branch(
            task=input_task,
            result=already_selected,
        )


def test_d4_fails_if_requested_candidate_is_missing():
    input_task = task(
        reference_branch="NEGATIVE"
    )

    d3 = solve_closure_candidates(
        input_task
    )

    positive = next(
        candidate
        for candidate in d3.candidates
        if candidate.branch == "POSITIVE"
    )

    inconsistent = d3.model_copy(
        update={
            "candidates": [
                positive,
            ],
        },
        deep=True,
    )

    with pytest.raises(
        ValueError,
        match="absent",
    ):
        resolve_reference_branch(
            task=input_task,
            result=inconsistent,
        )


def test_resolver_does_not_mutate_task_or_d3_result():
    input_task = task(
        reference_branch="POSITIVE"
    )

    d3 = solve_closure_candidates(
        input_task
    )

    task_snapshot = input_task.model_dump(
        mode="json"
    )

    result_snapshot = d3.model_dump(
        mode="json"
    )

    resolve_reference_branch(
        task=input_task,
        result=d3,
    )

    assert (
        input_task.model_dump(
            mode="json"
        )
        == task_snapshot
    )

    assert (
        d3.model_dump(
            mode="json"
        )
        == result_snapshot
    )


@pytest.mark.parametrize(
    "reference_branch",
    [
        "POSITIVE",
        "NEGATIVE",
        None,
    ],
)
def test_integrated_solve_closure_has_expected_resolution(
    reference_branch,
):
    result = solve_closure(
        task(
            reference_branch=reference_branch
        )
    )

    if reference_branch is None:
        assert (
            result.selection_status
            == "BRANCH_AMBIGUOUS"
        )

        assert result.selected_pose is None

    else:
        assert (
            result.selection_status
            == "SELECTED"
        )

        assert result.selected_pose is not None

        assert (
            result.selected_pose.branch
            == reference_branch
        )

        assert (
            result.provenance.branch_resolution
            == "REFERENCE_POSE"
        )


def test_integrated_solver_calls_d3_exactly_once(
    monkeypatch,
):
    calls = 0

    real_solver = (
        closure_service
        .solve_closure_candidates
    )

    def counted_solver(input_task):
        nonlocal calls
        calls += 1
        return real_solver(input_task)

    monkeypatch.setattr(
        closure_service,
        "solve_closure_candidates",
        counted_solver,
    )

    result = closure_service.solve_closure(
        task(
            reference_branch="POSITIVE"
        )
    )

    assert calls == 1

    assert (
        result.selection_status
        == "SELECTED"
    )


def test_reference_resolution_is_deterministic():
    input_task = task(
        reference_branch="POSITIVE"
    )

    first = solve_closure(
        input_task
    )

    second = solve_closure(
        input_task
    )

    assert first == second
