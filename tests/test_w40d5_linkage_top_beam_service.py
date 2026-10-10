import math

import pytest

from app.models.linkage_closure import (
    ClosureSolverInput,
    NumericalTolerance,
)
from app.models.linkage_geometry import (
    DegreeParameter,
    EngineeringPoint2D,
    LinkageGeometry,
    MillimetreParameter,
    ReferencePose,
    TopBeamInterface,
)
from app.models.linkage_motion import (
    MotionSweepInput,
)
from app.services.linkage_motion import (
    sweep_rear_link_angles,
)
from app.services.linkage_top_beam import (
    propagate_shield_top_beam_joint,
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


def tolerance(
    absolute_mm=1e-9,
    relative=1e-12,
):
    return NumericalTolerance(
        absolute_mm=absolute_mm,
        relative=relative,
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
    tol=None,
):
    if tol is None:
        tol = tolerance()

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
        tolerance=tol,
    )


def build_motion(
    angles,
    *,
    branch="POSITIVE",
    direction="INCREASING",
    task=None,
):
    if task is None:
        task = closure_task(
            angle=angles[0],
            branch=branch,
        )

    sweep = MotionSweepInput(
        reference_task=task,
        direction=direction,
        angle_samples_deg=[
            deg(value)
            for value in angles
        ],
    )

    return sweep_rear_link_angles(
        sweep
    )


def tangent_angle():
    return math.degrees(
        math.acos(
            -11.0 / 80.0
        )
    )


def degenerate_motion():
    angle = 10.0

    dx = (
        5.0
        * math.cos(
            math.radians(angle)
        )
    )

    dy = (
        5.0
        * math.sin(
            math.radians(angle)
        )
    )

    task = closure_task(
        angle=0,
        branch="POSITIVE",
        front_base=(dx, dy),
        ab=5,
        bc=2,
        cd=2,
        da=5,
    )

    return build_motion(
        [0, 10, 20],
        task=task,
    )


def rigid_point_from_local(
    b,
    c,
    *,
    longitudinal,
    normal,
):
    bx = b.x_mm.value
    by = b.y_mm.value

    cx = c.x_mm.value
    cy = c.y_mm.value

    dx = cx - bx
    dy = cy - by

    length = math.hypot(
        dx,
        dy,
    )

    ux = dx / length
    uy = dy / length

    vx = -uy
    vy = ux

    return (
        bx
        + longitudinal * ux
        + normal * vx,
        by
        + longitudinal * uy
        + normal * vy,
    )


def linkage_for_motion(
    motion,
    *,
    longitudinal=2.0,
    normal=1.0,
    b_shift_x=0.0,
    c_shift_x=0.0,
):
    first_pose = (
        motion.samples[0]
        .closure_result
        .selected_pose
    )

    assert first_pose is not None

    source_b = (
        first_pose.rear_link_shield
    )

    source_c = (
        first_pose.front_link_shield
    )

    b = point(
        source_b.x_mm.value
        + b_shift_x,
        source_b.y_mm.value,
    )

    c = point(
        source_c.x_mm.value
        + c_shift_x,
        source_c.y_mm.value,
    )

    ex, ey = rigid_point_from_local(
        b,
        c,
        longitudinal=longitudinal,
        normal=normal,
    )

    return LinkageGeometry(
        reference_pose=ReferencePose(
            support_height_mm=mm(3000),
            rear_link_shield=b,
            front_link_shield=c,
        ),
        top_beam_interface=TopBeamInterface(
            shield_top_beam_pivot=(
                point(ex, ey)
            )
        ),
    )


def test_completed_propagation_returns_one_to_one_samples():
    motion = build_motion(
        [0, 5, 10]
    )

    linkage = linkage_for_motion(
        motion
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    assert len(result.samples) == 3
    assert result.requested_angle_count == 3
    assert result.termination == "COMPLETED"

    assert all(
        item.selected_pose_available
        for item in result.samples
    )

    assert all(
        item.joint_center is not None
        for item in result.samples
    )


def test_reference_attachment_offsets_and_round_trip():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion,
        longitudinal=2.0,
        normal=1.0,
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    assert (
        result.attachment
        .longitudinal_offset_mm.value
        == pytest.approx(2.0)
    )

    assert (
        result.attachment
        .normal_offset_mm.value
        == pytest.approx(1.0)
    )

    expected_e = (
        linkage.top_beam_interface
        .shield_top_beam_pivot
    )

    actual_e = (
        result.samples[0]
        .joint_center
    )

    assert actual_e is not None
    assert expected_e is not None

    assert (
        actual_e.x_mm.value
        == pytest.approx(
            expected_e.x_mm.value
        )
    )

    assert (
        actual_e.y_mm.value
        == pytest.approx(
            expected_e.y_mm.value
        )
    )


def test_second_pose_matches_independent_rigid_transform():
    motion = build_motion(
        [0, 5, 10]
    )

    linkage = linkage_for_motion(
        motion,
        longitudinal=2.5,
        normal=-0.75,
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    second_pose = (
        motion.samples[1]
        .closure_result
        .selected_pose
    )

    assert second_pose is not None

    expected_x, expected_y = (
        rigid_point_from_local(
            second_pose.rear_link_shield,
            second_pose.front_link_shield,
            longitudinal=2.5,
            normal=-0.75,
        )
    )

    actual = (
        result.samples[1]
        .joint_center
    )

    assert actual is not None

    assert (
        actual.x_mm.value
        == pytest.approx(expected_x)
    )

    assert (
        actual.y_mm.value
        == pytest.approx(expected_y)
    )


def test_tangent_boundary_gets_final_e():
    tangent = tangent_angle()

    motion = build_motion(
        [
            0,
            30,
            tangent,
            120,
        ]
    )

    linkage = linkage_for_motion(
        motion
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    assert (
        result.termination
        == "TANGENT_BOUNDARY"
    )

    assert (
        result.samples[-1].closure_state
        == "TANGENT"
    )

    assert (
        result.samples[-1]
        .selected_pose_available
    )

    assert (
        result.samples[-1]
        .joint_center
        is not None
    )


def test_no_solution_boundary_keeps_null_e():
    motion = build_motion(
        [
            0,
            30,
            120,
            130,
        ]
    )

    linkage = linkage_for_motion(
        motion
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    assert (
        result.termination
        == "NO_SOLUTION_BOUNDARY"
    )

    final = result.samples[-1]

    assert (
        final.closure_state
        == "NO_SOLUTION"
    )

    assert not final.selected_pose_available
    assert final.joint_center is None


def test_degenerate_boundary_keeps_null_e():
    motion = degenerate_motion()

    linkage = linkage_for_motion(
        motion
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    assert (
        result.termination
        == "DEGENERATE_BOUNDARY"
    )

    final = result.samples[-1]

    assert (
        final.closure_state
        == "DEGENERATE"
    )

    assert not final.selected_pose_available
    assert final.joint_center is None


def test_requested_count_and_termination_are_preserved():
    motion = build_motion(
        [
            0,
            30,
            120,
            130,
        ]
    )

    linkage = linkage_for_motion(
        motion
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    assert (
        result.requested_angle_count
        == motion.requested_angle_count
    )

    assert (
        result.termination
        == motion.termination
    )

    assert (
        len(result.samples)
        == len(motion.samples)
    )


def test_sample_index_and_angle_alignment_are_preserved():
    motion = build_motion(
        [0, 5, 10]
    )

    linkage = linkage_for_motion(
        motion
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    assert [
        item.sample_index
        for item in result.samples
    ] == [
        item.sample_index
        for item in motion.samples
    ]

    assert [
        item.requested_angle_deg
        .model_dump(mode="json")
        for item in result.samples
    ] == [
        item.requested_angle_deg
        .model_dump(mode="json")
        for item in motion.samples
    ]


def test_result_provenance_is_frozen():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    provenance = result.provenance

    assert (
        provenance.engine
        == "W40_SHIELD_TOP_BEAM_JOINT_RIGID_PROPAGATION"
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


def test_propagated_joint_center_is_calculated_partial():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    joint = (
        result.samples[1]
        .joint_center
    )

    assert joint is not None

    for parameter in (
        joint.x_mm,
        joint.y_mm,
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


def test_reference_e_provenance_is_preserved_in_attachment():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion
    )

    original_e = (
        linkage.top_beam_interface
        .shield_top_beam_pivot
    )

    assert original_e is not None

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    stored_e = (
        result.attachment
        .reference_joint_center
    )

    assert (
        stored_e.x_mm.origin
        == original_e.x_mm.origin
    )

    assert (
        stored_e.x_mm.evidence_status
        == original_e.x_mm.evidence_status
    )

    assert stored_e == original_e


def test_service_does_not_mutate_linkage_motion_or_tolerance():
    motion = build_motion(
        [0, 5, 10]
    )

    linkage = linkage_for_motion(
        motion
    )

    tol = tolerance()

    linkage_before = linkage.model_dump(
        mode="json"
    )

    motion_before = motion.model_dump(
        mode="json"
    )

    tolerance_before = tol.model_dump(
        mode="json"
    )

    propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tol,
    )

    assert (
        linkage.model_dump(
            mode="json"
        )
        == linkage_before
    )

    assert (
        motion.model_dump(
            mode="json"
        )
        == motion_before
    )

    assert (
        tol.model_dump(
            mode="json"
        )
        == tolerance_before
    )


def test_repeated_execution_is_deterministic():
    motion = build_motion(
        [0, 5, 10]
    )

    linkage = linkage_for_motion(
        motion
    )

    tol = tolerance()

    first = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tol,
    )

    second = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tol,
    )

    assert first == second


def test_missing_reference_pose_is_rejected():
    motion = build_motion(
        [0, 5]
    )

    linkage = LinkageGeometry()

    with pytest.raises(
        ValueError,
        match="reference_pose is required",
    ):
        propagate_shield_top_beam_joint(
            linkage=linkage,
            motion=motion,
            tolerance=tolerance(),
        )


def test_missing_e_is_rejected():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion
    )

    linkage.top_beam_interface.shield_top_beam_pivot = None

    with pytest.raises(
        ValueError,
        match="shield_top_beam_pivot E0 is required",
    ):
        propagate_shield_top_beam_joint(
            linkage=linkage,
            motion=motion,
            tolerance=tolerance(),
        )


def test_reference_b_mismatch_is_rejected():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion,
        b_shift_x=0.01,
    )

    with pytest.raises(
        ValueError,
        match="reference B does not match",
    ):
        propagate_shield_top_beam_joint(
            linkage=linkage,
            motion=motion,
            tolerance=tolerance(),
        )


def test_reference_c_mismatch_is_rejected():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion,
        c_shift_x=0.01,
    )

    with pytest.raises(
        ValueError,
        match="reference C does not match",
    ):
        propagate_shield_top_beam_joint(
            linkage=linkage,
            motion=motion,
            tolerance=tolerance(),
        )


def test_numerically_degenerate_reference_axis_is_rejected():
    motion = build_motion(
        [0, 5]
    )

    linkage = LinkageGeometry(
        reference_pose=ReferencePose(
            support_height_mm=mm(3000),
            rear_link_shield=point(
                0,
                0,
            ),
            front_link_shield=point(
                1e-12,
                0,
            ),
        ),
        top_beam_interface=TopBeamInterface(
            shield_top_beam_pivot=point(
                1,
                0,
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="numerically degenerate",
    ):
        propagate_shield_top_beam_joint(
            linkage=linkage,
            motion=motion,
            tolerance=tolerance(
                absolute_mm=1e-9,
            ),
        )


def test_reference_match_within_tolerance_is_accepted():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion,
        b_shift_x=5e-10,
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(
            absolute_mm=1e-9,
        ),
    )

    assert len(result.samples) == 2


def test_scale_aware_relative_tolerance_can_accept_small_relative_error():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion,
        b_shift_x=5e-8,
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(
            absolute_mm=1e-12,
            relative=1e-8,
        ),
    )

    assert len(result.samples) == 2


def test_service_does_not_touch_legacy_trajectory_results():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion
    )

    assert linkage.trajectory_results is None

    propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    assert linkage.trajectory_results is None


def test_output_contains_no_beam_tip_or_support_height_fields():
    motion = build_motion(
        [0, 5]
    )

    linkage = linkage_for_motion(
        motion
    )

    result = propagate_shield_top_beam_joint(
        linkage=linkage,
        motion=motion,
        tolerance=tolerance(),
    )

    payload = result.model_dump(
        mode="json"
    )

    assert "support_height_mm" not in payload
    assert "top_beam_angle_deg" not in payload
    assert "beam_tip_trajectory" not in payload

    assert (
        "beam_tip_horizontal_displacement_mm"
        not in payload
    )
