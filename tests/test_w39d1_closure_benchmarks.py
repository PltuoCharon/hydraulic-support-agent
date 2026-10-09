import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = (
    ROOT
    / "docs/evidence/w39/W39D1_closure_benchmarks.csv"
)

POLICY = (
    ROOT
    / "docs/evidence/w39/W39D1_benchmark_policy.md"
)


def rows():
    with CSV_PATH.open(
        encoding="utf-8",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def policy_text():
    return POLICY.read_text(encoding="utf-8")


def test_six_synthetic_math_cases_are_registered():
    synthetic = [
        row
        for row in rows()
        if row["benchmark_class"] == "SYNTHETIC_MATH"
    ]

    assert len(synthetic) == 6

    assert {
        row["case_id"]
        for row in synthetic
    } == {
        "SM-001",
        "SM-002",
        "SM-003",
        "SM-004",
        "SM-005",
        "SM-006",
    }


def test_synthetic_cases_cover_core_multiplicity_states():
    states = {
        row["expected_closure_state"]
        for row in rows()
        if row["benchmark_class"] == "SYNTHETIC_MATH"
    }

    assert "TWO_SOLUTIONS" in states
    assert "TANGENT" in states
    assert "NO_SOLUTION" in states
    assert "DEGENERATE" in states


def test_synthetic_cases_are_never_engineering_verified():
    for row in rows():
        if row["benchmark_class"] != "SYNTHETIC_MATH":
            continue

        assert row["engineering_verified"] == "false"
        assert "synthetic" in row["source_text"].lower()


def test_two_solution_case_has_expected_circle_geometry():
    row = next(
        r
        for r in rows()
        if r["case_id"] == "SM-001"
    )

    # B = (5, 0), D = (8, 0), hence q = 3.
    assert float(row["AB_mm"]) == 5
    assert float(row["rear_link_angle_deg"]) == 0
    assert float(row["BC_mm"]) == 5
    assert float(row["CD_mm"]) == 5
    assert row["expected_closure_state"] == "TWO_SOLUTIONS"


def test_tangent_case_is_explicit():
    row = next(
        r
        for r in rows()
        if r["case_id"] == "SM-002"
    )

    # q = 3 and BC + CD = 3.
    assert float(row["BC_mm"]) == 1
    assert float(row["CD_mm"]) == 2
    assert row["expected_closure_state"] == "TANGENT"


def test_coincident_equal_circle_case_is_degenerate():
    row = next(
        r
        for r in rows()
        if r["case_id"] == "SM-005"
    )

    assert float(row["D_x_mm"]) == 5
    assert float(row["AB_mm"]) == 5

    assert float(row["BC_mm"]) == float(row["CD_mm"])

    assert row["expected_closure_state"] == "DEGENERATE"


def test_engineering_reference_is_not_fabricated():
    engineering = [
        row
        for row in rows()
        if row["benchmark_class"] == "ENGINEERING_REFERENCE"
    ]

    assert len(engineering) == 1

    row = engineering[0]

    assert row["case_id"] == "ER-001"
    assert row["status"] == "NOT_SOLVER_READY"
    assert row["engineering_verified"] == "false"

    assert row["A_x_mm"] == ""
    assert row["D_x_mm"] == ""
    assert row["AB_mm"] == ""
    assert row["BC_mm"] == ""
    assert row["CD_mm"] == ""


def test_policy_requires_complete_engineering_geometry():
    s = policy_text()

    for item in (
        "fixed pivot A",
        "fixed pivot D",
        "rear-link length AB",
        "shield linkage length BC",
        "front-link length CD",
        "source provenance",
    ):
        assert item in s


def test_policy_keeps_math_and_engineering_validation_separate():
    s = " ".join(policy_text().split())

    assert (
        "They are not hydraulic-support design data"
        in s
    )

    assert (
        "Passing SYNTHETIC_MATH tests shall never promote "
        "an engineering case to verified status"
        in s
    )

    assert (
        "Software validation and engineering validation remain separate"
        in s
    )
