import math

import pytest

import app.services.linkage_closure_integration as integration

from app.models.linkage_closure import (
    NumericalTolerance,
)
from app.models.linkage_geometry import (
    EngineeringPoint2D,
    LinkageGeometry,
    MillimetreParameter,
    ReferencePose,
)
from app.services.linkage_closure import (
    solve_closure,
)
from app.services.linkage_closure_integration import (
    build_closure_task_from_linkage,
    solve_linkage_reference_pose,
    validate_reference_pose_round_trip,
)
from app.services.linkage_pose import (
    analyze_reference_pose,
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


def numerical_tolerance():
    return NumericalTolerance(
        absolute_mm=1e-9,
        relative=1e-12,
    )


def complete_linkage(
    *,
    height=3000,
    rear=(300, 400),
    front=(900, 1200),
    front_base=(1000, 0),
):
    linkage = LinkageGeometry(
        reference_pose=ReferencePose(
            support_height_mm=mm(
                height
            ),
            rear_link_shield=point(
                *rear,
                role="rear_link_shield",
            ),
            front_link_shield=point(
                *front,
                role="front_link_shield",
            ),
        )
    )

    linkage.fixed_geometry.front_link_base = point(
        *front_base,
        role="front_link_base",
    )

    return linkage


def assert_point_close(
    actual,
    expected,
    *,
    abs_tol=1e-8,
):
    assert (
        actual.x_mm.value
        == pytest.approx(
            expected.x_mm.value,
            abs=abs_tol,
        )
    )

    assert (
        actual.y_mm.value
        == pytest.approx(
            expected.y_mm.value,
            abs=abs_tol,
        )
    )


def test_build_task_uses_fresh_four_bar_dimensions():
    linkage = complete_linkage()

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert (
        task.rear_link_length_mm.value
        == pytest.approx(500.0)
    )

    assert (
        task.shield_beam_effective_length_mm.value
        == pytest.approx(1000.0)
    )

    assert (
        task.front_link_length_mm.value
        == pytest.approx(
            math.hypot(
                100,
                1200,
            )
        )
    )

    assert (
        task.base_pivot_spacing_mm.value
        == pytest.approx(1000.0)
    )


def test_build_task_reuses_w38_reference_angle():
    linkage = complete_linkage()

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    expected = math.degrees(
        math.atan2(
            400,
            300,
        )
    )

    assert (
        task.rear_link_angle_deg.value
        == pytest.approx(expected)
    )

    assert (
        task.rear_link_angle_deg.origin
        == "CALCULATED"
    )

    assert (
        task.rear_link_angle_deg.evidence_status
        == "PARTIAL"
    )


def test_build_task_derives_positive_reference_branch():
    linkage = complete_linkage()

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert (
        task.reference_branch
        == "POSITIVE"
    )


def test_w38_same_side_is_not_used_as_w39_branch_mapping():
    linkage = complete_linkage(
        rear=(300, 800),
        front=(900, 100),
        front_base=(1000, 0),
    )

    analysis = analyze_reference_pose(
        linkage
    )

    assert (
        analysis.assembly_side_signature
        == "SAME_SIDE"
    )

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    # Both moving pivots are above A->D, but C is on the
    # NEGATIVE side of directed B->D.
    assert (
        task.reference_branch
        == "NEGATIVE"
    )


def test_missing_front_base_is_rejected():
    linkage = LinkageGeometry(
        reference_pose=ReferencePose(
            support_height_mm=mm(3000),
            rear_link_shield=point(
                300,
                400,
            ),
            front_link_shield=point(
                900,
                1200,
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="front_link_base is required",
    ):
        build_closure_task_from_linkage(
            linkage=linkage,
            tolerance=numerical_tolerance(),
        )


def test_missing_reference_pose_is_rejected():
    linkage = LinkageGeometry()

    linkage.fixed_geometry.front_link_base = point(
        1000,
        0,
    )

    with pytest.raises(
        ValueError,
        match="reference_pose is required",
    ):
        build_closure_task_from_linkage(
            linkage=linkage,
            tolerance=numerical_tolerance(),
        )


def test_degenerate_w38_reference_is_rejected():
    linkage = complete_linkage(
        rear=(0, 0),
    )

    with pytest.raises(
        ValueError,
        match="degenerate W38 reference geometry",
    ):
        build_closure_task_from_linkage(
            linkage=linkage,
            tolerance=numerical_tolerance(),
        )


def test_stored_derived_geometry_is_not_authoritative():
    linkage = complete_linkage()

    linkage.derived_geometry.base_pivot_spacing_mm = mm(
        9999
    )

    linkage.derived_geometry.rear_link_length_mm = mm(
        9999
    )

    linkage.derived_geometry.front_link_length_mm = mm(
        9999
    )

    linkage.derived_geometry.shield_beam_effective_length_mm = mm(
        9999
    )

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert (
        task.base_pivot_spacing_mm.value
        == pytest.approx(1000.0)
    )

    assert (
        task.rear_link_length_mm.value
        == pytest.approx(500.0)
    )

    assert (
        task.shield_beam_effective_length_mm.value
        == pytest.approx(1000.0)
    )

    assert (
        task.front_link_length_mm.value
        != 9999
    )


def test_support_height_does_not_change_closure_task():
    a = complete_linkage(
        height=2500
    )

    b = complete_linkage(
        height=5000
    )

    task_a = build_closure_task_from_linkage(
        linkage=a,
        tolerance=numerical_tolerance(),
    )

    task_b = build_closure_task_from_linkage(
        linkage=b,
        tolerance=numerical_tolerance(),
    )

    assert (
        task_a.model_dump(mode="json")
        == task_b.model_dump(mode="json")
    )


def test_top_beam_geometry_does_not_change_closure_task():
    baseline = complete_linkage()

    changed = complete_linkage()

    changed.top_beam_interface.shield_top_beam_pivot = (
        point(
            9999,
            -9999,
        )
    )

    changed.top_beam_interface.beam_tip_reference_point = (
        point(
            -7777,
            8888,
        )
    )

    task_a = build_closure_task_from_linkage(
        linkage=baseline,
        tolerance=numerical_tolerance(),
    )

    task_b = build_closure_task_from_linkage(
        linkage=changed,
        tolerance=numerical_tolerance(),
    )

    assert (
        task_a.model_dump(mode="json")
        == task_b.model_dump(mode="json")
    )


def test_build_task_does_not_mutate_linkage():
    linkage = complete_linkage()

    linkage.derived_geometry.base_pivot_spacing_mm = mm(
        777
    )

    before = linkage.model_dump(
        mode="json"
    )

    build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert (
        linkage.model_dump(
            mode="json"
        )
        == before
    )


def test_positive_reference_pose_round_trip():
    linkage = complete_linkage()

    result = solve_linkage_reference_pose(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert (
        result.closure_state
        == "TWO_SOLUTIONS"
    )

    assert (
        result.selection_status
        == "SELECTED"
    )

    assert result.selected_pose is not None

    assert (
        result.selected_pose.branch
        == "POSITIVE"
    )

    assert (
        result.provenance.branch_resolution
        == "REFERENCE_POSE"
    )

    assert_point_close(
        result.selected_pose.rear_link_shield,
        linkage.reference_pose.rear_link_shield,
    )

    assert_point_close(
        result.selected_pose.front_link_shield,
        linkage.reference_pose.front_link_shield,
    )


def test_negative_reference_pose_round_trip():
    linkage = complete_linkage(
        rear=(300, 400),
        front=(900, -400),
        front_base=(1000, 0),
    )

    result = solve_linkage_reference_pose(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert result.selected_pose is not None

    assert (
        result.selected_pose.branch
        == "NEGATIVE"
    )

    assert_point_close(
        result.selected_pose.rear_link_shield,
        linkage.reference_pose.rear_link_shield,
    )

    assert_point_close(
        result.selected_pose.front_link_shield,
        linkage.reference_pose.front_link_shield,
    )


def test_tangent_reference_can_round_trip_without_reference_branch():
    linkage = complete_linkage(
        rear=(5, 2),
        front=(6.5, 1),
        front_base=(8, 0),
    )

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert task.reference_branch is None

    result = solve_linkage_reference_pose(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert result.closure_state == "TANGENT"

    assert (
        result.selection_status
        == "SELECTED"
    )

    assert result.selected_pose is not None

    assert (
        result.selected_pose.branch
        == "TANGENT"
    )

    assert (
        result.provenance.branch_resolution
        == "TANGENT_UNIQUE"
    )

    assert_point_close(
        result.selected_pose.front_link_shield,
        linkage.reference_pose.front_link_shield,
    )


def test_round_trip_rejects_unselected_two_solution():
    linkage = complete_linkage()

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    unresolved_task = task.model_copy(
        update={
            "reference_branch": None,
        },
        deep=True,
    )

    result = solve_closure(
        unresolved_task
    )

    assert result.selected_pose is None

    with pytest.raises(
        ValueError,
        match="requires a unique selected pose",
    ):
        validate_reference_pose_round_trip(
            linkage=linkage,
            task=unresolved_task,
            result=result,
        )


def test_round_trip_rejects_wrong_reference_b():
    linkage = complete_linkage()

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    result = solve_closure(
        task
    )

    other_linkage = complete_linkage(
        rear=(301, 400),
        front=(900, 1200),
    )

    with pytest.raises(
        ValueError,
        match="rear_link_shield round-trip mismatch",
    ):
        validate_reference_pose_round_trip(
            linkage=other_linkage,
            task=task,
            result=result,
        )


def test_round_trip_rejects_wrong_reference_c():
    linkage = complete_linkage()

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    result = solve_closure(
        task
    )

    other_linkage = complete_linkage(
        rear=(300, 400),
        front=(901, 1200),
    )

    with pytest.raises(
        ValueError,
        match="front_link_shield round-trip mismatch",
    ):
        validate_reference_pose_round_trip(
            linkage=other_linkage,
            task=task,
            result=result,
        )


def test_round_trip_preserves_calculated_partial_provenance():
    linkage = complete_linkage()

    result = solve_linkage_reference_pose(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert result.selected_pose is not None

    for point_value in (
        result.selected_pose.rear_link_shield,
        result.selected_pose.front_link_shield,
    ):
        for parameter in (
            point_value.x_mm,
            point_value.y_mm,
        ):
            assert (
                parameter.origin
                == "CALCULATED"
            )

            assert (
                parameter.evidence_status
                == "PARTIAL"
            )

            assert parameter.formula_ids == []

            assert (
                parameter.calculation_record_ids
                == []
            )


def test_integrated_solve_does_not_mutate_linkage():
    linkage = complete_linkage()

    linkage.derived_geometry.base_pivot_spacing_mm = mm(
        777
    )

    before = linkage.model_dump(
        mode="json"
    )

    solve_linkage_reference_pose(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert (
        linkage.model_dump(
            mode="json"
        )
        == before
    )


def test_integrated_solver_calls_existing_w39_solver_once(
    monkeypatch,
):
    linkage = complete_linkage()

    calls = 0

    real_solver = integration.solve_closure

    def counted_solver(task):
        nonlocal calls
        calls += 1
        return real_solver(task)

    monkeypatch.setattr(
        integration,
        "solve_closure",
        counted_solver,
    )

    result = integration.solve_linkage_reference_pose(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert calls == 1

    assert (
        result.selection_status
        == "SELECTED"
    )


def test_integrated_reference_solve_is_deterministic():
    linkage = complete_linkage()

    first = solve_linkage_reference_pose(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    second = solve_linkage_reference_pose(
        linkage=linkage,
        tolerance=numerical_tolerance(),
    )

    assert first == second


def test_explicit_tolerance_is_required():
    linkage = complete_linkage()

    with pytest.raises(TypeError):
        build_closure_task_from_linkage(
            linkage=linkage,
        )
