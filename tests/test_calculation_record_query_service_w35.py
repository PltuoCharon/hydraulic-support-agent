import json

import pytest

import app.services.calculation_records as records


class FakeCursor:
    def __init__(self, rows=None, row=None):
        self.rows = rows or []
        self.row = row
        self.sql = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.sql = sql
        self.params = params

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.row


class FakeConn:
    def __init__(self, cursor):
        self._cursor = cursor
        self.closed = False

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True


def test_list_records_decodes_formula_ids_and_is_read_only(monkeypatch):
    cursor = FakeCursor(
        rows=[
            {
                "id": 2,
                "record_version": 1,
                "calc_type": "column_design",
                "run_mode": "engineering",
                "formula_ids": json.dumps(
                    ["F-COL-001", "F-COL-002"]
                ),
                "context_source_type": "user_input",
                "context_confirmed": None,
                "created_at": None,
            }
        ]
    )
    conn = FakeConn(cursor)
    monkeypatch.setattr(records, "get_conn", lambda: conn)

    result = records.list_calculation_records(limit=2)

    assert result[0]["formula_ids"] == [
        "F-COL-001",
        "F-COL-002",
    ]
    assert result[0]["context_confirmed"] is None
    assert "ORDER BY created_at DESC, id DESC" in cursor.sql
    assert "LIMIT %s" in cursor.sql
    assert cursor.params == ("column_design", 2)
    assert conn.closed is True


def test_get_record_decodes_all_snapshots(monkeypatch):
    cursor = FakeCursor(
        row={
            "id": 7,
            "record_version": 1,
            "calc_type": "column_design",
            "run_mode": "engineering",
            "formula_ids": "[\"F-COL-001\"]",
            "inputs_snapshot": "{\"p_kn\":2533}",
            "outputs_snapshot": "{\"d_std_mm\":320}",
            "context_source_type": "selected_support",
            "context_confirmed": 1,
            "context_snapshot": "{\"target\":{\"resistance_kn\":2533}}",
            "created_at": None,
        }
    )
    conn = FakeConn(cursor)
    monkeypatch.setattr(records, "get_conn", lambda: conn)

    result = records.get_calculation_record(7)

    assert result["formula_ids"] == ["F-COL-001"]
    assert result["inputs_snapshot"] == {"p_kn": 2533}
    assert result["outputs_snapshot"] == {"d_std_mm": 320}
    assert result["context_confirmed"] is True
    assert result["context_snapshot"]["target"]["resistance_kn"] == 2533
    assert cursor.params == (7,)
    assert conn.closed is True


def test_get_missing_record_returns_none(monkeypatch):
    cursor = FakeCursor(row=None)
    conn = FakeConn(cursor)
    monkeypatch.setattr(records, "get_conn", lambda: conn)

    assert records.get_calculation_record(999) is None
    assert conn.closed is True


def test_corrupt_json_raises_data_error(monkeypatch):
    cursor = FakeCursor(
        rows=[
            {
                "id": 1,
                "record_version": 1,
                "calc_type": "column_design",
                "run_mode": "engineering",
                "formula_ids": "{broken",
                "context_source_type": "user_input",
                "context_confirmed": None,
                "created_at": None,
            }
        ]
    )
    conn = FakeConn(cursor)
    monkeypatch.setattr(records, "get_conn", lambda: conn)

    with pytest.raises(
        records.CalculationRecordDataError,
        match="formula_ids",
    ):
        records.list_calculation_records()


def test_wrong_json_top_level_type_is_rejected():
    with pytest.raises(
        records.CalculationRecordDataError,
        match="top-level type",
    ):
        records._decode_json_field(
            "{\"x\":1}",
            "formula_ids",
            list,
        )


def test_query_arguments_are_bounded():
    with pytest.raises(ValueError, match="calc_type"):
        records.list_calculation_records(
            calc_type="other",
        )

    with pytest.raises(ValueError, match="limit"):
        records.list_calculation_records(
            limit=101,
        )

    with pytest.raises(ValueError, match="record_id"):
        records.get_calculation_record(0)
