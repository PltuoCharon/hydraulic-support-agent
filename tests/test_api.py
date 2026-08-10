from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_areas_real_data():
    r = client.get("/api/areas/").json()
    assert r["data"]["total"] > 0

def test_area_404():
    assert client.get("/api/areas/99999").status_code == 404

def test_recommend_validation():
    r = client.post("/api/supports/recommend",
                    json={"seam_thickness": 99, "gas_level": "低瓦斯"})
    assert r.status_code == 422

def test_filter_excludes_suspect():
    r = client.get("/api/supports/").json()
    models = [s["model"] for s in r["data"]["items"]]
    assert "ZY18900/36/72D" not in models

def test_match_topn():
    r = client.post("/api/match", json={"area_id": 1, "top_n": 5})
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert len(items) <= 5
    sims = [i["similarity"] for i in items]
    assert sims == sorted(sims, reverse=True)

def test_match_404():
    assert client.post("/api/match", json={"area_id": 99999}).status_code == 404

def test_ahp_consistency():
    from app.services.ahp import ahp_weights, JUDGE_MATRIX
    assert ahp_weights(JUDGE_MATRIX)["CR"] < 0.1

def test_match_topn():
    r = client.post("/api/match", json={"area_id": 1, "top_n": 5})
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert len(items) <= 5
    sims = [i["similarity"] for i in items]
    assert sims == sorted(sims, reverse=True)

def test_match_404():
    assert client.post("/api/match", json={"area_id": 99999}).status_code == 404

def test_ahp_consistency():
    from app.services.ahp import ahp_weights, JUDGE_MATRIX
    assert ahp_weights(JUDGE_MATRIX)["CR"] < 0.1

def test_chat_reply():
    """一次性模式：mock Agent，验证结构与会话字段。"""
    from unittest.mock import patch
    with patch("app.routers.chat.ask",
               return_value={"answer": "测试回复", "steps": []}), \
         patch("app.routers.chat.save_pair"):
        r = client.post("/api/chat/", json={"message": "你好"})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["reply"] == "测试回复"
    assert d["session_id"]
    assert d["tools"] == []


def test_chat_stream():
    """流式模式：验证 SSE 格式与 [DONE] 结尾。"""
    from unittest.mock import patch
    with patch("app.routers.chat.ask",
               return_value={"answer": "掩护式支架", "steps": []}), \
         patch("app.routers.chat.save_pair"):
        r = client.post("/api/chat/", json={"message": "hi", "stream": True})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert "data: 掩护" in r.text.replace("\n\n", "")
    assert "data: [DONE]" in r.text


def test_chat_agent_tools():
    """Agent 工具链透传：tools 字段反映真实调用。"""
    from unittest.mock import patch
    with patch("app.routers.chat.ask",
               return_value={"answer": "推荐ZF15000", 
                             "steps": [("run_matching", {"coal_thickness": 8.8})]}), \
         patch("app.routers.chat.save_pair"):
        r = client.post("/api/chat/", json={"message": "煤层8.8米推荐支架"})
    d = r.json()["data"]
    assert d["tools"] == ["run_matching"]
    assert d["reply"] == "推荐ZF15000"


def test_history_truncation():
    """历史截断：只带最近10轮(20条)进上下文。"""
    from app.db import get_conn
    from app.routers.chat import load_history
    conn = get_conn(); cur = conn.cursor()
    cur.executemany(
        "INSERT INTO chat_messages(session_id,role,content) VALUES ('pytest_trunc',%s,%s)",
        [("user", f"msg{i}") for i in range(25)])
    conn.commit()
    try:
        h = load_history("pytest_trunc")
        assert len(h) == 20
        assert h[0][1] == "msg5"
        assert h[-1][1] == "msg24"
    finally:
        cur.execute("DELETE FROM chat_messages WHERE session_id='pytest_trunc'")
        conn.commit()


    """历史截断：只带最近10轮(20条)进上下文。"""
    from app.db import get_conn
    from app.routers.chat import load_history
    conn = get_conn(); cur = conn.cursor()
    cur.executemany(
        "INSERT INTO chat_messages(session_id,role,content) VALUES ('pytest_trunc',%s,%s)",
        [("user", f"msg{i}") for i in range(25)])
    conn.commit()
    try:
        h = load_history("pytest_trunc")
        assert len(h) == 20
        assert h[0][1] == "msg5"
        assert h[-1][1] == "msg24"
    finally:
        cur.execute("DELETE FROM chat_messages WHERE session_id='pytest_trunc'")
        conn.commit()


def test_support_calc_physics():
    """重算公式物理正确性：缸径320→360，阻力比应=(360/320)^2。"""
    from app.services.support_calc import recalc
    r320 = recalc(320)
    r360 = recalc(360)
    ratio = r360["resistance_kn"] / r320["resistance_kn"]
    assert abs(ratio - (360 / 320) ** 2) < 0.001
    assert r320["resistance_kn"] > r320["single_thrust_kn"]  # η<1? 多柱
    assert r320["note"].startswith("公式法")

def test_knowledge_search():
    """RAG检索：支护强度相关查询应命中MT/T556条款，无关查询应空。"""
    from app.services.knowledge import search
    hits = search("支护强度如何确定")
    assert hits and "556" in hits[0]["source"]
    assert hits[0]["score"] > 0
    assert search("火星殖民政策") == []
