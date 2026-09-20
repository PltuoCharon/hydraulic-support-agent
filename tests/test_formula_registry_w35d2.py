import csv
from pathlib import Path


REGISTRY = Path(
    "docs/evidence/formulas/"
    "W34D2_Formula_Registry.csv"
)


def rows_by_id():
    with REGISTRY.open(
        encoding="utf-8-sig",
        newline="",
    ) as f:
        rows = list(csv.reader(f))

    return {
        row[0]: row
        for row in rows
        if row
    }


def test_w35d2_formulas_are_active():
    rows = rows_by_id()

    for formula_id in (
        "F-QN-005",
        "F-QN-006",
        "F-QN-007",
    ):
        assert formula_id in rows
        assert rows[formula_id][3] == "active"


def test_w35d2_registry_uses_production_service():
    rows = rows_by_id()

    for formula_id in (
        "F-QN-005",
        "F-QN-006",
        "F-QN-007",
    ):
        row = rows[formula_id]

        assert (
            "app/services/calc/resistance.py"
            in row
        )

    assert "canopy_len" in rows["F-QN-005"][-1]
    assert "eta" in rows["F-QN-007"][-1]
