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

def test_guide_collect():
    """collect节点：抽到煤厚→追问倾角；抽全→不追问。"""
    from unittest.mock import patch
    import app.guide.graph as gg
    class FakeResp:
        def __init__(self, c): self.content = c
    class FakeLLM:
        def __init__(self): self.n = 0
        def invoke(self, msgs):
            self.n += 1
            # 第一次是抽参数，第二次是追问话术
            return FakeResp('{"coal_thickness": 8.8}' if self.n == 1 else "请问倾角和瓦斯等级？")
    fake = FakeLLM()
    with patch.object(gg, "get_llm", return_value=fake):
        out = gg.collect({"messages": [("user", "煤层8.8米")], "params": {}})
    assert out["params"]["coal_thickness"] == 8.8
    assert out["missing"] == ["dip_angle", "gas_level"]
    assert "倾角" in out["messages"][-1][1]

def test_guide_route():
    """条件边：缺参→ask；等确认+肯定→recommend；等确认+改口→confirm。"""
    from app.guide.graph import route
    assert route({"missing": ["dip_angle"]}) == "ask"
    assert route({"missing": [], "stage": "confirm_pending",
                  "_changed": False, "messages": [("user", "对的")]}) == "recommend"
    assert route({"missing": [], "stage": "confirm_pending",
                  "_changed": True, "messages": [("user", "倾角改成10度")]}) == "confirm"
    assert route({"missing": [], "stage": "collect",
                  "messages": [("user", "煤层8米倾角2度低瓦斯")]}) == "confirm"

def test_guide_recommend():
    """recommend 节点: 真实调 run_match 拿到候选。"""
    from app.guide.graph import recommend
    out = recommend({"params": {"coal_thickness": 8.8, "dip_angle": 2.0}})
    assert out["stage"] == "explain"
    assert out["match_result"]

def test_guide_checkpointer():
    """MemorySaver: 同 thread_id 跨轮记住参数; 不同 thread_id 互不干扰。"""
    from unittest.mock import patch
    import app.guide.graph as gg
    class FakeResp:
        def __init__(self, c): self.content = c
    class FakeLLM:
        def __init__(self): self.calls = []
        def invoke(self, msgs):
            s = msgs if isinstance(msgs, str) else str(msgs)
            self.calls.append(s)
            # 抽取类 prompt 含"用户消息:", 按其中用户输入决定返回
            if "用户消息:" in s:
                if "倾角2度" in s:
                    return FakeResp('{"dip_angle": 2, "gas_level": "低瓦斯"}')
                return FakeResp('{"coal_thickness": 8.8}')
            return FakeResp("追问话术")
    fake = FakeLLM()
    with patch.object(gg, "get_llm", return_value=fake):
        graph = gg.build_graph()
        s1 = gg.chat_once(graph, "t-1", "煤层8.8米")
        assert s1["missing"]                          # 还缺倾角/瓦斯
        s2 = gg.chat_once(graph, "t-1", "倾角2度，低瓦斯")
        assert not s2["missing"]                      # 跨轮记住了煤厚
        assert s2["params"]["coal_thickness"] == 8.8
        s3 = gg.chat_once(graph, "t-2", "煤层8.8米")  # 新会话从零开始
        assert s3["missing"]

def test_guide_api():
    """/api/guide: 首轮追问, 返回 session_id; 同 session 二轮补齐进确认。"""
    from unittest.mock import patch
    import app.guide.graph as gg
    import app.routers.guide as gr
    class FakeResp:
        def __init__(self, c): self.content = c
    class FakeLLM:
        def invoke(self, msgs):
            s = msgs if isinstance(msgs, str) else str(msgs)
            if "用户消息:" in s:
                if "倾角2度" in s:
                    return FakeResp('{"dip_angle": 2, "gas_level": "低瓦斯"}')
                return FakeResp('{"coal_thickness": 8.8}')
            return FakeResp("请问倾角和瓦斯等级？")
    with patch.object(gg, "get_llm", return_value=FakeLLM()):
        gr._GRAPH = gg.build_graph()
        r1 = client.post("/api/guide", json={"message": "煤层8.8米"})
        assert r1.status_code == 200
        d1 = r1.json()["data"]
        assert d1["session_id"] and d1["missing"]
        r2 = client.post("/api/guide", json={"message": "倾角2度，低瓦斯",
                                             "session_id": d1["session_id"]})
        d2 = r2.json()["data"]
        assert d2["stage"] == "confirm_pending"
        assert d2["params"]["coal_thickness"] == 8.8
