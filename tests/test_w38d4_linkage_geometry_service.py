import math

import pytest

from app.models.linkage_geometry import (
    EngineeringPoint2D,
    LinkageGeometry,
    MillimetreParameter,
    ReferencePose,
)
from app.services.linkage_geometry import derive_geometry


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


def point(
    x,
    y,
    *,
    origin="USER_INPUT",
    evidence_status="EVIDENCE_GAP",
):
    return EngineeringPoint2D(
        x_mm=mm(
            x,
            origin=origin,
            evidence_status=evidence_status,
        ),
        y_mm=mm(
            y,
            origin=origin,
            evidence_status=evidence_status,
        ),
    )


def test_empty_geometry_derives_nothing():
    linkage = LinkageGeometry()

    result = derive_geometry(linkage)

    assert result.base_pivot_spacing_mm is None
    assert result.rear_link_length_mm is None
    assert result.front_link_length_mm is None

    assert (
        result.shield_beam_effective_length_mm
        is None
    )


def test_base_spacing_uses_euclidean_distance():
    linkage = LinkageGeometry()

    linkage.fixed_geometry.front_link_base = point(
        300,
        400,
    )

    result = derive_geometry(linkage)

    p = result.base_pivot_spacing_mm

    assert p is not None
    assert p.value == pytest.approx(500.0)
    assert p.unit == "mm"


def test_reference_pose_derives_rear_and_shield_lengths():
    linkage = LinkageGeometry(
        reference_pose=ReferencePose(
            support_height_mm=mm(3000),
            rear_link_shield=point(300, 400),
            front_link_shield=point(900, 1200),
        )
    )

    result = derive_geometry(linkage)

    assert result.rear_link_length_mm is not None
    assert (
        result.rear_link_length_mm.value
        == pytest.approx(500.0)
    )

    assert (
        result.shield_beam_effective_length_mm
        is not None
    )

    assert (
        result.shield_beam_effective_length_mm.value
        == pytest.approx(1000.0)
    )


def test_full_reference_geometry_derives_all_four_lengths():
    linkage = LinkageGeometry(
        reference_pose=ReferencePose(
            support_height_mm=mm(3000),
            rear_link_shield=point(300, 400),
            front_link_shield=point(900, 1200),
        )
    )

    linkage.fixed_geometry.front_link_base = point(
        900,
        400,
    )

    result = derive_geometry(linkage)

    assert (
        result.base_pivot_spacing_mm.value
        == pytest.approx(
            math.hypot(900, 400)
        )
    )

    assert (
        result.rear_link_length_mm.value
        == pytest.approx(500.0)
    )

    assert (
        result.front_link_length_mm.value
        == pytest.approx(800.0)
    )

    assert (
        result.shield_beam_effective_length_mm.value
        == pytest.approx(1000.0)
    )


def test_partial_geometry_does_not_block_available_results():
    linkage = LinkageGeometry(
        reference_pose=ReferencePose(
            support_height_mm=mm(3000),
            rear_link_shield=point(300, 400),
            front_link_shield=point(900, 1200),
        )
    )

    result = derive_geometry(linkage)

    assert result.base_pivot_spacing_mm is None
    assert result.front_link_length_mm is None

    assert result.rear_link_length_mm is not None

    assert (
        result.shield_beam_effective_length_mm
        is not None
    )


def test_calculated_lengths_use_frozen_provenance():
    linkage = LinkageGeometry()

    linkage.fixed_geometry.front_link_base = point(
        300,
        400,
        origin="AI_PROPOSED",
        evidence_status="EVIDENCE_GAP",
    )

    result = derive_geometry(linkage)

    p = result.base_pivot_spacing_mm

    assert p is not None
    assert p.origin == "CALCULATED"
    assert p.evidence_status == "PARTIAL"

    assert p.formula_ids == []
    assert p.calculation_record_ids == []


def test_ai_input_is_not_promoted_to_verified():
    linkage = LinkageGeometry()

    linkage.fixed_geometry.front_link_base = point(
        300,
        400,
        origin="AI_PROPOSED",
        evidence_status="EVIDENCE_GAP",
    )

    before = (
        linkage.fixed_geometry
        .front_link_base
        .x_mm
        .model_dump()
    )

    derive_geometry(linkage)

    after = (
        linkage.fixed_geometry
        .front_link_base
        .x_mm
        .model_dump()
    )

    assert before == after

    assert after["origin"] == "AI_PROPOSED"
    assert after["evidence_status"] == "EVIDENCE_GAP"


def test_service_does_not_mutate_existing_derived_geometry():
    linkage = LinkageGeometry()

    linkage.fixed_geometry.front_link_base = point(
        300,
        400,
    )

    linkage.derived_geometry.base_pivot_spacing_mm = mm(
        999,
        origin="USER_INPUT",
    )

    derive_geometry(linkage)

    assert (
        linkage.derived_geometry
        .base_pivot_spacing_mm
        .value
        == 999
    )


def test_negative_coordinates_are_valid():
    linkage = LinkageGeometry()

    linkage.fixed_geometry.front_link_base = point(
        -300,
        -400,
    )

    result = derive_geometry(linkage)

    assert (
        result.base_pivot_spacing_mm.value
        == pytest.approx(500.0)
    )


@pytest.mark.parametrize(
    "bad_value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_coordinates_are_rejected(bad_value):
    linkage = LinkageGeometry()

    linkage.fixed_geometry.front_link_base = point(
        bad_value,
        100,
    )

    with pytest.raises(
        ValueError,
        match="coordinates must be finite",
    ):
        derive_geometry(linkage)


def test_no_rounding_is_applied_inside_geometry_core():
    linkage = LinkageGeometry()

    linkage.fixed_geometry.front_link_base = point(
        1,
        1,
    )

    result = derive_geometry(linkage)

    assert result.base_pivot_spacing_mm is not None

    assert (
        result.base_pivot_spacing_mm.value
        == pytest.approx(math.sqrt(2))
    )

    assert (
        result.base_pivot_spacing_mm.value
        != round(math.sqrt(2), 2)
    )


def test_d4_implementation_document_preserves_boundary():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]

    text = (
        root
        / "docs/evidence/w38/W38D4_geometry_derivation.md"
    ).read_text(encoding="utf-8")

    assert "D4 is not a kinematic solver" in text
    assert "origin = CALCULATED" in text
    assert "evidence_status = PARTIAL" in text
    assert "returns a new DerivedGeometry object" in text
    assert "canopy_len" in text
    assert "center_dist" in text
    assert "does not constitute physical validation" in text
    assert "W38-D5" in text
