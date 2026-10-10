from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w40/W40D2_closeout.md"


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_records_all_motion_model_types():
    s = normalized()

    for item in (
        "MotionDirection",
        "MotionTermination",
        "MotionSweepInput",
        "MotionSample",
        "MotionSweepProvenance",
        "MotionSegmentResult",
    ):
        assert item in s


def test_closeout_freezes_reference_branch_and_angle():
    s = normalized()

    assert "reference_task.reference_branch = POSITIVE" in s
    assert "reference_task.reference_branch = NEGATIVE" in s

    assert (
        "first requested angle shall equal: "
        "reference_task.rear_link_angle_deg"
        in s
    )


def test_closeout_freezes_branch_continuity():
    s = normalized()

    assert (
        "A POSITIVE MotionSegmentResult cannot contain "
        "a selected NEGATIVE"
        in s
    )

    assert (
        "A NEGATIVE MotionSegmentResult cannot contain "
        "a selected POSITIVE"
        in s
    )

    assert (
        "TWO_SOLUTIONS + BRANCH_AMBIGUOUS is invalid"
        in s
    )


def test_closeout_freezes_terminal_boundaries():
    s = normalized()

    assert "TANGENT_BOUNDARY" in s
    assert "NO_SOLUTION_BOUNDARY" in s
    assert "DEGENERATE_BOUNDARY" in s

    assert (
        "No later sample may exist in the same segment"
        in s
    )


def test_closeout_prevents_gap_and_resume():
    s = normalized()

    assert "0, 1, 2, ..., n - 1" in s

    assert (
        "Gap-and-resume is therefore invalid at the model layer"
        in s
    )


def test_closeout_preserves_w39_candidates_and_provenance():
    s = normalized()

    assert (
        "retain both: POSITIVE and: NEGATIVE mathematical candidates"
        in s
    )

    assert "W40_BRANCH_PRESERVING_ANGLE_SWEEP" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s


def test_closeout_does_not_fake_support_height_or_top_beam():
    s = normalized()

    assert "support_height_mm" in s
    assert "top_beam_pose" in s
    assert "beam_tip_trajectory" in s

    assert (
        "No placeholder geometry is fabricated in W40-D2"
        in s
    )


def test_closeout_freezes_d3_service_boundary():
    s = normalized()

    assert "sweep_rear_link_angles(...)" in s

    assert (
        "stop at the first TANGENT, NO_SOLUTION, "
        "or DEGENERATE boundary"
        in s
    )

    assert "never gap and resume" in s

    assert (
        "shall not implement support-height solving"
        in s
    )
