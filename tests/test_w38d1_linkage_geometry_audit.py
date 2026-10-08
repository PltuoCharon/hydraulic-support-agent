from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w38/W38D1_linkage_geometry_audit.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_d1_keeps_linkage_unimplemented():
    s = text()

    assert "NOT_IMPLEMENTED" in s
    assert "implement linkage formulas" in s


def test_d1_freezes_four_bar_topology():
    s = text()

    for value in (
        "front link",
        "rear link",
        "shield beam",
        "base",
    ):
        assert value in s


def test_d1_preserves_canopy_len_boundary():
    s = text()

    assert "support_length_parameter_m" in s
    assert "canopy_len = top-beam length" in s
    assert "canopy_len = Bc" in s


def test_d1_preserves_center_distance_boundary():
    s = text()

    assert "support center distance" in s
    assert "center_dist = linkage length" in s


def test_d1_does_not_promote_support_parts_to_geometry():
    s = text()

    assert "structural-composition knowledge" in s
    assert (
        "support_parts part existence = verified part geometry"
        in s
    )


def test_d1_rejects_example_dimensions_as_defaults():
    s = text()

    assert "reference/example results only" in s

    assert (
        "historical example dimensions = default geometry"
        in s
    )


def test_d1_records_missing_geometry():
    s = text()

    for value in (
        "base rear-link fixed pivot",
        "base front-link fixed pivot",
        "front-link effective length",
        "rear-link effective length",
        "linkage coordinate origin",
        "beam-tip reference point",
    ):
        assert value in s


def test_d1_freezes_d2_parameter_layers():
    s = text()

    for value in (
        "design_boundaries",
        "geometry_inputs",
        "derived_geometry",
        "pose_results",
        "trajectory_results",
        "validation_results",
    ):
        assert value in s


def test_d1_records_80mm_validation_constraint():
    s = text()

    assert "shall not exceed 80 mm" in s


def test_d1_preserves_no_fake_geometry_rule():
    s = text()

    assert (
        "No unverified geometry default shall be introduced"
        in s
    )
