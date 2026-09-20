import csv

import pytest

import app.services.formula_registry as registry


def write_registry(path, rows, fieldnames=None):
    fields = fieldnames or list(registry.REQUIRED_FIELDS)

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fields,
        )
        writer.writeheader()
        writer.writerows(rows)


def make_row(formula_id="F-TEST-001"):
    return {
        "formula_id": formula_id,
        "module": "test",
        "name": "测试公式",
        "status": "active",
        "formula": "x=y",
        "input_vars": "y",
        "output": "x",
        "unit": "-",
        "source": "test source",
        "verification": "test verification",
        "current_callers": "test.py",
        "notes": "",
    }


def test_list_formulas_preserves_registry_order_and_summary_fields(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "registry.csv"
    write_registry(
        path,
        [
            make_row("F-TEST-002"),
            make_row("F-TEST-001"),
        ],
    )
    monkeypatch.setattr(
        registry,
        "REGISTRY_PATH",
        path,
    )

    result = registry.list_formulas()

    assert [
        row["formula_id"]
        for row in result
    ] == [
        "F-TEST-002",
        "F-TEST-001",
    ]
    assert set(result[0]) == set(
        registry.SUMMARY_FIELDS
    )


def test_get_formula_returns_all_frozen_fields(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "registry.csv"
    write_registry(
        path,
        [make_row()],
    )
    monkeypatch.setattr(
        registry,
        "REGISTRY_PATH",
        path,
    )

    result = registry.get_formula(
        "F-TEST-001"
    )

    assert set(result) == set(
        registry.REQUIRED_FIELDS
    )
    assert result["input_vars"] == "y"
    assert result["notes"] == ""


def test_unknown_formula_returns_none(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "registry.csv"
    write_registry(path, [make_row()])
    monkeypatch.setattr(
        registry,
        "REGISTRY_PATH",
        path,
    )

    assert registry.get_formula(
        "F-NOT-FOUND"
    ) is None


def test_missing_required_header_fails(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "registry.csv"
    fields = [
        field
        for field in registry.REQUIRED_FIELDS
        if field != "verification"
    ]
    row = make_row()
    row.pop("verification")

    write_registry(
        path,
        [row],
        fieldnames=fields,
    )
    monkeypatch.setattr(
        registry,
        "REGISTRY_PATH",
        path,
    )

    with pytest.raises(
        registry.FormulaRegistryDataError,
        match="missing fields",
    ):
        registry.list_formulas()


def test_duplicate_formula_id_fails(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "registry.csv"
    write_registry(
        path,
        [
            make_row("F-TEST-001"),
            make_row("F-TEST-001"),
        ],
    )
    monkeypatch.setattr(
        registry,
        "REGISTRY_PATH",
        path,
    )

    with pytest.raises(
        registry.FormulaRegistryDataError,
        match="duplicate formula_id",
    ):
        registry.list_formulas()


def test_empty_formula_id_fails(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "registry.csv"
    write_registry(
        path,
        [make_row("")],
    )
    monkeypatch.setattr(
        registry,
        "REGISTRY_PATH",
        path,
    )

    with pytest.raises(
        registry.FormulaRegistryDataError,
        match="empty formula_id",
    ):
        registry.list_formulas()


def test_formula_id_argument_must_be_non_empty_string():
    with pytest.raises(
        ValueError,
        match="formula_id",
    ):
        registry.get_formula("")

    with pytest.raises(
        ValueError,
        match="formula_id",
    ):
        registry.get_formula(None)
