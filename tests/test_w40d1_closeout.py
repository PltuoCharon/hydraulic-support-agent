from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w40/W40D1_closeout.md"


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_keeps_angle_as_motion_parameter():
    s = normalized()

    assert "rear_link_angle_deg" in s

    assert (
        "does not redefine support_height_mm"
        in s
    )


def test_closeout_freezes_non_degenerate_branch_seed():
    s = normalized()

    assert "POSITIVE" in s
    assert "NEGATIVE" in s

    assert (
        "A null reference branch does not seed"
        in s
    )

    assert (
        "W40 does not guess the branch"
        in s
    )


def test_closeout_freezes_branch_continuity():
    s = normalized()

    assert (
        "selected_pose.branch = frozen reference branch"
        in s
    )

    assert (
        "A POSITIVE trajectory shall not silently become NEGATIVE"
        in s
    )

    assert (
        "A NEGATIVE trajectory shall not silently become POSITIVE"
        in s
    )


def test_closeout_tangent_is_boundary_not_switch():
    s = normalized()

    assert "selected_pose.branch = TANGENT" in s
    assert "branch_resolution = TANGENT_UNIQUE" in s

    assert (
        "does not authorize automatic branch switching"
        in s
    )


def test_closeout_invalid_state_cannot_gap_and_resume():
    s = normalized()

    assert "NO_SOLUTION" in s
    assert "DEGENERATE" in s

    assert (
        "does not skip an invalid sample and resume"
        in s
    )


def test_closeout_does_not_fake_support_height():
    s = normalized()

    assert (
        "support_height_mm shall not be fabricated"
        in s
    )

    assert "B.y" in s
    assert "C.y" in s


def test_closeout_keeps_top_beam_gap_explicit():
    s = normalized()

    assert "shield_top_beam_pivot" in s
    assert "beam_tip_reference_point" in s
    assert "top-beam local coordinate frame" in s

    assert (
        "does not calculate a beam-tip trajectory"
        in s
    )


def test_closeout_keeps_80mm_validation_conditional():
    s = normalized()

    assert "shall not exceed 80 mm" in s

    assert (
        "It does not claim compliance"
        in s
    )

    assert (
        "deterministic top-beam / beam-tip propagation"
        in s
    )

    assert (
        "explicit operating-height-to-pose semantics"
        in s
    )
