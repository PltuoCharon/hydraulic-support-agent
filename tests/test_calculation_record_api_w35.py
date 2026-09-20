import app.routers.calc as calc_router


def fake_recorder(captured, record_id=77):
    def _fake(**kwargs):
        captured.update(kwargs)
        return record_id
    return _fake


def test_column_design_records_direct_user_input(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        calc_router,
        "create_calculation_record",
        fake_recorder(captured),
    )

    req = calc_router.ColumnDesignReq(
        p_kn=2533,
        n=1,
        p_mpa=31.5,
        eta=1.0,
    )
    response = calc_router.column_design(req)

    assert response["code"] == 0
    assert response["data"]["record_id"] == 77
    assert captured["calc_type"] == "column_design"
    assert captured["run_mode"] == "engineering"
    assert captured["formula_ids"] == [
        "F-COL-001",
        "F-COL-002",
    ]
    assert captured["context_source_type"] == "user_input"
    assert captured["context_confirmed"] is None
    assert captured["inputs_snapshot"]["p_kn"] == 2533


def test_column_design_records_setting_ratio_formula(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        calc_router,
        "create_calculation_record",
        fake_recorder(captured, 78),
    )

    req = calc_router.ColumnDesignReq(
        p_kn=2533,
        n=1,
        p_mpa=31.5,
        eta=1.0,
        p_set_kn=1900,
    )
    response = calc_router.column_design(req)

    assert response["code"] == 0
    assert response["data"]["record_id"] == 78
    assert captured["formula_ids"] == [
        "F-COL-001",
        "F-COL-002",
        "F-COL-003",
    ]


def test_column_design_preserves_confirmed_selected_support(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        calc_router,
        "create_calculation_record",
        fake_recorder(captured, 79),
    )

    context = {
        "target": {
            "support_model": "TEST",
            "resistance_kn": 5000,
        },
        "provenance": {
            "source_text": "test source",
            "data_status": "verified",
        },
        "confirmed": True,
    }

    req = calc_router.ColumnDesignReq(
        p_kn=5000,
        n=2,
        p_mpa=31.5,
        eta=0.9,
        run_mode="engineering",
        context_source_type="selected_support",
        context_confirmed=True,
        context_snapshot=context,
    )
    response = calc_router.column_design(req)

    assert response["code"] == 0
    assert captured["context_source_type"] == "selected_support"
    assert captured["context_confirmed"] is True
    assert (
        captured["context_snapshot"]["target"]["support_model"]
        == "TEST"
    )


def test_column_design_demotes_modified_transfer_to_user_input(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        calc_router,
        "create_calculation_record",
        fake_recorder(captured, 80),
    )

    req = calc_router.ColumnDesignReq(
        p_kn=5200,
        n=2,
        p_mpa=31.5,
        eta=0.9,
        context_source_type="selected_support",
        context_confirmed=True,
        context_snapshot={
            "target": {
                "support_model": "TEST",
                "resistance_kn": 5000,
            }
        },
    )
    response = calc_router.column_design(req)

    assert response["code"] == 0
    assert captured["context_source_type"] == "user_input"
    assert captured["context_confirmed"] is None
    assert captured["context_snapshot"]["actual_input_override"] == {
        "field": "p_kn",
        "reference_value": 5000.0,
        "actual_value": 5200.0,
    }


def test_column_design_rejects_unconfirmed_transfer_without_record(monkeypatch):
    called = {"value": False}

    def _fake(**kwargs):
        called["value"] = True
        return 81

    monkeypatch.setattr(
        calc_router,
        "create_calculation_record",
        _fake,
    )

    req = calc_router.ColumnDesignReq(
        p_kn=5000,
        n=2,
        p_mpa=31.5,
        eta=0.9,
        context_source_type="selected_support",
        context_confirmed=False,
        context_snapshot={
            "target": {
                "support_model": "TEST",
                "resistance_kn": 5000,
            }
        },
    )
    response = calc_router.column_design(req)

    assert response["code"] == 1
    assert called["value"] is False
