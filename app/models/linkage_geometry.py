"""W38-D3 LinkageGeometry v1 pure data model.

Boundary:
- data contract and validation only
- no database persistence
- no API routing
- no four-bar closure calculation
- no pose solving
- no trajectory calculation
- no optimization
- no CAD
- no FEA
"""

from typing import Any, Literal

from pydantic import Field

from app.models.overall_design import (
    DesignProvenance,
    EngineeringParameter,
    ModuleStatus,
    StrictModel,
)


class NumericEngineeringParameter(EngineeringParameter):
    """Engineering parameter restricted to numeric values."""

    value: float


class MillimetreParameter(NumericEngineeringParameter):
    """Numeric engineering parameter expressed in millimetres."""

    unit: Literal["mm"] = "mm"


class DegreeParameter(NumericEngineeringParameter):
    """Numeric engineering parameter expressed in degrees."""

    unit: Literal["degree"] = "degree"


class CoordinateSystem(StrictModel):
    """Normalized longitudinal side-view coordinate convention."""

    plane: Literal["LONGITUDINAL_SIDE_VIEW_2D"] = (
        "LONGITUDINAL_SIDE_VIEW_2D"
    )

    origin_anchor: Literal["rear_link_base"] = "rear_link_base"

    x_positive: Literal["FRONT_COAL_WALL_SIDE"] = (
        "FRONT_COAL_WALL_SIDE"
    )

    y_positive: Literal["UP"] = "UP"

    linear_unit: Literal["mm"] = "mm"
    angle_unit: Literal["degree"] = "degree"


class NormalizedOriginPoint(StrictModel):
    """Coordinate-system anchor, not a measured engineering point."""

    x_mm: Literal[0] = 0
    y_mm: Literal[0] = 0

    coordinate_role: Literal["NORMALIZED_ORIGIN"] = (
        "NORMALIZED_ORIGIN"
    )


class EngineeringPoint2D(StrictModel):
    """One provenance-aware engineering point in normalized coordinates."""

    x_mm: MillimetreParameter
    y_mm: MillimetreParameter

    point_role: str | None = None
    note: str | None = None


class DesignBoundaries(StrictModel):
    """External design/validation boundaries for the mechanism."""

    operating_height_min_mm: MillimetreParameter | None = None
    operating_height_max_mm: MillimetreParameter | None = None

    beam_tip_horizontal_displacement_limit_mm: (
        MillimetreParameter | None
    ) = None


class FixedGeometry(StrictModel):
    """Fixed pivots of the four-bar mechanism."""

    rear_link_base: NormalizedOriginPoint = Field(
        default_factory=NormalizedOriginPoint
    )

    front_link_base: EngineeringPoint2D | None = None


class ReferencePose(StrictModel):
    """One explicit physical reference configuration."""

    support_height_mm: MillimetreParameter

    rear_link_shield: EngineeringPoint2D
    front_link_shield: EngineeringPoint2D

    note: str | None = None


class DerivedGeometry(StrictModel):
    """Geometry that will later be deterministically derived."""

    base_pivot_spacing_mm: MillimetreParameter | None = None

    rear_link_length_mm: MillimetreParameter | None = None
    front_link_length_mm: MillimetreParameter | None = None

    shield_beam_effective_length_mm: (
        MillimetreParameter | None
    ) = None


class TopBeamInterface(StrictModel):
    """Geometry outside the canonical four-bar closure."""

    shield_top_beam_pivot: EngineeringPoint2D | None = None
    beam_tip_reference_point: EngineeringPoint2D | None = None


class PoseResult(StrictModel):
    """Reserved deterministic kinematic pose result."""

    support_height_mm: MillimetreParameter

    rear_link_shield: EngineeringPoint2D
    front_link_shield: EngineeringPoint2D

    rear_link_angle_deg: DegreeParameter | None = None
    front_link_angle_deg: DegreeParameter | None = None
    shield_beam_angle_deg: DegreeParameter | None = None

    top_beam_pose: dict[str, Any] | None = None

    note: str | None = None


class TrajectoryResults(StrictModel):
    """Reserved deterministic trajectory result container."""

    beam_tip_trajectory: list[EngineeringPoint2D] | None = None

    beam_tip_horizontal_displacement_mm: (
        MillimetreParameter | None
    ) = None

    shield_top_beam_joint_trajectory: (
        list[EngineeringPoint2D] | None
    ) = None

    instantaneous_center_trajectory: (
        list[EngineeringPoint2D] | None
    ) = None


class ValidationResults(StrictModel):
    """Reserved mechanism-validation result container."""

    geometry_closure_ok: bool | None = None
    operating_height_range_ok: bool | None = None
    beam_tip_displacement_ok: bool | None = None

    interference_status: str | None = None

    validation_notes: list[str] = Field(default_factory=list)


class LinkageGeometry(StrictModel):
    """Canonical hs.linkageGeometry.v1 application model."""

    version: Literal[1] = 1
    status: ModuleStatus = "PARTIAL"

    coordinate_system: CoordinateSystem = Field(
        default_factory=CoordinateSystem
    )

    design_boundaries: DesignBoundaries = Field(
        default_factory=DesignBoundaries
    )

    fixed_geometry: FixedGeometry = Field(
        default_factory=FixedGeometry
    )

    reference_pose: ReferencePose | None = None

    derived_geometry: DerivedGeometry = Field(
        default_factory=DerivedGeometry
    )

    top_beam_interface: TopBeamInterface = Field(
        default_factory=TopBeamInterface
    )

    pose_results: list[PoseResult] = Field(default_factory=list)

    trajectory_results: TrajectoryResults | None = None
    validation_results: ValidationResults | None = None

    provenance: DesignProvenance = Field(
        default_factory=DesignProvenance
    )


def validate_linkage_geometry(
    payload: dict[str, Any],
) -> LinkageGeometry:
    """Validate a Python payload against hs.linkageGeometry.v1."""

    return LinkageGeometry.model_validate(payload)


def serialize_linkage_geometry(
    geometry: LinkageGeometry,
) -> dict[str, Any]:
    """Serialize hs.linkageGeometry.v1 to a JSON-compatible dict."""

    return geometry.model_dump(mode="json")


SideClassification = Literal[
    "POSITIVE",
    "NEGATIVE",
    "ON_BASE_LINE",
]


AssemblySideSignature = Literal[
    "SAME_SIDE",
    "OPPOSITE_SIDE",
    "DEGENERATE",
]


class ReferencePoseAnalysis(StrictModel):
    """W38-D5 deterministic analysis of one explicit reference pose."""

    rear_link_angle_deg: DegreeParameter | None = None
    front_link_angle_deg: DegreeParameter | None = None
    shield_beam_angle_deg: DegreeParameter | None = None

    rear_link_shield_side: SideClassification
    front_link_shield_side: SideClassification

    assembly_side_signature: AssemblySideSignature

    geometry_degenerate: bool = False

    degeneracy_reasons: list[str] = Field(
        default_factory=list
    )

    note: str | None = None
