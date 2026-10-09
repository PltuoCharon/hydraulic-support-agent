from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D3_closeout.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_records_executable_d3_scope():
    s = text()

    assert "app/services/linkage_closure.py" in s

    for item in (
        "NO_SOLUTION",
        "TANGENT",
        "TWO_SOLUTIONS",
        "DEGENERATE",
    ):
        assert item in s


def test_closeout_preserves_base_consistency_boundary():
    s = normalized()

    assert "distance(A, D)" in s
    assert "base_pivot_spacing_mm" in s

    assert (
        "explicit input-consistency failure"
        in s
    )

    assert (
        "It is not returned as NO_SOLUTION"
        in s
    )


def test_closeout_preserves_dimensionally_coherent_tolerance():
    s = normalized()

    assert (
        "effective_tolerance_mm = max( "
        "absolute_mm, relative * scale_mm )"
        in s
    )

    assert (
        "signed_distance_mm = cross / distance(B, D)"
        in s
    )

    assert "unit mm" in s


def test_closeout_keeps_two_solution_unselected():
    s = normalized()

    assert "closure_state = TWO_SOLUTIONS" in s
    assert "selection_status = BRANCH_AMBIGUOUS" in s
    assert "selected_pose = null" in s
    assert "branch_resolution = NONE" in s

    assert (
        "W39-D3 intentionally does not consume it "
        "for TWO_SOLUTIONS selection"
        in s
    )


def test_closeout_tangent_selection_is_math_uniqueness():
    s = normalized()

    assert "branch_resolution = TANGENT_UNIQUE" in s

    assert (
        "This is mathematical uniqueness"
        in s
    )

    assert (
        "It is not engineering reference-branch selection"
        in s
    )


def test_closeout_preserves_provenance_boundary():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert "introduces no Formula Registry ID" in s
    assert "creates no Calculation Record" in s


def test_closeout_records_all_six_synthetic_results():
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

    assert (
        "do not constitute hydraulic-support engineering validation"
        in normalized()
    )


def test_d4_owns_engineering_branch_resolution():
    s = normalized()

    assert (
        "W39-D4 may now implement engineering branch resolution"
        in s
    )

    assert (
        "shall not: - recalculate the circle intersection "
        "merely to select a branch"
        in s
    )

    assert (
        "If a non-degenerate reference branch is unavailable, "
        "the result shall remain BRANCH_AMBIGUOUS"
        in s
    )
