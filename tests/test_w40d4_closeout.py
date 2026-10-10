from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w40/W40D4_closeout.md"


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_freezes_bc_to_e_capability():
    s = normalized()

    assert "B/C trajectory" in s
    assert "shield rigid-body pose" in s
    assert "E trajectory" in s

    assert "DETERMINISTICALLY MODELABLE" in s


def test_closeout_freezes_directed_shield_frame():
    s = normalized()

    assert "u0 = (C0 - B0) / L0" in s
    assert "v0 = (-u0_y, u0_x)" in s
    assert "B0 -> C0" in s


def test_closeout_freezes_e_rigid_transform():
    s = normalized()

    assert "s_E = dot(E0 - B0, u0)" in s
    assert "n_E = dot(E0 - B0, v0)" in s

    assert (
        "Ei = Bi + s_E * ui + n_E * vi"
        in s
    )


def test_closeout_keeps_unsolved_samples_without_e():
    s = normalized()

    assert "NO_SOLUTION" in s
    assert "DEGENERATE" in s

    assert (
        "shall not fabricate an E point for an unsolved sample"
        in s
    )


def test_closeout_does_not_turn_e_into_beam_tip_solution():
    s = normalized()

    assert (
        "does not uniquely determine: T"
        in s
    )

    assert (
        "currently forbidden as an engineering assumption"
        in s
    )

    assert "NOT YET UNIQUELY SOLVABLE" in s


def test_closeout_records_balance_jack_geometry_gap():
    s = normalized()

    assert "shield-side balance-jack pivot" in s
    assert "top-beam-side balance-jack pivot" in s
    assert "effective jack length" in s

    assert (
        "Component existence alone is insufficient"
        in s
    )


def test_closeout_preserves_80mm_blocker():
    s = normalized()

    assert "beam-tip horizontal displacement <= 80 mm" in s

    assert (
        "deterministic beam-tip trajectory"
        in s
    )

    assert (
        "deterministic mapping to the complete "
        "operating-height range"
        in s
    )


def test_closeout_freezes_d5_boundary():
    s = normalized()

    assert (
        "B/C motion + explicit E0 -> E trajectory"
        in s
    )

    assert (
        "D5 shall not implement a beam-tip trajectory"
        in s
    )

    assert (
        "Missing geometry shall remain explicit rather than fabricated"
        in s
    )
