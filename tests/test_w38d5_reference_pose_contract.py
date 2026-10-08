from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w38/W38D5_reference_pose_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized_text():
    """Normalize presentation-only whitespace in the Markdown contract."""

    return " ".join(text().split())


def test_d5_is_reference_pose_analysis_only():
    s = normalized_text()

    assert "explicitly supplied reference pose" in s
    assert "solving a pose from support height" in s
    assert "four-bar closure search" in s


def test_d5_requires_complete_fixed_base():
    s = text()

    assert "rear_link_base" in s
    assert "front_link_base" in s
    assert "shall not fabricate one" in s


def test_d5_freezes_three_direction_angles():
    s = text()

    for value in (
        "rear_link_angle_deg",
        "front_link_angle_deg",
        "shield_beam_angle_deg",
    ):
        assert value in s


def test_d5_uses_atan2_convention():
    s = normalized_text()

    assert "ordinary planar atan2 convention" in s
    assert "measured from the +X axis" in s


def test_d5_does_not_copy_ocr_angle_symbols():
    s = text()

    assert (
        "No OCR-derived alpha/beta symbol is silently mapped"
        in s
    )


def test_side_classification_is_frozen():
    s = text()

    for value in (
        "POSITIVE",
        "NEGATIVE",
        "ON_BASE_LINE",
    ):
        assert value in s


def test_neutral_assembly_signature_is_frozen():
    s = text()

    for value in (
        "SAME_SIDE",
        "OPPOSITE_SIDE",
        "DEGENERATE",
    ):
        assert value in s


def test_open_crossed_labels_are_intentionally_deferred():
    s = text()

    assert "does not rename these states to OPEN or CROSSED" in s


def test_zero_length_geometry_is_degenerate():
    s = text()

    assert "zero or near-zero length" in s
    assert "base pivot spacing" in s
    assert "rear-link length" in s
    assert "front-link length" in s
    assert "shield-beam effective linkage length" in s


def test_d5_preserves_provenance_boundary():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "creates no new Formula Registry ID" in s
    assert "creates no Calculation Record" in s


def test_support_height_is_not_used_as_solver_input():
    s = text()

    assert (
        "does not infer support height from joint coordinates"
        in s
    )

    assert (
        "does not use support_height_mm to solve or move"
        in s
    )


def test_d5_rejects_historical_geometry_completion():
    s = text()

    assert "canopy_len" in s
    assert "center_dist" in s
    assert "historical example dimensions" in s
