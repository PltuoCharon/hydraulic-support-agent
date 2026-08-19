"""W24-D6 接口断言：recalc / requirement / chat。回归时保证参数链与对话不退化。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_requirement():
    r = client.get("/api/requirement/", params={"coal_thickness": 8.8})
    assert r.status_code == 200
    d = r.json()["data"]
    assert abs(d["intensity"] - 1.76) < 0.001
    assert abs(d["resistance"] - 21287.2) < 1.0

def test_recalc_small_bore_alarm():
    # 小缸径 → 支护强度/工作阻力低于需求 → 有报警
    r = client.post("/api/recalc/", json={
        "support_model": "ZF15000/25/45", "bore": 360,
        "column_count": 4, "pump_pressure": 31.5, "coal_thickness": 8.8})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["new_params"]["setting_load"] > 0
    assert len(d["alarms"]) >= 1   # 360/4/31.5 应低于需求 21287/1.76

def test_recalc_large_bore_no_alarm():
    # 大缸径 + 高压 → 达标无报警
    r = client.post("/api/recalc/", json={
        "support_model": "ZF15000/25/45", "bore": 480,
        "column_count": 4, "pump_pressure": 37.5, "coal_thickness": 8.8})
    d = r.json()["data"]
    assert d["alarms"] == []

def test_recalc_chain_matches_formula():
    # 链式公式：setting_load = n*P*pi/4*D^2
    r = client.post("/api/recalc/", json={
        "support_model": "X", "bore": 360,
        "column_count": 4, "pump_pressure": 31.5, "coal_thickness": 8.8})
    d = r.json()["data"]
    expect = 4 * 31.5 * 3.14159 * (0.36 ** 2) / 4 * 1000
    assert abs(d["new_params"]["setting_load"] - expect) < 5

def test_chat_collect_stage():
    r = client.post("/api/chat/", json={"message": "推荐一个支架"})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["stage"] == "collect"
    assert len(d["missing"]) >= 1

def test_chat_why_explained():
    # 收集→确认→为什么 → explained + 带出处
    r1 = client.post("/api/chat/", json={"message": "煤层厚度8.8米，倾角2度，低瓦斯"})
    sid = r1.json()["data"]["session_id"]
    client.post("/api/chat/", json={"message": "对", "session_id": sid})
    r3 = client.post("/api/chat/", json={"message": "为什么推荐它", "session_id": sid})
    d = r3.json()["data"]
    assert d["stage"] == "explained"
    assert "案例库" in d["reply"]
