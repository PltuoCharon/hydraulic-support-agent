from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D5_closeout.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_records_complete_integration_chain():
    s = normalized()

    assert "derive_geometry(linkage)" in s
    assert "analyze_reference_pose(linkage)" in s
    assert "derive_reference_branch(...)" in s
    assert "ClosureSolverInput" in s
    assert "solve_closure(...)" in s
    assert "validate_reference_pose_round_trip(...)" in s


def test_closeout_fresh_geometry_wins_over_stored_geometry():
    s = normalized()

    assert "linkage.derived_geometry" in s

    assert (
        "is not treated as authoritative solver geometry"
        in s
    )

    assert (
        "D5 does not overwrite linkage.derived_geometry"
        in s
    )


def test_closeout_keeps_w38_signature_separate_from_w39_branch():
    s = normalized()

    assert "SAME_SIDE" in s
    assert "OPPOSITE_SIDE" in s
    assert "POSITIVE" in s
    assert "NEGATIVE" in s

    assert (
        "No direct mapping between those classifications is assumed"
        in s
    )


def test_closeout_freezes_reference_pose_round_trip():
    s = normalized()

    assert (
        "solved: rear_link_shield must reproduce "
        "the W38 reference B point"
        in s
    )

    assert (
        "solved: front_link_shield must reproduce "
        "the W38 reference C point"
        in s
    )

    assert "Euclidean distance in millimetres" in s


def test_closeout_preserves_tangent_without_fake_branch():
    s = normalized()

    assert "reference_branch = null" in s
    assert "selected_pose.branch = TANGENT" in s
    assert "branch_resolution = TANGENT_UNIQUE" in s

    assert (
        "D5 does not invent POSITIVE or NEGATIVE"
        in s
    )


def test_closeout_preserves_provenance_boundary():
    s = normalized()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert (
        "does not promote any value to VERIFIED"
        in s
    )


def test_closeout_keeps_engineering_validation_pending():
    s = normalized()

    assert "ER-001 therefore remains:" in s
    assert "ENGINEERING_REFERENCE NOT_SOLVER_READY" in s

    assert (
        "No missing real-support geometry is fabricated"
        in s
    )


def test_closeout_moves_continuous_motion_to_w40():
    s = normalized()

    assert "support-height-to-pose inversion" in s
    assert "operating-height sweep" in s
    assert "branch continuity across multiple poses" in s

    assert (
        "Continuous multi-pose motion belongs to W40"
        in s
    )
