import math

import pytest

from app.models.linkage_geometry import (
    EngineeringPoint2D,
    LinkageGeometry,
    MillimetreParameter,
    ReferencePose,
)
from app.services.linkage_pose import (
    analyze_reference_pose,
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


def complete_linkage(
    *,
    height=3000,
    rear=(300, 400),
    front=(900, 1200),
    front_base=(1000, 0),
):
    linkage = LinkageGeometry(
        reference_pose=ReferencePose(
            support_height_mm=mm(height),
            rear_link_shield=point(*rear),
            front_link_shield=point(*front),
        )
    )

    linkage.fixed_geometry.front_link_base = (
        point(*front_base)
    )

    return linkage


def test_missing_front_base_is_rejected():
    linkage = LinkageGeometry(
        reference_pose=ReferencePose(
            support_height_mm=mm(3000),
            rear_link_shield=point(300, 400),
            front_link_shield=point(900, 1200),
        )
    )

    with pytest.raises(
        ValueError,
        match="front_link_base is required",
    ):
        analyze_reference_pose(linkage)


def test_missing_reference_pose_is_rejected():
    linkage = LinkageGeometry()

    linkage.fixed_geometry.front_link_base = (
        point(1000, 0)
    )

    with pytest.raises(
        ValueError,
        match="reference_pose is required",
    ):
        analyze_reference_pose(linkage)


def test_same_side_pose_calculates_three_angles():
    linkage = complete_linkage()

    result = analyze_reference_pose(linkage)

    assert (
        result.assembly_side_signature
        == "SAME_SIDE"
    )

    assert (
        result.rear_link_shield_side
        == "POSITIVE"
    )

    assert (
        result.front_link_shield_side
        == "POSITIVE"
    )

    assert result.geometry_degenerate is False
    assert result.degeneracy_reasons == []

    assert (
        result.rear_link_angle_deg.value
        == pytest.approx(
            math.degrees(
                math.atan2(400, 300)
            )
        )
    )

    assert (
        result.front_link_angle_deg.value
        == pytest.approx(
            math.degrees(
                math.atan2(1200, -100)
            )
        )
    )

    assert (
        result.shield_beam_angle_deg.value
        == pytest.approx(
            math.degrees(
                math.atan2(800, 600)
            )
        )
    )


def test_opposite_side_pose_is_classified_neutrally():
    linkage = complete_linkage(
        rear=(300, 400),
        front=(900, -400),
    )

    result = analyze_reference_pose(linkage)

    assert (
        result.rear_link_shield_side
        == "POSITIVE"
    )

    assert (
        result.front_link_shield_side
        == "NEGATIVE"
    )

    assert (
        result.assembly_side_signature
        == "OPPOSITE_SIDE"
    )

    assert result.geometry_degenerate is False


def test_moving_pivot_on_base_line_is_degenerate():
    linkage = complete_linkage(
        front=(900, 0),
    )

    result = analyze_reference_pose(linkage)

    assert (
        result.front_link_shield_side
        == "ON_BASE_LINE"
    )

    assert (
        result.assembly_side_signature
        == "DEGENERATE"
    )

    assert result.geometry_degenerate is True

    assert (
        "front_link_shield_on_base_line"
        in result.degeneracy_reasons
    )


def test_zero_base_spacing_is_degenerate():
    linkage = complete_linkage(
        front_base=(0, 0),
    )

    result = analyze_reference_pose(linkage)

    assert result.geometry_degenerate is True

    assert (
        result.assembly_side_signature
        == "DEGENERATE"
    )

    assert (
        "base_pivot_spacing_near_zero"
        in result.degeneracy_reasons
    )


def test_zero_rear_link_has_no_direction_angle():
    linkage = complete_linkage(
        rear=(0, 0),
    )

    result = analyze_reference_pose(linkage)

    assert result.geometry_degenerate is True

    assert result.rear_link_angle_deg is None

    assert (
        "rear_link_near_zero"
        in result.degeneracy_reasons
    )


def test_calculated_angles_use_frozen_provenance():
    linkage = complete_linkage()

    result = analyze_reference_pose(linkage)

    for parameter in (
        result.rear_link_angle_deg,
        result.front_link_angle_deg,
        result.shield_beam_angle_deg,
    ):
        assert parameter is not None
        assert parameter.unit == "degree"
        assert parameter.origin == "CALCULATED"
        assert parameter.evidence_status == "PARTIAL"
        assert parameter.formula_ids == []
        assert parameter.calculation_record_ids == []


def test_service_does_not_rewrite_input_provenance():
    linkage = complete_linkage()

    linkage.reference_pose.rear_link_shield.x_mm.origin = (
        "AI_PROPOSED"
    )

    before = linkage.model_dump(mode="json")

    analyze_reference_pose(linkage)

    after = linkage.model_dump(mode="json")

    assert before == after


def test_support_height_does_not_change_pose_analysis():
    a = complete_linkage(
        height=2500,
    )

    b = complete_linkage(
        height=5000,
    )

    result_a = analyze_reference_pose(a)
    result_b = analyze_reference_pose(b)

    assert (
        result_a.rear_link_angle_deg.value
        == pytest.approx(
            result_b.rear_link_angle_deg.value
        )
    )

    assert (
        result_a.assembly_side_signature
        == result_b.assembly_side_signature
    )


def test_top_beam_interface_does_not_affect_core_analysis():
    linkage = complete_linkage()

    baseline = analyze_reference_pose(linkage)

    linkage.top_beam_interface.shield_top_beam_pivot = (
        point(9999, -9999)
    )

    linkage.top_beam_interface.beam_tip_reference_point = (
        point(-7777, 8888)
    )

    changed = analyze_reference_pose(linkage)

    assert (
        baseline.model_dump(mode="json")
        == changed.model_dump(mode="json")
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
    linkage = complete_linkage()

    linkage.fixed_geometry.front_link_base = (
        point(
            bad_value,
            0,
        )
    )

    with pytest.raises(
        ValueError,
        match="coordinates must be finite",
    ):
        analyze_reference_pose(linkage)


def test_d5_implementation_document_preserves_boundary():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]

    text = (
        root
        / "docs/evidence/w38/W38D5_reference_pose_analysis.md"
    ).read_text(encoding="utf-8")

    normalized = " ".join(text.split())

    assert "not a four-bar pose solver" in text
    assert "ordinary planar atan2 convention" in normalized

    assert "SAME_SIDE" in text
    assert "OPPOSITE_SIDE" in text
    assert "DEGENERATE" in text

    assert "does not rename these states OPEN or CROSSED" in text

    assert "origin = CALCULATED" in text
    assert "evidence_status = PARTIAL" in text

    assert "canopy_len" in text
    assert "center_dist" in text

    assert "does not constitute physical validation" in text
    assert "W38-D6" in text
