from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_push_jack_api_benchmark():
    response = client.post(
        "/api/calc/push-jack-design",
        json={
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
            "rod_mm": 70,
            "pull_required_kn": 250,
            "stroke_mm": 800,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 0

    data = body["data"]

    assert data["bore_calc_mm"] == 110.1
    assert data["bore_candidate_mm"] == 125
    assert data["push_actual_kn"] == 386.6
    assert data["push_ok"] is True

    assert data["rod_mm"] == 70
    assert data["pull_actual_kn"] == 265.3
    assert data["pull_required_kn"] == 250
    assert data["pull_ok"] is True

    assert data["stroke_mm"] == 800
    assert data["stroke_origin"] == "user_input"
    assert data["mt_t94_verified"] is False

    assert "record_id" not in data


def test_push_jack_api_rejects_invalid_rod():
    response = client.post(
        "/api/calc/push-jack-design",
        json={
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
            "rod_mm": 125,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 1
    assert "活塞杆直径必须小于候选缸径" in body["msg"]


def test_pull_requirement_without_rod_is_rejected():
    response = client.post(
        "/api/calc/push-jack-design",
        json={
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
            "pull_required_kn": 250,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 1
    assert "必须同时提供活塞杆直径" in body["msg"]


def test_missing_required_pressure_returns_422():
    response = client.post(
        "/api/calc/push-jack-design",
        json={
            "push_required_kn": 300,
        },
    )

    assert response.status_code == 422


def test_push_jack_api_does_not_create_calculation_record(
    monkeypatch,
):
    import app.routers.calc as calc_router

    def forbidden_record_write(**kwargs):
        raise AssertionError(
            "push jack must not create calculation record"
        )

    monkeypatch.setattr(
        calc_router,
        "create_calculation_record",
        forbidden_record_write,
    )

    response = client.post(
        "/api/calc/push-jack-design",
        json={
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
        },
    )

    assert response.status_code == 200
    assert response.json()["code"] == 0
