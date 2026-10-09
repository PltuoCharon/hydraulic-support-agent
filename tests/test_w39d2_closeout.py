from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D2_closeout.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_reuses_w38_type_system():
    s = text()

    for item in (
        "StrictModel",
        "NormalizedOriginPoint",
        "EngineeringPoint2D",
        "MillimetreParameter",
        "DegreeParameter",
    ):
        assert item in s

    assert "does not replace hs.linkageGeometry.v1" in s


def test_closeout_preserves_explicit_tolerance_boundary():
    s = normalized()

    assert "absolute_mm" in s
    assert "relative" in s

    assert (
        "finite and strictly positive"
        in s
    )

    assert (
        "not a hydraulic-support engineering design parameter"
        in s
    )


def test_closeout_separates_multiplicity_from_selection():
    s = normalized()

    assert "NO_SOLUTION" in s
    assert "TANGENT" in s
    assert "TWO_SOLUTIONS" in s
    assert "DEGENERATE" in s

    assert "SELECTED" in s
    assert "BRANCH_AMBIGUOUS" in s
    assert "NOT_APPLICABLE" in s

    assert (
        "TWO_SOLUTIONS does not imply SELECTED"
        in s
    )


def test_closeout_preserves_tangent_invariant():
    s = normalized()

    assert (
        "branch_resolution = TANGENT_UNIQUE"
        in s
    )

    assert (
        "selected pose C coordinate must equal "
        "the sole candidate C coordinate"
        in s
    )


def test_closeout_preserves_two_solution_invariant():
    s = normalized()

    assert (
        "Their branch set must be exactly: POSITIVE NEGATIVE"
        in s
    )

    assert (
        "Matching the branch label alone is insufficient"
        in s
    )

    assert (
        "branch_resolution = REFERENCE_POSE"
        in s
    )


def test_closeout_preserves_selected_pose_identity():
    s = normalized()

    assert "selected_pose.rear_link_shield" in s

    assert (
        "must equal: ClosureResult.rear_link_shield"
        in s
    )

    assert (
        "cannot contain two contradictory solved B points"
        in s
    )


def test_closeout_preserves_solver_provenance_boundary():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert (
        "A deterministic mathematical result "
        "is not automatically VERIFIED"
        in normalized()
    )


def test_d3_entry_condition_is_numerical_not_optimization():
    s = normalized()

    assert (
        "W39-D3 may now implement deterministic "
        "numerical closure primitives"
        in s
    )

    assert "two-circle intersection" in s
    assert "candidate branch sign" in s

    assert (
        "linkage optimization"
        in s
    )
