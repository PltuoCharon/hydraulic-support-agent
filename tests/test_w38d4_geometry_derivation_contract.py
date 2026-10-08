from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w38/W38D4_geometry_derivation_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_d4_is_limited_to_direct_geometry():
    s = text()

    assert "direct 2D Euclidean geometry" in s
    assert "four-bar closure solving" in s
    assert "trajectory generation" in s


def test_d4_freezes_four_allowed_outputs():
    s = text()

    for value in (
        "base_pivot_spacing_mm",
        "rear_link_length_mm",
        "front_link_length_mm",
        "shield_beam_effective_length_mm",
    ):
        assert value in s


def test_d4_rejects_legacy_geometry_inference():
    s = text()

    for value in (
        "canopy_len",
        "center_dist",
        "historical beam_length",
        "historical example dimensions",
    ):
        assert value in s


def test_d4_supports_partial_derivation():
    s = text()

    assert "D4 supports partial geometry" in s

    assert (
        "A missing unrelated coordinate shall not prevent calculation"
        in s
    )


def test_calculated_geometry_origin_is_frozen():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s


def test_d4_does_not_promote_input_evidence():
    s = text()

    assert "AI_PROPOSED -> VERIFIED" in s
    assert "EVIDENCE_GAP -> VERIFIED" in s


def test_d4_creates_no_trace_ids_yet():
    s = text()

    assert "creates no new Formula Registry ID" in s
    assert "creates no Calculation Record" in s

    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s


def test_d4_service_must_not_mutate_input():
    s = text()

    assert "return a new DerivedGeometry object" in s
    assert "shall not mutate the supplied LinkageGeometry" in s


def test_d4_rejects_non_finite_coordinates():
    s = text()

    assert "NaN" in s
    assert "positive/negative infinity" in s
    assert "reject non-finite coordinates" in s


def test_negative_coordinates_are_not_automatically_invalid():
    s = text()

    assert (
        "Negative coordinate values are not rejected"
        in s
    )


def test_top_beam_remains_outside_d4_core():
    s = text()

    assert "W38-D4 does not derive top-beam geometry" in s
    assert "beam-tip trajectory" in s
