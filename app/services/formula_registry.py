import csv
from pathlib import Path


REGISTRY_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "evidence"
    / "formulas"
    / "W34D2_Formula_Registry.csv"
)

REQUIRED_FIELDS = (
    "formula_id",
    "module",
    "name",
    "status",
    "formula",
    "input_vars",
    "output",
    "unit",
    "source",
    "verification",
    "current_callers",
    "notes",
)

SUMMARY_FIELDS = (
    "formula_id",
    "module",
    "name",
    "status",
    "formula",
    "unit",
)


class FormulaRegistryDataError(ValueError):
    pass


def _load_registry_rows():
    try:
        with REGISTRY_PATH.open(
            encoding="utf-8-sig",
            newline="",
        ) as f:
            reader = csv.DictReader(f)

            fieldnames = reader.fieldnames or []
            missing = [
                field
                for field in REQUIRED_FIELDS
                if field not in fieldnames
            ]
            if missing:
                raise FormulaRegistryDataError(
                    "formula registry missing fields: "
                    + ", ".join(missing)
                )

            rows = list(reader)

    except FormulaRegistryDataError:
        raise
    except (OSError, UnicodeError, csv.Error) as exc:
        raise FormulaRegistryDataError(
            "failed to read formula registry"
        ) from exc

    seen = set()

    for row in rows:
        formula_id = row.get("formula_id")

        if not formula_id:
            raise FormulaRegistryDataError(
                "formula registry contains empty formula_id"
            )

        if formula_id in seen:
            raise FormulaRegistryDataError(
                f"duplicate formula_id: {formula_id}"
            )

        seen.add(formula_id)

    return rows


def list_formulas():
    rows = _load_registry_rows()

    return [
        {
            field: row[field]
            for field in SUMMARY_FIELDS
        }
        for row in rows
    ]


def get_formula(formula_id):
    if (
        not isinstance(formula_id, str)
        or not formula_id.strip()
    ):
        raise ValueError(
            "formula_id must be a non-empty string"
        )

    rows = _load_registry_rows()

    for row in rows:
        if row["formula_id"] == formula_id:
            return {
                field: row[field]
                for field in REQUIRED_FIELDS
            }

    return None
