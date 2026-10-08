from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w38/W38D6_closeout.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_records_completed_w38_chain():
    s = text()

    for item in (
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
    ):
        assert item in s

    assert "complete four-bar kinematic solver" in s


def test_closeout_freezes_canonical_topology():
    s = text()

    for item in (
        "rear_link_base",
        "rear_link_shield",
        "front_link_shield",
        "front_link_base",
    ):
        assert item in s

    assert (
        "top-beam / shield-beam joint is not one of"
        in normalized()
    )


def test_closeout_preserves_provenance_rules():
    s = text()

    assert "AI_PROPOSED is not automatically VERIFIED" in s
    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s

    assert "No W38 Formula Registry ID was introduced" in s
    assert "No W38 Calculation Record was introduced" in s


def test_closeout_records_four_geometry_outputs():
    s = text()

    for item in (
        "base_pivot_spacing_mm",
        "rear_link_length_mm",
        "front_link_length_mm",
        "shield_beam_effective_length_mm",
    ):
        assert item in s


def test_closeout_records_reference_pose_outputs():
    s = text()

    for item in (
        "rear_link_angle_deg",
        "front_link_angle_deg",
        "shield_beam_angle_deg",
        "SAME_SIDE",
        "OPPOSITE_SIDE",
        "DEGENERATE",
    ):
        assert item in s


def test_closeout_keeps_solver_work_unimplemented():
    s = text()

    for item in (
        "four-bar closure solving",
        "continuous pose tracking",
        "beam-tip trajectory",
        "instantaneous-center trajectory",
        "mechanism optimization",
    ):
        assert item in s


def test_closeout_preserves_historical_field_boundary():
    s = text()

    assert "canopy_len" in s
    assert "center_dist" in s

    assert (
        "Historical canopy_len remains "
        "support_length_parameter_m only"
        in normalized()
    )

    assert (
        "center_dist remains an overall transverse support parameter"
        in normalized()
    )


def test_closeout_keeps_80mm_as_validation_boundary():
    s = text()

    assert "MT/T 556-1996" in s
    assert "beam_tip_horizontal_displacement_limit_mm = 80 mm" in s
    assert "It is not a linkage dimension" in s


def test_closeout_preserves_physical_validation_boundary():
    s = text()

    assert "physical mechanism validation" in s
    assert "manufacturing validation" in s
    assert "structural-strength validation" in s


def test_w39_requires_explicit_branch_selection_semantics():
    s = text()

    assert "zero / one / two mathematical solutions" in s
    assert "configuration-branch continuity rules" in s

    assert (
        "must not select a mathematical solution merely because "
        "it is the first solution returned by an algorithm"
        in normalized()
    )


def test_optimization_remains_after_deterministic_kinematics():
    s = text()

    assert "W39" in s
    assert "W40" in s
    assert "W41" in s

    assert (
        "No optimizer should be connected before deterministic "
        "pose and trajectory behavior are independently testable"
        in normalized()
    )
