"""W39-D3 deterministic numerical four-bar closure service.

Boundary:
- calculate point B from rear-link angle
- validate fixed-base consistency
- classify two-circle closure
- generate mathematical C candidates
- classify candidate branch sign
- do not perform engineering reference-branch selection
"""

from math import cos, hypot, radians, sin, sqrt

from app.models.linkage_closure import (
    ClosureCandidate,
    ClosureResult,
    ClosureSelectedPose,
    ClosureSolverInput,
    ClosureSolverProvenance,
    NumericalTolerance,
)
from app.models.linkage_geometry import (
    EngineeringPoint2D,
    MillimetreParameter,
)


SOURCE_TEXT = (
    "W39-D3 deterministic four-bar closure calculation"
)


def _effective_distance_tolerance(
    tolerance: NumericalTolerance,
    *distance_values_mm: float,
) -> float:
    """Return scale-aware numerical tolerance in millimetres."""

    scale_mm = max(
        (
            abs(value)
            for value in distance_values_mm
        ),
        default=0.0,
    )

    return max(
        tolerance.absolute_mm,
        tolerance.relative * scale_mm,
    )


def _calculated_mm(
    value: float,
) -> MillimetreParameter:
    """Create one provenance-aware calculated coordinate."""

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
    """Create one calculated W39-D3 engineering point."""

    return EngineeringPoint2D(
        x_mm=_calculated_mm(x_mm),
        y_mm=_calculated_mm(y_mm),
        point_role=point_role,
    )


def calculate_rear_link_shield(
    task: ClosureSolverInput,
) -> EngineeringPoint2D:
    """Calculate point B from A, AB and rear-link angle."""

    ax = float(task.rear_link_base.x_mm)
    ay = float(task.rear_link_base.y_mm)

    ab = task.rear_link_length_mm.value

    theta_rad = radians(
        task.rear_link_angle_deg.value
    )

    bx = ax + ab * cos(theta_rad)
    by = ay + ab * sin(theta_rad)

    return _calculated_point(
        bx,
        by,
        point_role="rear_link_shield",
    )


def _validate_fixed_base(
    task: ClosureSolverInput,
) -> None:
    """Validate that A-D coordinates agree with declared DA."""

    ax = float(task.rear_link_base.x_mm)
    ay = float(task.rear_link_base.y_mm)

    dx = task.front_link_base.x_mm.value
    dy = task.front_link_base.y_mm.value

    geometric_ad = hypot(
        dx - ax,
        dy - ay,
    )

    declared_ad = (
        task.base_pivot_spacing_mm.value
    )

    tolerance_mm = (
        _effective_distance_tolerance(
            task.tolerance,
            geometric_ad,
            declared_ad,
        )
    )

    mismatch_mm = abs(
        geometric_ad - declared_ad
    )

    if mismatch_mm > tolerance_mm:
        raise ValueError(
            "front_link_base coordinates are inconsistent "
            "with base_pivot_spacing_mm: "
            f"geometric_AD={geometric_ad!r} mm, "
            f"declared_AD={declared_ad!r} mm, "
            f"tolerance={tolerance_mm!r} mm"
        )


def _signed_distance_from_bd(
    point_b: EngineeringPoint2D,
    point_d: EngineeringPoint2D,
    point_c: EngineeringPoint2D,
) -> float:
    """Signed perpendicular distance of C from directed B->D."""

    bx = point_b.x_mm.value
    by = point_b.y_mm.value

    dx = point_d.x_mm.value
    dy = point_d.y_mm.value

    cx = point_c.x_mm.value
    cy = point_c.y_mm.value

    bdx = dx - bx
    bdy = dy - by

    q = hypot(
        bdx,
        bdy,
    )

    if q == 0:
        raise ValueError(
            "cannot classify branch when B and D coincide"
        )

    cross_mm2 = (
        bdx * (cy - by)
        - bdy * (cx - bx)
    )

    return cross_mm2 / q


def _no_solution_result(
    point_b: EngineeringPoint2D,
) -> ClosureResult:
    return ClosureResult(
        closure_state="NO_SOLUTION",
        selection_status="NOT_APPLICABLE",
        rear_link_shield=point_b,
        candidates=[],
        selected_pose=None,
        provenance=ClosureSolverProvenance(
            branch_resolution="NONE",
        ),
    )


def _degenerate_result(
    point_b: EngineeringPoint2D,
) -> ClosureResult:
    return ClosureResult(
        closure_state="DEGENERATE",
        selection_status="NOT_APPLICABLE",
        rear_link_shield=point_b,
        candidates=[],
        selected_pose=None,
        provenance=ClosureSolverProvenance(
            branch_resolution="NONE",
        ),
    )


def solve_closure_candidates(
    task: ClosureSolverInput,
) -> ClosureResult:
    """Solve mathematical four-bar closure candidates.

    TWO_SOLUTIONS remains BRANCH_AMBIGUOUS in W39-D3 even
    when task.reference_branch is non-null.
    """

    _validate_fixed_base(task)

    point_b = calculate_rear_link_shield(
        task
    )

    bx = point_b.x_mm.value
    by = point_b.y_mm.value

    point_d = task.front_link_base

    dx = point_d.x_mm.value
    dy = point_d.y_mm.value

    bd_x = dx - bx
    bd_y = dy - by

    q = hypot(
        bd_x,
        bd_y,
    )

    r1 = (
        task
        .shield_beam_effective_length_mm
        .value
    )

    r2 = (
        task
        .front_link_length_mm
        .value
    )

    sum_radii = r1 + r2
    radius_difference = abs(
        r1 - r2
    )

    tolerance_mm = (
        _effective_distance_tolerance(
            task.tolerance,
            q,
            r1,
            r2,
            sum_radii,
            radius_difference,
        )
    )

    # --------------------------------------------------------
    # Coincident centers
    # --------------------------------------------------------
    if q <= tolerance_mm:
        if (
            abs(r1 - r2)
            <= tolerance_mm
        ):
            return _degenerate_result(
                point_b
            )

        return _no_solution_result(
            point_b
        )

    # --------------------------------------------------------
    # Valid centers but no circle intersection
    # --------------------------------------------------------
    outer_gap = q - sum_radii

    if outer_gap > tolerance_mm:
        return _no_solution_result(
            point_b
        )

    inner_gap = (
        radius_difference - q
    )

    if inner_gap > tolerance_mm:
        return _no_solution_result(
            point_b
        )

    # --------------------------------------------------------
    # Tangency classification
    # --------------------------------------------------------
    external_tangent = (
        abs(q - sum_radii)
        <= tolerance_mm
    )

    internal_tangent = (
        abs(q - radius_difference)
        <= tolerance_mm
    )

    a = (
        r1 * r1
        - r2 * r2
        + q * q
    ) / (2.0 * q)

    px = bx + a * bd_x / q
    py = by + a * bd_y / q

    if (
        external_tangent
        or internal_tangent
    ):
        point_c = _calculated_point(
            px,
            py,
            point_role="front_link_shield",
        )

        candidate = ClosureCandidate(
            point_c=point_c,
            branch="TANGENT",
        )

        selected_pose = ClosureSelectedPose(
            rear_link_shield=point_b,
            front_link_shield=point_c,
            rear_link_angle_deg=(
                task.rear_link_angle_deg
            ),
            branch="TANGENT",
        )

        return ClosureResult(
            closure_state="TANGENT",
            selection_status="SELECTED",
            rear_link_shield=point_b,
            candidates=[
                candidate,
            ],
            selected_pose=selected_pose,
            provenance=ClosureSolverProvenance(
                branch_resolution=(
                    "TANGENT_UNIQUE"
                ),
            ),
        )

    # --------------------------------------------------------
    # Two distinct intersections
    # --------------------------------------------------------
    h_squared = (
        r1 * r1
        - a * a
    )

    if h_squared <= 0:
        raise ValueError(
            "circle classification expected TWO_SOLUTIONS "
            "but computed non-positive h^2"
        )

    h = sqrt(
        h_squared
    )

    positive_c = _calculated_point(
        px - h * bd_y / q,
        py + h * bd_x / q,
        point_role="front_link_shield",
    )

    negative_c = _calculated_point(
        px + h * bd_y / q,
        py - h * bd_x / q,
        point_role="front_link_shield",
    )

    positive_distance = (
        _signed_distance_from_bd(
            point_b,
            point_d,
            positive_c,
        )
    )

    negative_distance = (
        _signed_distance_from_bd(
            point_b,
            point_d,
            negative_c,
        )
    )

    branch_tolerance_mm = (
        _effective_distance_tolerance(
            task.tolerance,
            q,
            r1,
            r2,
            abs(positive_distance),
            abs(negative_distance),
        )
    )

    if (
        positive_distance
        <= branch_tolerance_mm
    ):
        raise ValueError(
            "positive closure candidate is numerically "
            "indistinguishable from the B-D line"
        )

    if (
        negative_distance
        >= -branch_tolerance_mm
    ):
        raise ValueError(
            "negative closure candidate is numerically "
            "indistinguishable from the B-D line"
        )

    candidates = [
        ClosureCandidate(
            point_c=positive_c,
            branch="POSITIVE",
        ),
        ClosureCandidate(
            point_c=negative_c,
            branch="NEGATIVE",
        ),
    ]

    return ClosureResult(
        closure_state="TWO_SOLUTIONS",
        selection_status="BRANCH_AMBIGUOUS",
        rear_link_shield=point_b,
        candidates=candidates,
        selected_pose=None,
        provenance=ClosureSolverProvenance(
            branch_resolution="NONE",
        ),
    )
