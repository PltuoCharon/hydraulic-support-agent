import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.linkage_geometry import (
    EngineeringPoint2D,
    LinkageGeometry,
    MillimetreParameter,
    NormalizedOriginPoint,
    serialize_linkage_geometry,
    validate_linkage_geometry,
)


ROOT = Path(__file__).resolve().parents[1]

EXAMPLE = (
    ROOT
    / "docs/evidence/w38/linkage_geometry_v1.example.json"
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


def test_d2_example_validates_against_d3_model():
    payload = json.loads(
        EXAMPLE.read_text(encoding="utf-8")
    )

    geometry = validate_linkage_geometry(payload)

    assert geometry.version == 1
    assert geometry.status == "PARTIAL"

    assert geometry.fixed_geometry.rear_link_base.x_mm == 0
    assert geometry.fixed_geometry.rear_link_base.y_mm == 0

    assert geometry.fixed_geometry.front_link_base is None
    assert geometry.reference_pose is None


def test_model_round_trip_preserves_contract():
    geometry = LinkageGeometry()

    payload = serialize_linkage_geometry(geometry)

    rebuilt = validate_linkage_geometry(payload)

    assert rebuilt == geometry
    assert payload["version"] == 1


def test_contract_rejects_wrong_version():
    with pytest.raises(ValidationError):
        validate_linkage_geometry({
            "version": 2,
        })


def test_contract_rejects_unknown_top_level_field():
    with pytest.raises(ValidationError):
        validate_linkage_geometry({
            "version": 1,
            "unexpected_field": 123,
        })


def test_normalized_origin_cannot_be_changed():
    with pytest.raises(ValidationError):
        NormalizedOriginPoint(
            x_mm=100,
            y_mm=0,
        )


def test_engineering_point_requires_parameter_trace():
    point = EngineeringPoint2D(
        x_mm=mm(500),
        y_mm=mm(250),
        point_role="front_link_base",
    )

    assert point.x_mm.value == 500
    assert point.x_mm.unit == "mm"

    assert point.x_mm.origin == "USER_INPUT"
    assert point.x_mm.evidence_status == "EVIDENCE_GAP"


def test_geometry_coordinate_rejects_wrong_unit():
    with pytest.raises(ValidationError):
        MillimetreParameter(
            value=500,
            unit="m",
            origin="USER_INPUT",
            evidence_status="EVIDENCE_GAP",
        )


def test_ai_coordinate_remains_ai_proposed():
    p = MillimetreParameter(
        value=600,
        origin="AI_PROPOSED",
        evidence_status="EVIDENCE_GAP",
    )

    assert p.origin == "AI_PROPOSED"
    assert p.evidence_status == "EVIDENCE_GAP"


def test_unknown_geometry_remains_none():
    geometry = LinkageGeometry()

    assert geometry.fixed_geometry.front_link_base is None
    assert geometry.reference_pose is None

    assert geometry.derived_geometry.rear_link_length_mm is None
    assert geometry.derived_geometry.front_link_length_mm is None

    assert (
        geometry.derived_geometry.shield_beam_effective_length_mm
        is None
    )


def test_example_preserves_80mm_as_verified_constraint():
    payload = json.loads(
        EXAMPLE.read_text(encoding="utf-8")
    )

    geometry = validate_linkage_geometry(payload)

    p = (
        geometry.design_boundaries
        .beam_tip_horizontal_displacement_limit_mm
    )

    assert p is not None
    assert p.value == 80
    assert p.unit == "mm"
    assert p.origin == "RETRIEVED"
    assert p.evidence_status == "VERIFIED"


def test_reference_pose_requires_real_coordinate_traces():
    point_a = EngineeringPoint2D(
        x_mm=mm(900),
        y_mm=mm(1200),
    )

    point_b = EngineeringPoint2D(
        x_mm=mm(500),
        y_mm=mm(1000),
    )

    geometry = LinkageGeometry.model_validate({
        "reference_pose": {
            "support_height_mm": mm(3000).model_dump(),
            "rear_link_shield": point_a.model_dump(),
            "front_link_shield": point_b.model_dump(),
        }
    })

    assert geometry.reference_pose is not None

    assert (
        geometry.reference_pose.support_height_mm.value
        == 3000
    )


def test_model_does_not_calculate_link_lengths():
    geometry = LinkageGeometry()

    assert geometry.derived_geometry.base_pivot_spacing_mm is None
    assert geometry.derived_geometry.rear_link_length_mm is None
    assert geometry.derived_geometry.front_link_length_mm is None


def test_top_beam_interface_is_separate_from_fixed_four_bar():
    fields = LinkageGeometry.model_fields

    assert "fixed_geometry" in fields
    assert "top_beam_interface" in fields

    fixed_fields = (
        geometry_fields()
    )

    assert "shield_top_beam_pivot" not in fixed_fields


def geometry_fields():
    geometry = LinkageGeometry()

    return type(geometry.fixed_geometry).model_fields


def test_serialization_preserves_missing_results():
    geometry = LinkageGeometry()

    payload = serialize_linkage_geometry(geometry)

    assert payload["pose_results"] == []
    assert payload["trajectory_results"] is None
    assert payload["validation_results"] is None


def test_model_contains_no_canopy_len_or_center_dist_field():
    fields = LinkageGeometry.model_fields

    assert "canopy_len" not in fields
    assert "center_dist" not in fields
    assert "top_beam_length_mm" not in fields
