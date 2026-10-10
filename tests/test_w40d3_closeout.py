from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w40/W40D3_closeout.md"


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_records_execution_chain():
    s = normalized()

    assert "MotionSweepInput" in s
    assert "ClosureSolverInput.model_validate(...)" in s
    assert "solve_closure(...)" in s
    assert "MotionSample" in s
    assert "MotionSegmentResult" in s


def test_closeout_reuses_w39_without_duplicate_solver():
    s = normalized()

    assert (
        "calls: solve_closure(...) exactly once"
        in s
    )

    assert "solve_closure_candidates(...)" in s

    assert (
        "does not implement another circle-intersection algorithm"
        in s
    )


def test_closeout_freezes_branch_continuity():
    s = normalized()

    assert "POSITIVE motion segment" in s
    assert "NEGATIVE motion segment" in s

    assert (
        "explicitly rejects an opposite selected branch"
        in s
    )


def test_closeout_freezes_boundary_termination():
    s = normalized()

    assert "TANGENT_BOUNDARY" in s
    assert "NO_SOLUTION_BOUNDARY" in s
    assert "DEGENERATE_BOUNDARY" in s

    assert (
        "No later requested angle is solved"
        in s
    )


def test_closeout_prevents_gap_and_resume():
    s = normalized()

    assert (
        "the sweep immediately stops"
        in s
    )

    assert (
        "not silently attached to the same continuous motion segment"
        in s
    )


def test_closeout_records_bc_trajectory_capability():
    s = normalized()

    assert "rear_link_shield = B" in s
    assert "front_link_shield = C" in s

    assert (
        "deterministic ordered B and C trajectories"
        in s
    )

    assert (
        "not yet an operating-height trajectory"
        in s
    )


def test_closeout_keeps_support_height_and_top_beam_out():
    s = normalized()

    assert "support_height_mm" in s
    assert "shield_top_beam_pivot trajectory" in s
    assert "beam_tip_trajectory" in s
    assert "80 mm validation" in s

    assert (
        "No operating-height coverage claim is made"
        in s
    )


def test_closeout_freezes_d4_top_beam_audit_boundary():
    s = normalized()

    assert (
        "audit and freeze the top-beam kinematic relationship"
        in s
    )

    assert "shield_top_beam_pivot" in s
    assert "beam_tip_reference_point" in s

    assert (
        "explicit engineering-geometry gap"
        in s
    )
