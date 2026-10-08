import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w38/W38D2_linkage_geometry_contract.md"
)

EXAMPLE = (
    ROOT
    / "docs/evidence/w38/linkage_geometry_v1.example.json"
)


def doc_text():
    return DOC.read_text(encoding="utf-8")


def load_example():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_contract_identity():
    assert "hs.linkageGeometry.v1" in doc_text()


def test_contract_freezes_four_bar_members():
    s = doc_text()

    for value in (
        "base",
        "rear_link",
        "shield_beam",
        "front_link",
    ):
        assert value in s


def test_top_beam_joint_is_not_core_four_bar_joint():
    s = doc_text()

    assert (
        "top-beam / shield-beam joint is not one of these four canonical joints"
        in s
    )

    assert "top_beam_interface" in s


def test_coordinate_system_is_normalized():
    s = doc_text()

    assert "origin anchor: rear_link_base" in s
    assert "rear_link_base is normalized to (0, 0)" in s
    assert "+Y points vertically upward" in s


def test_contract_reuses_origin_and_evidence_semantics():
    s = doc_text()

    for value in (
        "RETRIEVED",
        "CALCULATED",
        "USER_INPUT",
        "AI_PROPOSED",
        "VERIFIED",
        "PARTIAL",
        "EVIDENCE_GAP",
        "NOT_APPLICABLE",
    ):
        assert value in s


def test_canonical_geometry_is_coordinate_first():
    s = doc_text()

    assert "coordinate-first canonical representation" in s

    assert (
        "derived geometry, not independent mandatory inputs"
        in s
    )


def test_historical_geometry_is_not_promoted():
    s = doc_text()

    assert "Historical canopy_len remains support_length_parameter_m only" in s
    assert "center_dist as linkage geometry" in s


def test_example_contains_no_fake_link_dimensions():
    data = load_example()

    derived = data["derived_geometry"]

    assert derived["rear_link_length_mm"] is None
    assert derived["front_link_length_mm"] is None
    assert derived["shield_beam_effective_length_mm"] is None


def test_example_normalizes_rear_base_pivot():
    data = load_example()

    point = data["fixed_geometry"]["rear_link_base"]

    assert point["x_mm"] == 0
    assert point["y_mm"] == 0

    assert point["coordinate_role"] == "NORMALIZED_ORIGIN"


def test_example_preserves_80mm_as_constraint():
    data = load_example()

    p = data["design_boundaries"][
        "beam_tip_horizontal_displacement_limit_mm"
    ]

    assert p["value"] == 80
    assert p["unit"] == "mm"
    assert p["origin"] == "RETRIEVED"
    assert p["evidence_status"] == "VERIFIED"


def test_unknown_geometry_remains_missing():
    data = load_example()

    assert data["fixed_geometry"]["front_link_base"] is None
    assert data["reference_pose"] is None

    assert (
        data["top_beam_interface"]["shield_top_beam_pivot"]
        is None
    )


def test_d3_remains_data_model_only():
    s = doc_text()

    assert "D3 shall still not implement" in s
    assert "four-bar closure" in s
    assert "pose solving" in s
