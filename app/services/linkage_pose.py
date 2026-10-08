"""W38-D5 deterministic reference-pose analysis.

Boundary:
- analyzes only an explicit canonical reference pose
- no pose solving from support height
- no four-bar closure search
- no trajectory generation
- no optimization
"""

from __future__ import annotations

import math
from typing import TypeAlias

from app.models.linkage_geometry import (
    AssemblySideSignature,
    DegreeParameter,
    EngineeringPoint2D,
    LinkageGeometry,
    NormalizedOriginPoint,
    ReferencePoseAnalysis,
    SideClassification,
)
from app.services.linkage_geometry import derive_geometry


Point2D: TypeAlias = (
    EngineeringPoint2D
    | NormalizedOriginPoint
)


NUMERICAL_TOLERANCE_MM = 1e-9


def _coordinate_value(value: object) -> float:
    """Extract one finite numeric coordinate."""

    if hasattr(value, "value"):
        value = getattr(value, "value")

    result = float(value)

    if not math.isfinite(result):
        raise ValueError(
            "reference-pose coordinates must be finite"
        )

    return result


def _xy(
    point: Point2D,
) -> tuple[float, float]:
    return (
        _coordinate_value(point.x_mm),
        _coordinate_value(point.y_mm),
    )


def _vector(
    point_a: Point2D,
    point_b: Point2D,
) -> tuple[float, float]:
    ax, ay = _xy(point_a)
    bx, by = _xy(point_b)

    return (
        bx - ax,
        by - ay,
    )


def _length_mm(
    point_a: Point2D,
    point_b: Point2D,
) -> float:
    dx, dy = _vector(
        point_a,
        point_b,
    )

    return math.hypot(dx, dy)


def _calculated_angle(
    point_a: Point2D,
    point_b: Point2D,
    *,
    note: str,
) -> DegreeParameter | None:
    """Return atan2 direction angle unless the segment is degenerate."""

    dx, dy = _vector(
        point_a,
        point_b,
    )

    length = math.hypot(dx, dy)

    if length <= NUMERICAL_TOLERANCE_MM:
        return None

    angle = math.degrees(
        math.atan2(
            dy,
            dx,
        )
    )

    return DegreeParameter(
        value=angle,
        origin="CALCULATED",
        evidence_status="PARTIAL",
        source_text=(
            "W38-D5 deterministic reference-pose analysis"
        ),
        formula_ids=[],
        calculation_record_ids=[],
        note=note,
    )


def _side_of_base(
    point: EngineeringPoint2D,
    *,
    rear_base: NormalizedOriginPoint,
    front_base: EngineeringPoint2D,
) -> SideClassification:
    """Classify one point relative to the directed fixed-base line."""

    bx, by = _vector(
        rear_base,
        front_base,
    )

    base_length = math.hypot(
        bx,
        by,
    )

    if base_length <= NUMERICAL_TOLERANCE_MM:
        return "ON_BASE_LINE"

    px, py = _vector(
        rear_base,
        point,
    )

    cross = (
        bx * py
        - by * px
    )

    signed_distance = (
        cross
        / base_length
    )

    if (
        abs(signed_distance)
        <= NUMERICAL_TOLERANCE_MM
    ):
        return "ON_BASE_LINE"

    if signed_distance > 0:
        return "POSITIVE"

    return "NEGATIVE"


def _assembly_signature(
    *,
    rear_side: SideClassification,
    front_side: SideClassification,
    segment_degenerate: bool,
) -> AssemblySideSignature:
    if segment_degenerate:
        return "DEGENERATE"

    if (
        rear_side == "ON_BASE_LINE"
        or front_side == "ON_BASE_LINE"
    ):
        return "DEGENERATE"

    if rear_side == front_side:
        return "SAME_SIDE"

    return "OPPOSITE_SIDE"


def analyze_reference_pose(
    linkage: LinkageGeometry,
) -> ReferencePoseAnalysis:
    """Analyze one explicit canonical reference pose.

    The supplied LinkageGeometry object is not mutated.
    """

    front_base = (
        linkage.fixed_geometry
        .front_link_base
    )

    if front_base is None:
        raise ValueError(
            "front_link_base is required "
            "for reference-pose analysis"
        )

    pose = linkage.reference_pose

    if pose is None:
        raise ValueError(
            "reference_pose is required "
            "for reference-pose analysis"
        )

    rear_base = (
        linkage.fixed_geometry
        .rear_link_base
    )

    # Validate every canonical coordinate before analysis.
    for point in (
        rear_base,
        front_base,
        pose.rear_link_shield,
        pose.front_link_shield,
    ):
        _xy(point)

    derived = derive_geometry(linkage)

    lengths = {
        "base_pivot_spacing": (
            derived.base_pivot_spacing_mm
        ),
        "rear_link": (
            derived.rear_link_length_mm
        ),
        "front_link": (
            derived.front_link_length_mm
        ),
        "shield_beam": (
            derived.shield_beam_effective_length_mm
        ),
    }

    degeneracy_reasons: list[str] = []

    for name, parameter in lengths.items():
        if parameter is None:
            degeneracy_reasons.append(
                f"{name}_missing"
            )
            continue

        if (
            float(parameter.value)
            <= NUMERICAL_TOLERANCE_MM
        ):
            degeneracy_reasons.append(
                f"{name}_near_zero"
            )

    rear_side = _side_of_base(
        pose.rear_link_shield,
        rear_base=rear_base,
        front_base=front_base,
    )

    front_side = _side_of_base(
        pose.front_link_shield,
        rear_base=rear_base,
        front_base=front_base,
    )

    if (
        rear_side
        == "ON_BASE_LINE"
    ):
        degeneracy_reasons.append(
            "rear_link_shield_on_base_line"
        )

    if (
        front_side
        == "ON_BASE_LINE"
    ):
        degeneracy_reasons.append(
            "front_link_shield_on_base_line"
        )

    # Preserve first occurrence while removing duplicates.
    degeneracy_reasons = list(
        dict.fromkeys(
            degeneracy_reasons
        )
    )

    geometry_degenerate = bool(
        degeneracy_reasons
    )

    signature = _assembly_signature(
        rear_side=rear_side,
        front_side=front_side,
        segment_degenerate=geometry_degenerate,
    )

    return ReferencePoseAnalysis(
        rear_link_angle_deg=_calculated_angle(
            rear_base,
            pose.rear_link_shield,
            note=(
                "direction from rear_link_base "
                "to rear_link_shield"
            ),
        ),
        front_link_angle_deg=_calculated_angle(
            front_base,
            pose.front_link_shield,
            note=(
                "direction from front_link_base "
                "to front_link_shield"
            ),
        ),
        shield_beam_angle_deg=_calculated_angle(
            pose.rear_link_shield,
            pose.front_link_shield,
            note=(
                "direction from rear_link_shield "
                "to front_link_shield"
            ),
        ),
        rear_link_shield_side=rear_side,
        front_link_shield_side=front_side,
        assembly_side_signature=signature,
        geometry_degenerate=geometry_degenerate,
        degeneracy_reasons=degeneracy_reasons,
        note=(
            "W38-D5 reference-pose analysis only; "
            "not a four-bar pose solver"
        ),
    )
