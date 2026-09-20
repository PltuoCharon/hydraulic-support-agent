import app.routers.formulas as formulas_router


def test_formula_list_returns_service_data(
    monkeypatch,
):
    monkeypatch.setattr(
        formulas_router,
        "list_formulas",
        lambda: [
            {
                "formula_id": "F-COL-001",
                "module": "column",
                "name": "立柱理论缸径反算",
                "status": "active",
                "formula": "D=...",
                "unit": "mm",
            }
        ],
    )

    response = formulas_router.formula_list()

    assert response["code"] == 0
    assert response["data"][0][
        "formula_id"
    ] == "F-COL-001"


def test_formula_detail_returns_full_record(
    monkeypatch,
):
    row = {
        "formula_id": "F-COL-003",
        "module": "column",
        "name": "初撑力比",
        "status": "active",
        "formula": "r=P_set/P_rated",
        "input_vars": "P_set;P_rated",
        "output": "r",
        "unit": "-",
        "source": "W35-D2已核标准证据",
        "verification": "校核区间60%~85%",
        "current_callers": "column.py",
        "notes": "test",
    }
    monkeypatch.setattr(
        formulas_router,
        "get_formula",
        lambda formula_id: row,
    )

    response = formulas_router.formula_detail(
        "F-COL-003"
    )

    assert response == {
        "code": 0,
        "data": row,
    }


def test_unknown_formula_returns_explicit_error(
    monkeypatch,
):
    monkeypatch.setattr(
        formulas_router,
        "get_formula",
        lambda formula_id: None,
    )

    response = formulas_router.formula_detail(
        "F-NOT-FOUND"
    )

    assert response == {
        "code": 1,
        "msg": "formula not found",
    }


def test_registry_data_error_is_exposed(
    monkeypatch,
):
    def broken():
        raise formulas_router.FormulaRegistryDataError(
            "duplicate formula_id: F-X"
        )

    monkeypatch.setattr(
        formulas_router,
        "list_formulas",
        broken,
    )

    response = formulas_router.formula_list()

    assert response == {
        "code": 1,
        "msg": "duplicate formula_id: F-X",
    }


def test_formula_routes_are_exact_and_read_only():
    from app.main import app

    paths = {
        path: {
            method.upper()
            for method in spec
            if method.lower() in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
            }
        }
        for path, spec in app.openapi()["paths"].items()
        if path.startswith("/api/formulas")
    }

    assert set(paths) == {
        "/api/formulas",
        "/api/formulas/{formula_id}",
    }

    assert paths[
        "/api/formulas"
    ] == {"GET"}

    assert paths[
        "/api/formulas/{formula_id}"
    ] == {"GET"}
