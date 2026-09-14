"""W30-D1 架型谱系守门测试"""
from app.services.queries import spectrum


def test_spectrum_suspect_excluded():
    """铁律4: suspect 型号(id=63 ZY21000/38/82D, id=131 ZY18900/36/72D)不得出现在谱系"""
    ids = {i["id"] for i in spectrum()}
    assert 63 not in ids and 131 not in ids


def test_spectrum_plottable_fields():
    items = spectrum()
    assert len(items) >= 150
    for i in items:
        assert i["working_resistance"] is not None
        assert i["height_mid"] is not None
        assert i["est_fields"]


def test_spectrum_api():
    from fastapi.testclient import TestClient
    from app.main import app
    r = TestClient(app).get("/api/supports/spectrum")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["total"] == len(d["items"]) >= 150
    assert d["axis_note"]
