from pathlib import Path
import csv


REG = Path(
    "docs/evidence/formulas/W34D2_Formula_Registry.csv"
)


def load_rows():
    with REG.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_formula_registry_ids_unique():
    rows = load_rows()
    ids = [r["formula_id"] for r in rows]

    assert len(ids) == len(set(ids))
    assert all(ids)


def test_core_formula_registry_present():
    ids = {r["formula_id"] for r in load_rows()}

    required = {
        "F-QN-001",
        "F-QN-002",
        "F-QN-003",
        "F-QN-004",
        "F-COL-001",
        "F-COL-002",
        "F-COL-003",
        "F-STR-001",
        "F-STR-002",
        "F-STR-003",
        "F-STR-004",
        "F-STR-005",
        "F-STR-006",
    }

    assert required <= ids


def test_legacy_formulas_are_not_active():
    rows = load_rows()

    for r in rows:
        if r["formula_id"].startswith(
            ("F-LEG-", "F-SC-")
        ):
            assert r["status"] == "legacy_review"
