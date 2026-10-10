from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w40/W40D5_closeout.md"


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_records_complete_bce_chain():
    s = normalized()

    assert "ordered B/C trajectory" in s
    assert "shield rigid-body pose" in s
    assert "deterministic E trajectory" in s


def test_closeout_freezes_e_propagation_formula():
    s = normalized()

    assert "ui = (Ci - Bi) / Li" in s
    assert "vi = (-ui_y, ui_x)" in s

    assert (
        "Ei = Bi + s_E * ui + n_E * vi"
        in s
    )


def test_closeout_reuses_w39_scale_aware_tolerance():
    s = normalized()

    assert (
        "max( tolerance.absolute_mm, "
        "tolerance.relative * scale_mm )"
        in s
    )


def test_closeout_preserves_motion_boundary_alignment():
    s = normalized()

    assert "TANGENT_BOUNDARY" in s
    assert "NO_SOLUTION_BOUNDARY" in s
    assert "DEGENERATE_BOUNDARY" in s

    assert (
        "exactly one trajectory sample for every MotionSample"
        in s
    )


def test_closeout_preserves_calculated_partial_provenance():
    s = normalized()

    assert (
        "W40_SHIELD_TOP_BEAM_JOINT_RIGID_PROPAGATION"
        in s
    )

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s


def test_closeout_keeps_legacy_slot_unmodified():
    s = normalized()

    assert "LinkageGeometry.trajectory_results" in s

    assert (
        "TrajectoryResults.shield_top_beam_joint_trajectory"
        in s
    )

    assert (
        "does not directly populate"
        in s
    )


def test_closeout_keeps_beam_tip_and_height_out():
    s = normalized()

    assert "beam_tip_trajectory" in s
    assert "beam_tip_horizontal_displacement_mm" in s
    assert "support_height_mm" in s

    assert (
        "It is not yet an operating-height trajectory"
        in s
    )


def test_closeout_freezes_d6_not_executable_boundary():
    s = normalized()

    assert "beam-tip trajectory = NOT EXECUTABLE" in s
    assert "80 mm validation = NOT EXECUTABLE" in s

    assert (
        "Missing engineering geometry shall not be fabricated"
        in s
    )
