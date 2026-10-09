from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D4_closeout.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_separates_d3_math_from_d4_selection():
    s = normalized()

    assert (
        "W39-D3 answers: What mathematical closure solutions exist?"
        in s
    )

    assert (
        "W39-D4 answers: Which mathematical candidate matches"
        in s
    )

    assert (
        "D4 does not recalculate circle intersection"
        in s
    )


def test_closeout_keeps_w38_signature_separate():
    s = normalized()

    assert "SAME_SIDE" in s
    assert "OPPOSITE_SIDE" in s

    assert "SAME_SIDE -> POSITIVE" in s
    assert "OPPOSITE_SIDE -> NEGATIVE" in s

    assert "No such mapping is frozen" in s


def test_closeout_preserves_degenerate_reference_behavior():
    s = normalized()

    assert "reference branch is: null" in s

    assert (
        "does not guess POSITIVE or NEGATIVE"
        in s
    )

    assert "selection_status = BRANCH_AMBIGUOUS" in s
    assert "selected_pose = null" in s
    assert "branch_resolution = NONE" in s


def test_closeout_preserves_semantic_branch_selection():
    s = normalized()

    assert "task.reference_branch = POSITIVE" in s
    assert "task.reference_branch = NEGATIVE" in s

    assert (
        "Candidate lookup is based on branch semantics"
        in s
    )

    assert (
        "Candidate list position is not an engineering selection rule"
        in s
    )


def test_closeout_selected_pose_reuses_d3_geometry():
    s = normalized()

    assert (
        "rear_link_shield = D3 result rear_link_shield"
        in s
    )

    assert (
        "front_link_shield = selected D3 candidate point_c"
        in s
    )

    assert "D4 does not recompute B" in s
    assert "D4 does not recompute C" in s


def test_closeout_preserves_both_math_candidates():
    s = normalized()

    assert (
        "Both original D3 candidates remain"
        in s
    )

    assert (
        "The unselected candidate also remains present"
        in s
    )


def test_closeout_preserves_provenance_boundary():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s
    assert "branch_resolution = REFERENCE_POSE" in s

    assert (
        "does not promote the underlying geometry to VERIFIED"
        in s
    )


def test_d5_is_integration_not_math_rewrite():
    s = normalized()

    assert (
        "W39-D5 may integrate the W38 canonical geometry "
        "and explicit reference pose"
        in s
    )

    assert "consume one LinkageGeometry object" in s

    assert (
        "shall not modify D3 circle-intersection mathematics "
        "merely to make an engineering case pass"
        in s
    )
