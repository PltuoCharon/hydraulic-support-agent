"""W40-D5 deterministic shield/top-beam joint propagation.

Boundary:
- derive the reference E attachment from explicit B0/C0/E0
- preserve the directed shield frame B -> C
- propagate E for every selected W40 motion pose
- preserve unsolved boundary samples with joint_center=None
- no top-beam orientation solving
- no beam-tip trajectory
- no support-height solving
- no 80 mm validation
"""

from __future__ import annotations

import math

from app.models.linkage_closure import (
    NumericalTolerance,
)
from app.models.linkage_geometry import (
    EngineeringPoint2D,
    LinkageGeometry,
    MillimetreParameter,
)
from app.models.linkage_motion import (
    MotionSegmentResult,
)
from app.models.linkage_top_beam import (
    ShieldTopBeamJointAttachment,
    ShieldTopBeamJointTrajectoryResult,
    ShieldTopBeamJointTrajectorySample,
)
from app.services.linkage_closure import (
    _effective_distance_tolerance,
)


SOURCE_TEXT = (
    "W40-D5 deterministic shield/top-beam "
    "joint rigid-body propagation"
)


def _finite_float(
    value,
    *,
    name: str,
) -> float:
    result = float(value)

    if not math.isfinite(result):
        raise ValueError(
            f"{name} must be finite"
        )

    return result


def _point_xy(
    point: EngineeringPoint2D,
    *,
    name: str,
) -> tuple[float, float]:
    return (
        _finite_float(
            point.x_mm.value,
            name=f"{name}.x_mm",
        ),
        _finite_float(
            point.y_mm.value,
            name=f"{name}.y_mm",
        ),
    )


def _point_norm_mm(
    point: EngineeringPoint2D,
    *,
    name: str,
) -> float:
    x_mm, y_mm = _point_xy(
        point,
        name=name,
    )

    return math.hypot(
        x_mm,
        y_mm,
    )


def _point_error_mm(
    left: EngineeringPoint2D,
    right: EngineeringPoint2D,
    *,
    left_name: str,
    right_name: str,
) -> float:
    left_x, left_y = _point_xy(
        left,
        name=left_name,
    )

    right_x, right_y = _point_xy(
        right,
        name=right_name,
    )

    return math.hypot(
        left_x - right_x,
        left_y - right_y,
    )


def _calculated_mm(
    value: float,
) -> MillimetreParameter:
    return MillimetreParameter(
        value=value,
        origin="CALCULATED",
        evidence_status="PARTIAL",
        source_text=SOURCE_TEXT,
        formula_ids=[],
        calculation_record_ids=[],
    )


def _calculated_point(
    x_mm: float,
    y_mm: float,
    *,
    point_role: str,
) -> EngineeringPoint2D:
    return EngineeringPoint2D(
        x_mm=_calculated_mm(
            x_mm
        ),
        y_mm=_calculated_mm(
            y_mm
        ),
        point_role=point_role,
    )


def _shield_frame(
    *,
    point_b: EngineeringPoint2D,
    point_c: EngineeringPoint2D,
    tolerance: NumericalTolerance,
    context: str,
) -> tuple[
    float,
    float,
    float,
    float,
    float,
]:
    """Return directed B->C frame: ux, uy, vx, vy, length."""

    bx, by = _point_xy(
        point_b,
        name=f"{context}.B",
    )

    cx, cy = _point_xy(
        point_c,
        name=f"{context}.C",
    )

    dx = cx - bx
    dy = cy - by

    length_mm = math.hypot(
        dx,
        dy,
    )

    tolerance_mm = (
        _effective_distance_tolerance(
            tolerance,
            math.hypot(bx, by),
            math.hypot(cx, cy),
            length_mm,
        )
    )

    if length_mm <= tolerance_mm:
        raise ValueError(
            f"{context} B/C shield axis is "
            "numerically degenerate: "
            f"length={length_mm!r} mm, "
            f"tolerance={tolerance_mm!r} mm"
        )

    ux = dx / length_mm
    uy = dy / length_mm

    vx = -uy
    vy = ux

    return (
        ux,
        uy,
        vx,
        vy,
        length_mm,
    )


def _derive_attachment(
    *,
    linkage: LinkageGeometry,
    tolerance: NumericalTolerance,
) -> ShieldTopBeamJointAttachment:
    """Derive the fixed local E coordinate from explicit B0/C0/E0."""

    reference_pose = (
        linkage.reference_pose
    )

    if reference_pose is None:
        raise ValueError(
            "reference_pose is required for "
            "W40-D5 E propagation"
        )

    reference_e = (
        linkage.top_beam_interface
        .shield_top_beam_pivot
    )

    if reference_e is None:
        raise ValueError(
            "shield_top_beam_pivot E0 is required "
            "for W40-D5 E propagation"
        )

    reference_b = (
        reference_pose
        .rear_link_shield
    )

    reference_c = (
        reference_pose
        .front_link_shield
    )

    (
        ux,
        uy,
        vx,
        vy,
        shield_length_mm,
    ) = _shield_frame(
        point_b=reference_b,
        point_c=reference_c,
        tolerance=tolerance,
        context="reference",
    )

    bx, by = _point_xy(
        reference_b,
        name="reference.B0",
    )

    ex, ey = _point_xy(
        reference_e,
        name="reference.E0",
    )

    eb_x = ex - bx
    eb_y = ey - by

    longitudinal_offset_mm = (
        eb_x * ux
        + eb_y * uy
    )

    normal_offset_mm = (
        eb_x * vx
        + eb_y * vy
    )

    roundtrip_x = (
        bx
        + longitudinal_offset_mm * ux
        + normal_offset_mm * vx
    )

    roundtrip_y = (
        by
        + longitudinal_offset_mm * uy
        + normal_offset_mm * vy
    )

    roundtrip_error_mm = math.hypot(
        roundtrip_x - ex,
        roundtrip_y - ey,
    )

    roundtrip_tolerance_mm = (
        _effective_distance_tolerance(
            tolerance,
            _point_norm_mm(
                reference_b,
                name="reference.B0",
            ),
            _point_norm_mm(
                reference_c,
                name="reference.C0",
            ),
            _point_norm_mm(
                reference_e,
                name="reference.E0",
            ),
            shield_length_mm,
            abs(longitudinal_offset_mm),
            abs(normal_offset_mm),
        )
    )

    if (
        roundtrip_error_mm
        > roundtrip_tolerance_mm
    ):
        raise ValueError(
            "reference E0 rigid-frame round trip "
            "exceeds NumericalTolerance: "
            f"error={roundtrip_error_mm!r} mm, "
            f"tolerance={roundtrip_tolerance_mm!r} mm"
        )

    return ShieldTopBeamJointAttachment(
        reference_rear_link_shield=(
            reference_b.model_copy(
                deep=True
            )
        ),
        reference_front_link_shield=(
            reference_c.model_copy(
                deep=True
            )
        ),
        reference_joint_center=(
            reference_e.model_copy(
                deep=True
            )
        ),
        longitudinal_offset_mm=(
            _calculated_mm(
                longitudinal_offset_mm
            )
        ),
        normal_offset_mm=(
            _calculated_mm(
                normal_offset_mm
            )
        ),
    )


def _validate_motion_reference(
    *,
    attachment: ShieldTopBeamJointAttachment,
    motion: MotionSegmentResult,
    tolerance: NumericalTolerance,
) -> None:
    """Verify that motion sample zero belongs to the same reference geometry."""

    first = motion.samples[0]

    selected_pose = (
        first.closure_result.selected_pose
    )

    if selected_pose is None:
        raise ValueError(
            "first motion sample requires a "
            "selected reference pose"
        )

    motion_b = (
        selected_pose.rear_link_shield
    )

    motion_c = (
        selected_pose.front_link_shield
    )

    reference_b = (
        attachment
        .reference_rear_link_shield
    )

    reference_c = (
        attachment
        .reference_front_link_shield
    )

    reference_b_x, reference_b_y = (
        _point_xy(
            reference_b,
            name="attachment.reference_B",
        )
    )

    reference_c_x, reference_c_y = (
        _point_xy(
            reference_c,
            name="attachment.reference_C",
        )
    )

    motion_b_x, motion_b_y = (
        _point_xy(
            motion_b,
            name="motion.reference_B",
        )
    )

    motion_c_x, motion_c_y = (
        _point_xy(
            motion_c,
            name="motion.reference_C",
        )
    )

    reference_length_mm = math.hypot(
        reference_c_x - reference_b_x,
        reference_c_y - reference_b_y,
    )

    motion_length_mm = math.hypot(
        motion_c_x - motion_b_x,
        motion_c_y - motion_b_y,
    )

    tolerance_mm = (
        _effective_distance_tolerance(
            tolerance,
            math.hypot(
                reference_b_x,
                reference_b_y,
            ),
            math.hypot(
                reference_c_x,
                reference_c_y,
            ),
            math.hypot(
                motion_b_x,
                motion_b_y,
            ),
            math.hypot(
                motion_c_x,
                motion_c_y,
            ),
            reference_length_mm,
            motion_length_mm,
        )
    )

    b_error_mm = _point_error_mm(
        reference_b,
        motion_b,
        left_name="attachment.reference_B",
        right_name="motion.reference_B",
    )

    c_error_mm = _point_error_mm(
        reference_c,
        motion_c,
        left_name="attachment.reference_C",
        right_name="motion.reference_C",
    )

    if b_error_mm > tolerance_mm:
        raise ValueError(
            "motion reference B does not match "
            "LinkageGeometry reference B: "
            f"error={b_error_mm!r} mm, "
            f"tolerance={tolerance_mm!r} mm"
        )

    if c_error_mm > tolerance_mm:
        raise ValueError(
            "motion reference C does not match "
            "LinkageGeometry reference C: "
            f"error={c_error_mm!r} mm, "
            f"tolerance={tolerance_mm!r} mm"
        )


def _propagate_joint_center(
    *,
    point_b: EngineeringPoint2D,
    point_c: EngineeringPoint2D,
    attachment: ShieldTopBeamJointAttachment,
    tolerance: NumericalTolerance,
    context: str,
) -> EngineeringPoint2D:
    """Propagate E using the frozen local shield-frame attachment."""

    (
        ux,
        uy,
        vx,
        vy,
        shield_length_mm,
    ) = _shield_frame(
        point_b=point_b,
        point_c=point_c,
        tolerance=tolerance,
        context=context,
    )

    bx, by = _point_xy(
        point_b,
        name=f"{context}.B",
    )

    longitudinal_offset_mm = _finite_float(
        attachment
        .longitudinal_offset_mm
        .value,
        name="attachment.longitudinal_offset_mm",
    )

    normal_offset_mm = _finite_float(
        attachment
        .normal_offset_mm
        .value,
        name="attachment.normal_offset_mm",
    )

    ex = (
        bx
        + longitudinal_offset_mm * ux
        + normal_offset_mm * vx
    )

    ey = (
        by
        + longitudinal_offset_mm * uy
        + normal_offset_mm * vy
    )

    # Verify that the propagated point still reconstructs
    # the same local rigid-body attachment.
    eb_x = ex - bx
    eb_y = ey - by

    recovered_s_mm = (
        eb_x * ux
        + eb_y * uy
    )

    recovered_n_mm = (
        eb_x * vx
        + eb_y * vy
    )

    invariant_tolerance_mm = (
        _effective_distance_tolerance(
            tolerance,
            _point_norm_mm(
                point_b,
                name=f"{context}.B",
            ),
            _point_norm_mm(
                point_c,
                name=f"{context}.C",
            ),
            math.hypot(
                ex,
                ey,
            ),
            shield_length_mm,
            abs(longitudinal_offset_mm),
            abs(normal_offset_mm),
        )
    )

    if (
        abs(
            recovered_s_mm
            - longitudinal_offset_mm
        )
        > invariant_tolerance_mm
    ):
        raise RuntimeError(
            f"{context} propagated E violates "
            "longitudinal rigid-body invariant"
        )

    if (
        abs(
            recovered_n_mm
            - normal_offset_mm
        )
        > invariant_tolerance_mm
    ):
        raise RuntimeError(
            f"{context} propagated E violates "
            "normal rigid-body invariant"
        )

    return _calculated_point(
        ex,
        ey,
        point_role="shield_top_beam_pivot",
    )


def propagate_shield_top_beam_joint(
    *,
    linkage: LinkageGeometry,
    motion: MotionSegmentResult,
    tolerance: NumericalTolerance,
) -> ShieldTopBeamJointTrajectoryResult:
    """Propagate deterministic E coordinates across one W40 motion segment."""

    linkage_before = linkage.model_dump(
        mode="json"
    )

    motion_before = motion.model_dump(
        mode="json"
    )

    tolerance_before = tolerance.model_dump(
        mode="json"
    )

    attachment = _derive_attachment(
        linkage=linkage,
        tolerance=tolerance,
    )

    _validate_motion_reference(
        attachment=attachment,
        motion=motion,
        tolerance=tolerance,
    )

    output_samples: list[
        ShieldTopBeamJointTrajectorySample
    ] = []

    for motion_sample in motion.samples:
        closure_result = (
            motion_sample.closure_result
        )

        selected_pose = (
            closure_result.selected_pose
        )

        if selected_pose is not None:
            if closure_result.closure_state not in {
                "TWO_SOLUTIONS",
                "TANGENT",
            }:
                raise ValueError(
                    "selected motion pose requires "
                    "TWO_SOLUTIONS or TANGENT"
                )

            joint_center = (
                _propagate_joint_center(
                    point_b=(
                        selected_pose
                        .rear_link_shield
                    ),
                    point_c=(
                        selected_pose
                        .front_link_shield
                    ),
                    attachment=attachment,
                    tolerance=tolerance,
                    context=(
                        "motion sample "
                        f"{motion_sample.sample_index}"
                    ),
                )
            )

            selected_pose_available = True

        else:
            if closure_result.closure_state not in {
                "NO_SOLUTION",
                "DEGENERATE",
            }:
                raise ValueError(
                    "motion sample without selected pose "
                    "requires NO_SOLUTION or DEGENERATE"
                )

            joint_center = None
            selected_pose_available = False

        output_samples.append(
            ShieldTopBeamJointTrajectorySample(
                sample_index=(
                    motion_sample.sample_index
                ),
                requested_angle_deg=(
                    motion_sample
                    .requested_angle_deg
                    .model_copy(
                        deep=True
                    )
                ),
                closure_state=(
                    closure_result.closure_state
                ),
                selected_pose_available=(
                    selected_pose_available
                ),
                joint_center=joint_center,
            )
        )

    result = (
        ShieldTopBeamJointTrajectoryResult(
            attachment=attachment,
            direction=motion.direction,
            reference_branch=(
                motion.reference_branch
            ),
            reference_angle_deg=(
                motion.reference_angle_deg
                .model_copy(
                    deep=True
                )
            ),
            requested_angle_count=(
                motion.requested_angle_count
            ),
            samples=output_samples,
            termination=motion.termination,
        )
    )

    if (
        linkage.model_dump(
            mode="json"
        )
        != linkage_before
    ):
        raise RuntimeError(
            "W40-D5 propagation mutated LinkageGeometry"
        )

    if (
        motion.model_dump(
            mode="json"
        )
        != motion_before
    ):
        raise RuntimeError(
            "W40-D5 propagation mutated MotionSegmentResult"
        )

    if (
        tolerance.model_dump(
            mode="json"
        )
        != tolerance_before
    ):
        raise RuntimeError(
            "W40-D5 propagation mutated NumericalTolerance"
        )

    return result
