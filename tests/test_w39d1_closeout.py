from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D1_closeout.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_closeout_preserves_canonical_abcd_chain():
    s = text()

    assert "A = rear_link_base" in s
    assert "B = rear_link_shield" in s
    assert "C = front_link_shield" in s
    assert "D = front_link_base" in s
    assert "A -> B -> C -> D -> A" in s


def test_closeout_preserves_closure_states():
    s = text()

    for item in (
        "NO_SOLUTION",
        "TANGENT",
        "TWO_SOLUTIONS",
        "DEGENERATE",
    ):
        assert item in s


def test_closeout_keeps_w38_and_w39_classifiers_separate():
    s = normalized()

    assert "A -> D" in s
    assert "B -> D" in s
    assert "The two classifiers shall remain separate" in s


def test_closeout_forbids_arbitrary_branch_choice():
    s = normalized()

    assert "BRANCH_AMBIGUOUS" in s
    assert "The solver shall not guess" in s


def test_closeout_separates_math_and_engineering_benchmarks():
    s = text()

    assert "SYNTHETIC_MATH" in s
    assert "ENGINEERING_REFERENCE" in s
    assert "NOT_SOLVER_READY" in s

    assert (
        "does not constitute hydraulic-support engineering validation"
        in normalized()
    )


def test_closeout_preserves_provenance_boundary():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "introduces no Formula Registry ID" in s
    assert "introduces no Calculation Record" in s


def test_push_jack_debt_remains_p1():
    s = text()

    assert "mt_t94_verified = false" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s
    assert "P1 system-completeness evidence debt" in s


def test_w39d2_is_model_layer_not_solver():
    s = normalized()

    assert (
        "W39-D2 shall introduce strongly typed data models"
        in s
    )

    assert (
        "W39-D2 shall not yet implement the numerical closure solver"
        in s
    )
