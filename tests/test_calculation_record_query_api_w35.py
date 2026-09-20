from datetime import datetime

import app.routers.calc as calc_router


def test_record_list_returns_summary_and_iso_time(monkeypatch):
    monkeypatch.setattr(
        calc_router,
        "list_calculation_records",
        lambda **kwargs: [
            {
                "id": 7,
                "record_version": 1,
                "calc_type": "column_design",
                "run_mode": "engineering",
                "formula_ids": ["F-COL-001", "F-COL-002"],
                "context_source_type": "user_input",
                "context_confirmed": None,
                "created_at": datetime(2026, 9, 20, 15, 30, 0),
            }
        ],
    )

    response = calc_router.calculation_records(
        calc_type="column_design",
        limit=20,
    )

    assert response["code"] == 0
    assert len(response["data"]) == 1
    assert response["data"][0]["id"] == 7
    assert response["data"][0]["formula_ids"] == [
        "F-COL-001",
        "F-COL-002",
    ]
    assert (
        response["data"][0]["created_at"]
        == "2026-09-20T15:30:00"
    )


def test_record_detail_returns_structured_snapshots(monkeypatch):
    monkeypatch.setattr(
        calc_router,
        "get_calculation_record",
        lambda record_id: {
            "id": record_id,
            "record_version": 1,
            "calc_type": "column_design",
            "run_mode": "engineering",
            "formula_ids": ["F-COL-001"],
            "inputs_snapshot": {"p_kn": 2533},
            "outputs_snapshot": {"d_std_mm": 320},
            "context_source_type": "selected_support",
            "context_confirmed": True,
            "context_snapshot": {
                "target": {
                    "resistance_kn": 2533,
                }
            },
            "created_at": datetime(2026, 9, 20, 16, 0, 0),
        },
    )

    response = calc_router.calculation_record_detail(9)

    assert response["code"] == 0
    assert response["data"]["id"] == 9
    assert response["data"]["inputs_snapshot"] == {
        "p_kn": 2533
    }
    assert response["data"]["outputs_snapshot"] == {
        "d_std_mm": 320
    }
    assert response["data"]["context_source_type"] == "selected_support"
    assert response["data"]["created_at"] == "2026-09-20T16:00:00"


def test_missing_record_returns_explicit_error(monkeypatch):
    monkeypatch.setattr(
        calc_router,
        "get_calculation_record",
        lambda record_id: None,
    )

    response = calc_router.calculation_record_detail(999)

    assert response == {
        "code": 1,
        "msg": "calculation record not found",
    }


def test_corrupt_record_error_is_exposed(monkeypatch):
    def _broken(**kwargs):
        raise calc_router.CalculationRecordDataError(
            "invalid JSON in formula_ids"
        )

    monkeypatch.setattr(
        calc_router,
        "list_calculation_records",
        _broken,
    )

    response = calc_router.calculation_records()

    assert response["code"] == 1
    assert response["msg"] == "invalid JSON in formula_ids"
