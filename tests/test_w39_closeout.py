from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w39/W39_closeout.md"


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_w39_closeout_records_all_five_days():
    s = normalized()

    for item in (
        "D1: closure semantics and benchmark boundary",
        "D2: strongly typed closure model",
        "D3: deterministic mathematical closure",
        "D4: engineering reference-branch resolution",
        "D5: W38-to-W39 integration",
    ):
        assert item in s


def test_w39_closeout_records_all_synthetic_states():
    s = text()

    for item in (
        "SM-001 -> TWO_SOLUTIONS",
        "SM-002 -> TANGENT",
        "SM-003 -> NO_SOLUTION",
        "SM-004 -> NO_SOLUTION",
        "SM-005 -> DEGENERATE",
        "SM-006 -> NO_SOLUTION",
    ):
        assert item in s


def test_w39_keeps_math_and_engineering_selection_separate():
    s = normalized()

    assert (
        "mathematical closure from: engineering branch selection"
        in s
    )

    assert "BRANCH_AMBIGUOUS" in s
    assert "POSITIVE" in s
    assert "NEGATIVE" in s


def test_w39_records_w38_to_w39_round_trip():
    s = normalized()

    assert "fresh derive_geometry(linkage)" in s
    assert "analyze_reference_pose(linkage)" in s
    assert "derive_reference_branch(...)" in s
    assert "reference-pose round-trip validation" in s


def test_w39_preserves_provenance_boundary():
    s = normalized()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert (
        "does not automatically produce VERIFIED engineering evidence"
        in s
    )


def test_w39_preserves_pushjack_traceability_boundary():
    s = normalized()

    assert "No F-JACK Formula Registry ID is created in W39" in s

    assert (
        "No PushJack Calculation Record is fabricated"
        in s
    )


def test_engineering_reference_is_still_pending():
    s = normalized()

    assert "ER-001 remains:" in s
    assert "ENGINEERING_REFERENCE NOT_SOLVER_READY" in s

    assert (
        "W39 does not fabricate missing engineering-reference geometry"
        in s
    )


def test_support_height_mapping_is_not_claimed():
    s = normalized()

    assert "support-height-to-pose mapping" in s

    assert (
        "shall not claim support-height inversion until "
        "the geometric relationship"
        in s
    )


def test_w40_owns_continuous_kinematics():
    s = normalized()

    assert "continuous operating-height kinematics" in s
    assert "continuity-preserving branch tracking" in s
    assert "pivot trajectories" in s
    assert "beam-tip trajectory" in s
    assert "80 mm validation" in s

    assert (
        "shall not silently jump between POSITIVE and NEGATIVE branches"
        in s
    )


def test_optimization_remains_outside_w39():
    s = normalized()

    assert "GA, PSO and NSGA-II" in s

    assert (
        "Four-bar optimization does not belong to W39"
        in s
    )

    assert (
        "deterministic mechanism evaluator"
        in s
    )
