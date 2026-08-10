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
    # 只验证接口结构，不验证LLM内容（避免测试依赖外部服务）
    from unittest.mock import patch
    class FakeResp:
        content = "测试回复"
    class FakeLLM:
        def invoke(self, msgs): return FakeResp()
    with patch("app.routers.chat.get_llm", return_value=FakeLLM()), \
         patch("app.routers.chat.save_pair"):
        r = client.post("/api/chat/", json={"message": "你好"})
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 0
    assert body["data"]["reply"] == "测试回复"
    assert body["data"]["session_id"]

def test_chat_stream():
    """流式模式：验证 SSE 格式与 [DONE] 结尾，不真调 LLM。"""
    from unittest.mock import patch
    class FakeChunk:
        def __init__(self, c): self.content = c
    class FakeLLM:
        def stream(self, msgs):
            return iter([FakeChunk("掩"), FakeChunk("护式"), FakeChunk("")])
    with patch("app.routers.chat.get_llm", return_value=FakeLLM()), patch("app.routers.chat.save_pair"):
        r = client.post("/api/chat/", json={"message": "hi", "stream": True})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert "data: 掩\n\n" in r.text
    assert "data: [DONE]" in r.text
    assert "data: \n\n" not in r.text   # 空 chunk 被过滤

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
