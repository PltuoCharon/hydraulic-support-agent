import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.overall_design import (
    EngineeringParameter,
    OverallSupportDesign,
    ReferenceSupport,
    serialize_overall_design,
    validate_overall_design,
)


ROOT = Path(__file__).resolve().parents[1]

EXAMPLE = (
    ROOT
    / "docs/evidence/w37/overall_design_v1.example.json"
)


def test_d2_example_validates_against_d3_model():
    payload = json.loads(
        EXAMPLE.read_text(encoding="utf-8")
    )

    design = validate_overall_design(payload)

    assert design.version == 1
    assert design.status == "PARTIAL"

    assert (
        design.hydraulic_components.valve.status
        == "NOT_IMPLEMENTED"
    )

    assert design.linkage.status == "NOT_IMPLEMENTED"
    assert design.structure.status == "NOT_IMPLEMENTED"
    assert design.analyses.status == "NOT_IMPLEMENTED"


def test_model_round_trip_preserves_contract():
    design = OverallSupportDesign()

    payload = serialize_overall_design(design)

    rebuilt = validate_overall_design(payload)

    assert rebuilt == design
    assert payload["version"] == 1


def test_contract_rejects_wrong_version():
    with pytest.raises(ValidationError):
        validate_overall_design({
            "version": 2,
        })


def test_contract_rejects_unknown_top_level_field():
    with pytest.raises(ValidationError):
        validate_overall_design({
            "version": 1,
            "unexpected_field": 123,
        })


def test_engineering_parameter_rejects_invalid_origin():
    with pytest.raises(ValidationError):
        EngineeringParameter(
            value=12000,
            unit="kN",
            origin="GUESSED",
            evidence_status="VERIFIED",
        )


def test_origin_and_evidence_status_remain_independent():
    p = EngineeringParameter(
        value=0.95,
        unit=None,
        origin="CALCULATED",
        evidence_status="EVIDENCE_GAP",
        note="calculation exists but evidence gap remains",
    )

    assert p.origin == "CALCULATED"
    assert p.evidence_status == "EVIDENCE_GAP"


def test_ai_proposed_parameter_is_preserved_as_ai_proposed():
    p = EngineeringParameter(
        value=5.2,
        unit="m",
        origin="AI_PROPOSED",
        evidence_status="EVIDENCE_GAP",
    )

    payload = p.model_dump(mode="json")

    assert payload["origin"] == "AI_PROPOSED"
    assert payload["evidence_status"] == "EVIDENCE_GAP"


def test_reference_support_uses_support_length_parameter_semantic():
    fields = ReferenceSupport.model_fields

    assert "support_length_parameter_m" in fields

    assert "control_width_m" not in fields
    assert "top_beam_length_m" not in fields


def test_reserved_modules_do_not_invent_engineering_values():
    design = OverallSupportDesign()

    assert (
        design.hydraulic_components.valve.status
        == "NOT_IMPLEMENTED"
    )
    assert (
        design.hydraulic_components.pipeline.status
        == "NOT_IMPLEMENTED"
    )
    assert (
        design.hydraulic_components.pump_station.status
        == "NOT_IMPLEMENTED"
    )


def test_parameter_trace_fields_are_available():
    p = EngineeringParameter(
        value=12500,
        unit="kN",
        origin="CALCULATED",
        evidence_status="VERIFIED",
        source_text="engineering calculation",
        formula_ids=["F-QN-007"],
        calculation_record_ids=[12],
    )

    assert p.formula_ids == ["F-QN-007"]
    assert p.calculation_record_ids == [12]


def test_d3_implementation_document_preserves_boundary():
    doc = (
        ROOT
        / "docs/evidence/w37/W37D3_overall_design_model.md"
    ).read_text(encoding="utf-8")

    assert "calculation-free" in doc
    assert "canopy_len is not Bc" in doc
    assert "Ks is not eta" in doc
    assert "AI_PROPOSED" in doc
    assert "W37-D4" in doc
