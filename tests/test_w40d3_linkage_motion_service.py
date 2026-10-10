import math

import pytest

import app.services.linkage_motion as motion_service

from app.models.linkage_closure import (
    ClosureSolverInput,
    NumericalTolerance,
)
from app.models.linkage_geometry import (
    DegreeParameter,
    EngineeringPoint2D,
    MillimetreParameter,
)
from app.models.linkage_motion import (
    MotionSweepInput,
)
from app.services.linkage_closure import (
    solve_closure,
)
from app.services.linkage_motion import (
    sweep_rear_link_angles,
)


def mm(value):
    return MillimetreParameter(
        value=value,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
    )


def deg(value):
    return DegreeParameter(
        value=value,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
    )


def point(x, y):
    return EngineeringPoint2D(
        x_mm=mm(x),
        y_mm=mm(y),
    )


def tolerance():
    return NumericalTolerance(
        absolute_mm=1e-9,
        relative=1e-12,
    )


def closure_task(
    *,
    angle=0,
    branch="POSITIVE",
    front_base=(8, 0),
    ab=5,
    bc=5,
    cd=5,
    da=8,
):
    return ClosureSolverInput(
        front_link_base=point(
            *front_base
        ),
        rear_link_length_mm=mm(ab),
        shield_beam_effective_length_mm=mm(bc),
        front_link_length_mm=mm(cd),
        base_pivot_spacing_mm=mm(da),
        rear_link_angle_deg=deg(angle),
        reference_branch=branch,
        tolerance=tolerance(),
    )


def sweep(
    angles,
    *,
    branch="POSITIVE",
    direction="INCREASING",
    reference_task=None,
):
    if reference_task is None:
        reference_task = closure_task(
            angle=angles[0],
            branch=branch,
        )

    return MotionSweepInput(
        reference_task=reference_task,
        direction=direction,
        angle_samples_deg=[
            deg(value)
            for value in angles
        ],
    )


def tangent_angle():
    # Standard fixture:
    # A=(0,0), D=(8,0), AB=BC=CD=5.
    # q^2 = 89 - 80*cos(theta).
    # External tangent occurs at q=10.
    return math.degrees(
        math.acos(
            -11.0 / 80.0
        )
    )


def degenerate_reference_task():
    # At theta=10°, make D coincide with B.
    angle = 10.0

    d_x = 5.0 * math.cos(
        math.radians(angle)
    )

    d_y = 5.0 * math.sin(
        math.radians(angle)
    )

    return closure_task(
        angle=0,
        branch="POSITIVE",
        front_base=(d_x, d_y),
        ab=5,
        bc=2,
        cd=2,
        da=5,
    )


def test_completed_increasing_positive_sweep():
    result = sweep_rear_link_angles(
        sweep(
            [0, 5, 10],
            branch="POSITIVE",
        )
    )

    assert result.termination == "COMPLETED"
    assert result.direction == "INCREASING"

    assert len(result.samples) == 3
    assert result.requested_angle_count == 3

    assert [
        item.closure_result
        .selected_pose.branch
        for item in result.samples
    ] == [
        "POSITIVE",
        "POSITIVE",
        "POSITIVE",
    ]


def test_completed_decreasing_negative_sweep():
    result = sweep_rear_link_angles(
        sweep(
            [20, 10, 0],
            branch="NEGATIVE",
            direction="DECREASING",
        )
    )

    assert result.termination == "COMPLETED"
    assert result.direction == "DECREASING"

    assert [
        item.closure_result
        .selected_pose.branch
        for item in result.samples
    ] == [
        "NEGATIVE",
        "NEGATIVE",
        "NEGATIVE",
    ]


def test_first_sample_is_solved_reference_pose():
    request = sweep(
        [0, 5],
        branch="POSITIVE",
    )

    result = sweep_rear_link_angles(
        request
    )

    first = result.samples[0]

    assert first.sample_index == 0
    assert first.requested_angle_deg.value == 0

    assert (
        first.closure_result.closure_state
        == "TWO_SOLUTIONS"
    )

    assert (
        first.closure_result.selection_status
        == "SELECTED"
    )

    assert (
        first.closure_result
        .selected_pose.branch
        == "POSITIVE"
    )


def test_per_angle_tasks_change_only_angle(
    monkeypatch,
):
    request = sweep(
        [0, 5, 10],
    )

    captured = []

    real_solver = motion_service.solve_closure

    def capturing_solver(task):
        captured.append(task)
        return real_solver(task)

    monkeypatch.setattr(
        motion_service,
        "solve_closure",
        capturing_solver,
    )

    sweep_rear_link_angles(
        request
    )

    assert len(captured) == 3

    reference_payload = (
        request.reference_task.model_dump(
            mode="json"
        )
    )

    reference_payload.pop(
        "rear_link_angle_deg"
    )

    for task in captured:
        payload = task.model_dump(
            mode="json"
        )

        payload.pop(
            "rear_link_angle_deg"
        )

        assert payload == reference_payload

    assert [
        task.rear_link_angle_deg.value
        for task in captured
    ] == [
        0,
        5,
        10,
    ]


def test_each_processed_angle_uses_new_task_object(
    monkeypatch,
):
    request = sweep(
        [0, 5, 10],
    )

    captured = []

    real_solver = motion_service.solve_closure

    def capturing_solver(task):
        captured.append(task)
        return real_solver(task)

    monkeypatch.setattr(
        motion_service,
        "solve_closure",
        capturing_solver,
    )

    sweep_rear_link_angles(
        request
    )

    assert all(
        task is not request.reference_task
        for task in captured
    )

    assert len({
        id(task)
        for task in captured
    }) == 3


def test_complete_sweep_calls_w39_once_per_angle(
    monkeypatch,
):
    request = sweep(
        [0, 5, 10, 15],
    )

    calls = 0

    real_solver = motion_service.solve_closure

    def counted_solver(task):
        nonlocal calls
        calls += 1
        return real_solver(task)

    monkeypatch.setattr(
        motion_service,
        "solve_closure",
        counted_solver,
    )

    result = sweep_rear_link_angles(
        request
    )

    assert calls == 4
    assert len(result.samples) == 4


def test_requested_angle_parameters_are_preserved():
    request = sweep(
        [0, 5, 10],
    )

    result = sweep_rear_link_angles(
        request
    )

    assert [
        item.requested_angle_deg.model_dump(
            mode="json"
        )
        for item in result.samples
    ] == [
        item.model_dump(
            mode="json"
        )
        for item in request.angle_samples_deg
    ]


def test_tangent_boundary_is_appended_and_stops():
    tangent = tangent_angle()

    request = sweep(
        [
            0,
            30,
            tangent,
            120,
        ]
    )

    result = sweep_rear_link_angles(
        request
    )

    assert (
        result.termination
        == "TANGENT_BOUNDARY"
    )

    assert len(result.samples) == 3

    assert (
        result.samples[-1]
        .closure_result.closure_state
        == "TANGENT"
    )

    assert (
        result.samples[-1]
        .closure_result.selected_pose.branch
        == "TANGENT"
    )


def test_tangent_boundary_preserves_requested_count():
    tangent = tangent_angle()

    result = sweep_rear_link_angles(
        sweep(
            [
                0,
                30,
                tangent,
                120,
            ]
        )
    )

    assert result.requested_angle_count == 4
    assert len(result.samples) == 3


def test_no_solution_boundary_is_appended_and_stops():
    result = sweep_rear_link_angles(
        sweep(
            [
                0,
                30,
                120,
                130,
            ]
        )
    )

    assert (
        result.termination
        == "NO_SOLUTION_BOUNDARY"
    )

    assert len(result.samples) == 3

    assert (
        result.samples[-1]
        .closure_result.closure_state
        == "NO_SOLUTION"
    )

    assert (
        result.samples[-1]
        .closure_result.selected_pose
        is None
    )


def test_degenerate_boundary_is_appended_and_stops():
    request = sweep(
        [
            0,
            10,
            20,
        ],
        reference_task=(
            degenerate_reference_task()
        ),
    )

    result = sweep_rear_link_angles(
        request
    )

    assert (
        result.termination
        == "DEGENERATE_BOUNDARY"
    )

    assert len(result.samples) == 2

    assert (
        result.samples[-1]
        .closure_result.closure_state
        == "DEGENERATE"
    )


def test_no_solver_calls_after_tangent(
    monkeypatch,
):
    tangent = tangent_angle()

    request = sweep(
        [
            0,
            30,
            tangent,
            120,
            130,
        ]
    )

    calls = []

    real_solver = motion_service.solve_closure

    def counted_solver(task):
        calls.append(
            task.rear_link_angle_deg.value
        )

        return real_solver(task)

    monkeypatch.setattr(
        motion_service,
        "solve_closure",
        counted_solver,
    )

    sweep_rear_link_angles(
        request
    )

    assert len(calls) == 3

    assert calls == [
        0,
        30,
        pytest.approx(tangent),
    ]


def test_ambiguous_two_solution_is_explicit_error(
    monkeypatch,
):
    request = sweep(
        [0, 5, 10],
    )

    calls = 0

    real_solver = motion_service.solve_closure

    def ambiguous_second(task):
        nonlocal calls
        calls += 1

        if calls == 2:
            payload = task.model_dump(
                mode="python"
            )

            payload[
                "reference_branch"
            ] = None

            ambiguous_task = (
                ClosureSolverInput
                .model_validate(
                    payload
                )
            )

            return real_solver(
                ambiguous_task
            )

        return real_solver(task)

    monkeypatch.setattr(
        motion_service,
        "solve_closure",
        ambiguous_second,
    )

    with pytest.raises(
        ValueError,
        match="ambiguous TWO_SOLUTIONS",
    ):
        sweep_rear_link_angles(
            request
        )


def test_opposite_selected_branch_is_explicit_error(
    monkeypatch,
):
    request = sweep(
        [0, 5, 10],
        branch="POSITIVE",
    )

    calls = 0

    real_solver = motion_service.solve_closure

    def opposite_second(task):
        nonlocal calls
        calls += 1

        if calls == 2:
            payload = task.model_dump(
                mode="python"
            )

            payload[
                "reference_branch"
            ] = "NEGATIVE"

            opposite_task = (
                ClosureSolverInput
                .model_validate(
                    payload
                )
            )

            return real_solver(
                opposite_task
            )

        return real_solver(task)

    monkeypatch.setattr(
        motion_service,
        "solve_closure",
        opposite_second,
    )

    with pytest.raises(
        ValueError,
        match="does not match the frozen reference branch",
    ):
        sweep_rear_link_angles(
            request
        )


def test_first_tangent_sample_is_rejected():
    tangent = tangent_angle()

    request = sweep(
        [
            tangent,
            tangent + 1,
        ],
        branch="POSITIVE",
    )

    with pytest.raises(
        ValueError,
        match="first solved sample",
    ):
        sweep_rear_link_angles(
            request
        )


def test_complete_w39_candidates_are_preserved():
    result = sweep_rear_link_angles(
        sweep(
            [0, 5],
        )
    )

    second = result.samples[1]

    assert len(
        second.closure_result.candidates
    ) == 2

    assert {
        candidate.branch
        for candidate
        in second.closure_result.candidates
    } == {
        "POSITIVE",
        "NEGATIVE",
    }


def test_result_preserves_direction_and_reference_metadata():
    request = sweep(
        [20, 10, 0],
        branch="NEGATIVE",
        direction="DECREASING",
    )

    result = sweep_rear_link_angles(
        request
    )

    assert (
        result.direction
        == request.direction
    )

    assert (
        result.reference_branch
        == request.reference_task.reference_branch
    )

    assert (
        result.reference_angle_deg.value
        == request.reference_task
        .rear_link_angle_deg.value
    )


def test_result_uses_frozen_motion_provenance():
    result = sweep_rear_link_angles(
        sweep(
            [0, 5],
        )
    )

    provenance = result.provenance

    assert (
        provenance.engine
        == "W40_BRANCH_PRESERVING_ANGLE_SWEEP"
    )

    assert (
        provenance.evidence_status
        == "PARTIAL"
    )

    assert provenance.formula_ids == []

    assert (
        provenance.calculation_record_ids
        == []
    )


def test_complete_sweep_does_not_mutate_input():
    request = sweep(
        [0, 5, 10],
    )

    before = request.model_dump(
        mode="json"
    )

    sweep_rear_link_angles(
        request
    )

    assert (
        request.model_dump(
            mode="json"
        )
        == before
    )


def test_boundary_sweep_does_not_mutate_input():
    request = sweep(
        [
            0,
            30,
            120,
        ]
    )

    before = request.model_dump(
        mode="json"
    )

    sweep_rear_link_angles(
        request
    )

    assert (
        request.model_dump(
            mode="json"
        )
        == before
    )


def test_repeated_execution_is_deterministic():
    request = sweep(
        [0, 5, 10],
    )

    first = sweep_rear_link_angles(
        request
    )

    second = sweep_rear_link_angles(
        request
    )

    assert first == second


def test_service_result_has_no_support_height_or_top_beam_fields():
    result = sweep_rear_link_angles(
        sweep(
            [0, 5],
        )
    )

    payload = result.model_dump(
        mode="json"
    )

    assert "support_height_mm" not in payload
    assert "top_beam_pose" not in payload
    assert "beam_tip_trajectory" not in payload


def test_service_solves_only_explicit_requested_angles(
    monkeypatch,
):
    request = sweep(
        [
            0,
            7,
            19,
            31,
        ]
    )

    solved_angles = []

    real_solver = motion_service.solve_closure

    def capturing_solver(task):
        solved_angles.append(
            task.rear_link_angle_deg.value
        )

        return real_solver(task)

    monkeypatch.setattr(
        motion_service,
        "solve_closure",
        capturing_solver,
    )

    sweep_rear_link_angles(
        request
    )

    assert solved_angles == [
        0,
        7,
        19,
        31,
    ]
