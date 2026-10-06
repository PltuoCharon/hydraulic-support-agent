"""W37-D3 OverallSupportDesign v1 pure data model.

Boundary:
- data contract and validation only
- no database persistence
- no API routing
- no engineering calculation
- no AI parameter generation
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ParameterOrigin = Literal[
    "RETRIEVED",
    "CALCULATED",
    "USER_INPUT",
    "AI_PROPOSED",
]

EvidenceStatus = Literal[
    "VERIFIED",
    "PARTIAL",
    "EVIDENCE_GAP",
    "NOT_APPLICABLE",
]

ModuleStatus = Literal[
    "COMPLETE",
    "PARTIAL",
    "EVIDENCE_GAP",
    "NOT_IMPLEMENTED",
    "INTENTIONALLY_DEFERRED",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EngineeringParameter(StrictModel):
    """One engineering parameter plus its origin/evidence trace."""

    value: Any
    unit: str | None = None

    origin: ParameterOrigin
    evidence_status: EvidenceStatus

    source_text: str | None = None
    formula_ids: list[str] = Field(default_factory=list)
    calculation_record_ids: list[int] = Field(default_factory=list)
    note: str | None = None


class DesignMetadata(StrictModel):
    design_name: str = "untitled"
    design_id: str | None = None


class WorkingCondition(StrictModel):
    working_face_name: str | None = None

    coal_thickness_m: EngineeringParameter | None = None
    mining_height_m: EngineeringParameter | None = None
    dip_angle_deg: EngineeringParameter | None = None

    roof_condition: EngineeringParameter | None = None
    roof_class: EngineeringParameter | None = None
    floor_condition: EngineeringParameter | None = None
    gas_level: EngineeringParameter | None = None
    daily_output_t: EngineeringParameter | None = None

    initial_weighting_step_m: EngineeringParameter | None = None
    periodic_weighting_step_m: EngineeringParameter | None = None

    control_width_m: EngineeringParameter | None = None
    direct_roof_filling_coefficient: EngineeringParameter | None = None
    roof_unit_weight_kn_m3: EngineeringParameter | None = None

    k1: EngineeringParameter | None = None
    dynamic_load_factor_k: EngineeringParameter | None = None


class ReferenceSupport(StrictModel):
    support_id: int | None = None
    support_model: str | None = None

    support_type: EngineeringParameter | None = None
    working_resistance_kn: EngineeringParameter | None = None

    height_min_m: EngineeringParameter | None = None
    height_max_m: EngineeringParameter | None = None

    manufacturer: str | None = None

    center_distance_m: EngineeringParameter | None = None

    # Historical canopy_len maps only to this semantic.
    support_length_parameter_m: EngineeringParameter | None = None

    reference_intensity: EngineeringParameter | None = None
    reference_initial_force: EngineeringParameter | None = None
    weight_t: EngineeringParameter | None = None

    source_text: str | None = None
    data_status: str | None = None


class SupportRequirement(StrictModel):
    p1_mpa: EngineeringParameter | None = None
    p2_mpa: EngineeringParameter | None = None
    p3_mpa: EngineeringParameter | None = None

    required_support_intensity_mpa: EngineeringParameter | None = None
    governing_method: str | None = None

    control_area_m2: EngineeringParameter | None = None
    base_resistance_kn: EngineeringParameter | None = None
    required_working_resistance_kn: EngineeringParameter | None = None

    support_efficiency_ks: EngineeringParameter | None = None


class OverallParameters(StrictModel):
    support_type: EngineeringParameter | None = None

    design_working_resistance_kn: EngineeringParameter | None = None

    design_height_min_m: EngineeringParameter | None = None
    design_height_max_m: EngineeringParameter | None = None

    center_distance_m: EngineeringParameter | None = None
    design_support_intensity_mpa: EngineeringParameter | None = None


class ColumnDesign(StrictModel):
    status: ModuleStatus = "PARTIAL"

    d_calc_mm: EngineeringParameter | None = None
    d_std_mm: EngineeringParameter | None = None
    p_actual_kn: EngineeringParameter | None = None

    setting_ratio_pct: EngineeringParameter | None = None
    setting_ok: EngineeringParameter | None = None

    inputs: dict[str, Any] = Field(default_factory=dict)

    formula_ids: list[str] = Field(default_factory=list)
    calculation_record_ids: list[int] = Field(default_factory=list)

    source_text: str | None = None
    note: str | None = None


class PushJackDesign(StrictModel):
    status: ModuleStatus = "PARTIAL"

    push_required_kn: EngineeringParameter | None = None
    pressure_mpa: EngineeringParameter | None = None

    bore_calc_mm: EngineeringParameter | None = None
    bore_candidate_mm: EngineeringParameter | None = None

    push_actual_kn: EngineeringParameter | None = None
    push_ok: EngineeringParameter | None = None

    rod_mm: EngineeringParameter | None = None
    pull_required_kn: EngineeringParameter | None = None
    pull_actual_kn: EngineeringParameter | None = None
    pull_ok: EngineeringParameter | None = None

    stroke_mm: EngineeringParameter | None = None

    mt_t94_verified: bool = False

    formula_ids: list[str] = Field(default_factory=list)
    calculation_record_ids: list[int] = Field(default_factory=list)

    source_text: str | None = None
    note: str | None = None


class ReservedModule(StrictModel):
    status: ModuleStatus = "NOT_IMPLEMENTED"
    note: str | None = None


class HydraulicComponents(StrictModel):
    columns: ColumnDesign | None = None
    push_jack: PushJackDesign | None = None

    valve: ReservedModule = Field(
        default_factory=lambda: ReservedModule(
            status="NOT_IMPLEMENTED"
        )
    )
    pipeline: ReservedModule = Field(
        default_factory=lambda: ReservedModule(
            status="NOT_IMPLEMENTED"
        )
    )
    pump_station: ReservedModule = Field(
        default_factory=lambda: ReservedModule(
            status="NOT_IMPLEMENTED"
        )
    )


class LinkageState(StrictModel):
    status: ModuleStatus = "NOT_IMPLEMENTED"
    note: str | None = None


class StructureState(StrictModel):
    status: ModuleStatus = "NOT_IMPLEMENTED"
    note: str | None = None


class AnalysesState(StrictModel):
    status: ModuleStatus = "NOT_IMPLEMENTED"
    note: str | None = None


class DesignProvenance(StrictModel):
    source_texts: list[str] = Field(default_factory=list)
    formula_ids: list[str] = Field(default_factory=list)
    calculation_record_ids: list[int] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class OverallSupportDesign(StrictModel):
    """Canonical hs.overallDesign.v1 application model."""

    version: Literal[1] = 1

    metadata: DesignMetadata = Field(
        default_factory=DesignMetadata
    )

    working_condition: WorkingCondition = Field(
        default_factory=WorkingCondition
    )

    reference_support: ReferenceSupport = Field(
        default_factory=ReferenceSupport
    )

    support_requirement: SupportRequirement = Field(
        default_factory=SupportRequirement
    )

    overall_parameters: OverallParameters = Field(
        default_factory=OverallParameters
    )

    hydraulic_components: HydraulicComponents = Field(
        default_factory=HydraulicComponents
    )

    linkage: LinkageState = Field(
        default_factory=LinkageState
    )

    structure: StructureState = Field(
        default_factory=StructureState
    )

    analyses: AnalysesState = Field(
        default_factory=AnalysesState
    )

    provenance: DesignProvenance = Field(
        default_factory=DesignProvenance
    )

    status: ModuleStatus = "PARTIAL"


def validate_overall_design(
    payload: dict[str, Any],
) -> OverallSupportDesign:
    """Validate a Python payload against hs.overallDesign.v1."""

    return OverallSupportDesign.model_validate(payload)


def serialize_overall_design(
    design: OverallSupportDesign,
) -> dict[str, Any]:
    """Serialize hs.overallDesign.v1 without changing engineering semantics."""

    return design.model_dump(mode="json")
