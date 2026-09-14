"""W30-D2 厂商分布守门测试"""
from app.services.queries import vendor_dist


def test_vendor_dist_total_conserved():
    """total 守恒: 已知+未知 = verified 总数"""
    d = vendor_dist()
    assert d["total"] >= 150
    assert d["known"] + d["unknown"] == d["total"]
    assert sum(i["cnt"] for i in d["items"]) == d["total"]


def test_vendor_dist_suspect_excluded():
    """铁律4: suspect 型号不计入(总数应等于 spectrum 的 157)"""
    from app.services.queries import spectrum
    assert vendor_dist()["total"] == len(spectrum())


def test_vendor_dist_api():
    from fastapi.testclient import TestClient
    from app.main import app
    r = TestClient(app).get("/api/supports/vendors")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["unknown"] > 0 and 0 < d["coverage"] < 100
    assert d["items"][0]["manufacturer"] == "未知"
