"""W39-D5 W38-to-W39 linkage closure integration.

Boundary:
- consume one W38 LinkageGeometry reference configuration
- freshly derive canonical four-bar dimensions
- reuse W38 reference-pose angle analysis
- derive the W39 B->D reference branch
- build one strongly typed ClosureSolverInput
- reuse the existing W39 D3+D4 solver chain
- validate deterministic reference-pose round trip
- no support-height inversion
- no trajectory generation
- no optimization
"""

from __future__ import annotations

import math

from app.models.linkage_closure import (
    ClosureResult,
    ClosureSolverInput,
    NumericalTolerance,
)
from app.models.linkage_geometry import (
    EngineeringPoint2D,
    LinkageGeometry,
)
from app.services.linkage_closure import (
    _effective_distance_tolerance,
    derive_reference_branch,
    solve_closure,
)
from app.services.linkage_geometry import (
    derive_geometry,
)
from app.services.linkage_pose import (
    analyze_reference_pose,
)


def _finite_coordinate(
    value: float,
    *,
    name: str,
) -> float:
    """Return one finite coordinate value."""

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
    """Extract one finite engineering point."""

    return (
        _finite_coordinate(
            point.x_mm.value,
            name=f"{name}.x_mm",
        ),
        _finite_coordinate(
            point.y_mm.value,
            name=f"{name}.y_mm",
        ),
    )


def _point_error_mm(
    solved: EngineeringPoint2D,
    reference: EngineeringPoint2D,
    *,
    solved_name: str,
    reference_name: str,
) -> float:
    """Return planar Euclidean point error in millimetres."""

    sx, sy = _point_xy(
        solved,
        name=solved_name,
    )

    rx, ry = _point_xy(
        reference,
        name=reference_name,
    )

    return math.hypot(
        sx - rx,
        sy - ry,
    )


def _round_trip_tolerance_mm(
    task: ClosureSolverInput,
    *,
    reference_b: EngineeringPoint2D,
    reference_c: EngineeringPoint2D,
    solved_b: EngineeringPoint2D,
    solved_c: EngineeringPoint2D,
) -> float:
    """Reuse the W39 scale-aware distance-tolerance policy."""

    reference_b_x, reference_b_y = _point_xy(
        reference_b,
        name="reference_b",
    )

    reference_c_x, reference_c_y = _point_xy(
        reference_c,
        name="reference_c",
    )

    solved_b_x, solved_b_y = _point_xy(
        solved_b,
        name="solved_b",
    )

    solved_c_x, solved_c_y = _point_xy(
        solved_c,
        name="solved_c",
    )

    return _effective_distance_tolerance(
        task.tolerance,
        task.base_pivot_spacing_mm.value,
        task.rear_link_length_mm.value,
        task.shield_beam_effective_length_mm.value,
        task.front_link_length_mm.value,
        math.hypot(
            reference_b_x,
            reference_b_y,
        ),
        math.hypot(
            reference_c_x,
            reference_c_y,
        ),
        math.hypot(
            solved_b_x,
            solved_b_y,
        ),
        math.hypot(
            solved_c_x,
            solved_c_y,
        ),
    )


def build_closure_task_from_linkage(
    *,
    linkage: LinkageGeometry,
    tolerance: NumericalTolerance,
) -> ClosureSolverInput:
    """Build one W39 closure task from explicit W38 reference geometry."""

    before = linkage.model_dump(
        mode="json"
    )

    front_base = (
        linkage.fixed_geometry
        .front_link_base
    )

    if front_base is None:
        raise ValueError(
            "front_link_base is required "
            "for W39-D5 integration"
        )

    reference_pose = (
        linkage.reference_pose
    )

    if reference_pose is None:
        raise ValueError(
            "reference_pose is required "
            "for W39-D5 integration"
        )

    # Fresh W38 derivation is authoritative for this solve.
    derived = derive_geometry(
        linkage
    )

    required_dimensions = {
        "base_pivot_spacing_mm": (
            derived.base_pivot_spacing_mm
        ),
        "rear_link_length_mm": (
            derived.rear_link_length_mm
        ),
        "shield_beam_effective_length_mm": (
            derived.shield_beam_effective_length_mm
        ),
        "front_link_length_mm": (
            derived.front_link_length_mm
        ),
    }

    missing = [
        name
        for name, value
        in required_dimensions.items()
        if value is None
    ]

    if missing:
        raise ValueError(
            "fresh linkage geometry is incomplete: "
            + ", ".join(missing)
        )

    analysis = analyze_reference_pose(
        linkage
    )

    if analysis.geometry_degenerate:
        reasons = ", ".join(
            analysis.degeneracy_reasons
        )

        raise ValueError(
            "degenerate W38 reference geometry "
            "cannot be used as the W39-D5 "
            "engineering reference baseline"
            + (
                f": {reasons}"
                if reasons
                else ""
            )
        )

    rear_link_angle = (
        analysis.rear_link_angle_deg
    )

    if rear_link_angle is None:
        raise ValueError(
            "rear_link_angle_deg is required "
            "for W39-D5 integration"
        )

    reference_branch = (
        derive_reference_branch(
            reference_b=(
                reference_pose
                .rear_link_shield
            ),
            reference_c=(
                reference_pose
                .front_link_shield
            ),
            front_link_base=front_base,
            tolerance=tolerance,
        )
    )

    task = ClosureSolverInput(
        rear_link_base=(
            linkage.fixed_geometry
            .rear_link_base
            .model_copy(deep=True)
        ),
        front_link_base=(
            front_base.model_copy(
                deep=True
            )
        ),
        rear_link_length_mm=(
            derived.rear_link_length_mm
            .model_copy(deep=True)
        ),
        shield_beam_effective_length_mm=(
            derived
            .shield_beam_effective_length_mm
            .model_copy(deep=True)
        ),
        front_link_length_mm=(
            derived.front_link_length_mm
            .model_copy(deep=True)
        ),
        base_pivot_spacing_mm=(
            derived.base_pivot_spacing_mm
            .model_copy(deep=True)
        ),
        rear_link_angle_deg=(
            rear_link_angle.model_copy(
                deep=True
            )
        ),
        reference_branch=reference_branch,
        tolerance=tolerance.model_copy(
            deep=True
        ),
    )

    after = linkage.model_dump(
        mode="json"
    )

    if after != before:
        raise RuntimeError(
            "W39-D5 task construction mutated LinkageGeometry"
        )

    return task


def validate_reference_pose_round_trip(
    *,
    linkage: LinkageGeometry,
    task: ClosureSolverInput,
    result: ClosureResult,
) -> None:
    """Validate that solved B/C reproduce the explicit W38 reference pose."""

    reference_pose = (
        linkage.reference_pose
    )

    if reference_pose is None:
        raise ValueError(
            "reference_pose is required "
            "for round-trip validation"
        )

    if result.selected_pose is None:
        raise ValueError(
            "W39-D5 reference-pose round trip "
            "requires a unique selected pose"
        )

    if result.closure_state not in {
        "TWO_SOLUTIONS",
        "TANGENT",
    }:
        raise ValueError(
            "W39-D5 reference-pose round trip "
            "requires TWO_SOLUTIONS or TANGENT"
        )

    if (
        result.closure_state
        == "TWO_SOLUTIONS"
    ):
        if task.reference_branch is None:
            raise ValueError(
                "TWO_SOLUTIONS reference-pose round trip "
                "requires a non-null reference branch"
            )

        if (
            result.selected_pose.branch
            != task.reference_branch
        ):
            raise ValueError(
                "selected branch does not match "
                "ClosureSolverInput.reference_branch"
            )

        if (
            result.provenance.branch_resolution
            != "REFERENCE_POSE"
        ):
            raise ValueError(
                "TWO_SOLUTIONS reference-pose round trip "
                "requires REFERENCE_POSE resolution"
            )

    if result.closure_state == "TANGENT":
        if (
            result.selected_pose.branch
            != "TANGENT"
        ):
            raise ValueError(
                "TANGENT result must preserve "
                "the TANGENT selected branch"
            )

        if (
            result.provenance.branch_resolution
            != "TANGENT_UNIQUE"
        ):
            raise ValueError(
                "TANGENT reference-pose round trip "
                "requires TANGENT_UNIQUE resolution"
            )

    solved_b = (
        result.selected_pose
        .rear_link_shield
    )

    solved_c = (
        result.selected_pose
        .front_link_shield
    )

    reference_b = (
        reference_pose
        .rear_link_shield
    )

    reference_c = (
        reference_pose
        .front_link_shield
    )

    tolerance_mm = (
        _round_trip_tolerance_mm(
            task,
            reference_b=reference_b,
            reference_c=reference_c,
            solved_b=solved_b,
            solved_c=solved_c,
        )
    )

    b_error_mm = _point_error_mm(
        solved_b,
        reference_b,
        solved_name="solved_b",
        reference_name="reference_b",
    )

    c_error_mm = _point_error_mm(
        solved_c,
        reference_c,
        solved_name="solved_c",
        reference_name="reference_c",
    )

    if b_error_mm > tolerance_mm:
        raise ValueError(
            "rear_link_shield round-trip mismatch: "
            f"error={b_error_mm!r} mm, "
            f"tolerance={tolerance_mm!r} mm"
        )

    if c_error_mm > tolerance_mm:
        raise ValueError(
            "front_link_shield round-trip mismatch: "
            f"error={c_error_mm!r} mm, "
            f"tolerance={tolerance_mm!r} mm"
        )


def solve_linkage_reference_pose(
    *,
    linkage: LinkageGeometry,
    tolerance: NumericalTolerance,
) -> ClosureResult:
    """Run the complete W38 -> W39 reference-pose integration."""

    before = linkage.model_dump(
        mode="json"
    )

    task = build_closure_task_from_linkage(
        linkage=linkage,
        tolerance=tolerance,
    )

    result = solve_closure(
        task
    )

    validate_reference_pose_round_trip(
        linkage=linkage,
        task=task,
        result=result,
    )

    after = linkage.model_dump(
        mode="json"
    )

    if after != before:
        raise RuntimeError(
            "W39-D5 integrated solve mutated LinkageGeometry"
        )

    return result
