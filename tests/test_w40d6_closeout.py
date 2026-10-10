from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w40/W40D6_closeout.md"


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_w40_closeout_records_final_executable_chain():
    s = normalized()

    assert "ordered B/C trajectory" in s
    assert "shield rigid-body pose" in s
    assert "deterministic E trajectory" in s

    assert (
        "rear-link-angle samples -> B/C trajectory "
        "-> shield rigid-body pose -> E trajectory"
        in s
    )


def test_w40_remains_angle_parameterized_not_height_trajectory():
    s = normalized()

    assert "rear_link_angle_deg" in s

    assert (
        "angle-parameterized sampled kinematic trajectory"
        in s
    )

    assert (
        "shall not be described as an operating-height trajectory"
        in s
    )


def test_w40_freezes_boundary_termination_semantics():
    s = normalized()

    assert "TANGENT_BOUNDARY" in s
    assert "NO_SOLUTION_BOUNDARY" in s
    assert "DEGENERATE_BOUNDARY" in s
    assert "BRANCH_AMBIGUOUS" in s

    assert (
        "never skips a failed angle and resumes later"
        in s
    )


def test_w40_records_explicit_e_capability():
    s = normalized()

    assert "shield_top_beam_pivot = E0" in s

    assert (
        "Ei = Bi + s_E * ui + n_E * vi"
        in s
    )

    assert (
        "E trajectory remains one-to-one aligned"
        in s
    )


def test_w40_does_not_infer_support_height():
    s = normalized()

    assert (
        "rear_link_angle_deg -> support_height_mm"
        in s
    )

    assert "B.y" in s
    assert "C.y" in s
    assert "E.y" in s

    assert (
        "not yet a complete operating-height-range trajectory"
        in s
    )


def test_w40_does_not_turn_100mm_height_rule_into_angle_spacing():
    s = normalized()

    assert "100 mm interval" in s
    assert "rear_link_angle_deg sweep spacing" in s

    assert (
        "cannot be converted into an angle-domain sampling interval"
        in s
    )


def test_w40_keeps_beam_tip_and_80mm_not_executable():
    s = normalized()

    assert "beam-tip trajectory = NOT EXECUTABLE" in s
    assert "80 mm validation = NOT EXECUTABLE" in s

    assert (
        "deterministic beam-tip trajectory"
        in s
    )

    assert (
        "complete operating-height range"
        in s
    )


def test_w40_preserves_provenance_boundary():
    s = normalized()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert (
        "does not promote missing engineering geometry to VERIFIED"
        in s
    )


def test_w40_freezes_scientific_claim_boundary():
    s = normalized()

    assert (
        "deterministic sampled branch-preserving four-bar "
        "kinematic trajectory"
        in s
    )

    assert (
        "a validated full-support operating-height trajectory"
        in s
    )

    assert "proof of MT/T 556 80 mm compliance" in s


def test_w41_handoff_uses_only_executable_objectives():
    s = normalized()

    assert (
        "mature-algorithm optimization baseline"
        in s
    )

    assert (
        "objectives and constraints that are deterministically executable"
        in s
    )

    assert (
        "Missing geometry shall not be fabricated"
        in s
    )
