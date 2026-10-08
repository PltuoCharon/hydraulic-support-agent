"""W38-D4 deterministic linkage geometry derivation.

Boundary:
- pure 2D Euclidean geometry only
- no database access
- no API routing
- no four-bar closure solving
- no pose solving
- no trajectory generation
- no optimization
"""

from __future__ import annotations

import math
from typing import TypeAlias

from app.models.linkage_geometry import (
    DerivedGeometry,
    EngineeringPoint2D,
    LinkageGeometry,
    MillimetreParameter,
    NormalizedOriginPoint,
)


Point2D: TypeAlias = EngineeringPoint2D | NormalizedOriginPoint


def _coordinate_value(value: object) -> float:
    """Extract one numeric coordinate from either point representation."""

    if hasattr(value, "value"):
        value = getattr(value, "value")

    result = float(value)

    if not math.isfinite(result):
        raise ValueError(
            "linkage geometry coordinates must be finite"
        )

    return result


def _xy(point: Point2D) -> tuple[float, float]:
    """Return finite x/y coordinates in millimetres."""

    return (
        _coordinate_value(point.x_mm),
        _coordinate_value(point.y_mm),
    )


def _distance_mm(
    point_a: Point2D,
    point_b: Point2D,
) -> float:
    """Deterministic planar Euclidean distance without rounding."""

    ax, ay = _xy(point_a)
    bx, by = _xy(point_b)

    return math.hypot(
        bx - ax,
        by - ay,
    )


def _calculated_length(
    value_mm: float,
    *,
    note: str,
) -> MillimetreParameter:
    """Wrap one D4-derived length with frozen provenance semantics."""

    if not math.isfinite(value_mm):
        raise ValueError(
            "derived linkage geometry must be finite"
        )

    return MillimetreParameter(
        value=value_mm,
        origin="CALCULATED",
        evidence_status="PARTIAL",
        source_text="W38-D4 deterministic 2D geometry derivation",
        formula_ids=[],
        calculation_record_ids=[],
        note=note,
    )


def derive_geometry(
    linkage: LinkageGeometry,
) -> DerivedGeometry:
    """Derive all currently available canonical linkage lengths.

    Missing inputs produce missing outputs for only the dependent quantity.
    The supplied LinkageGeometry object is not mutated.
    """

    result = DerivedGeometry()

    rear_base = linkage.fixed_geometry.rear_link_base
    front_base = linkage.fixed_geometry.front_link_base
    pose = linkage.reference_pose

    if front_base is not None:
        result.base_pivot_spacing_mm = _calculated_length(
            _distance_mm(
                rear_base,
                front_base,
            ),
            note=(
                "distance between rear_link_base and "
                "front_link_base"
            ),
        )

    if pose is not None:
        result.rear_link_length_mm = _calculated_length(
            _distance_mm(
                rear_base,
                pose.rear_link_shield,
            ),
            note=(
                "distance between rear_link_base and "
                "rear_link_shield"
            ),
        )

        result.shield_beam_effective_length_mm = (
            _calculated_length(
                _distance_mm(
                    pose.rear_link_shield,
                    pose.front_link_shield,
                ),
                note=(
                    "effective linkage distance between "
                    "rear_link_shield and front_link_shield"
                ),
            )
        )

        if front_base is not None:
            result.front_link_length_mm = _calculated_length(
                _distance_mm(
                    front_base,
                    pose.front_link_shield,
                ),
                note=(
                    "distance between front_link_base and "
                    "front_link_shield"
                ),
            )

    return result
