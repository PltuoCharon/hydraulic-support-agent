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

class _FakeResp:
    def __init__(self, c): self.content = c

class _GuideFakeLLM:
    def invoke(self, msgs):
        s = msgs if isinstance(msgs, str) else str(msgs)
        if "用户消息:" in s:
            user_text = s.split("用户消息:")[-1]
            if "倾角" in user_text:
                return _FakeResp('{"coal_thickness": 8.8, "dip_angle": 2, "gas_level": "低瓦斯"}')
            return _FakeResp('{"coal_thickness": 8.8}')
        return _FakeResp("请问倾角和瓦斯等级？")


def test_chat_reply():
    """一次性模式: 状态机引导追问, 结构与会话字段。"""
    from unittest.mock import patch
    import app.guide.graph as gg
    import app.routers.chat as rc
    with patch.object(gg, "get_llm", return_value=_GuideFakeLLM()), \
         patch.object(rc, "save_pair"):
        r = client.post("/api/chat/", json={"message": "煤层8.8米"})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["session_id"] and d["reply"]
    assert d["missing"]                       # 缺倾角/瓦斯, 进入引导


def test_chat_stream():
    """流式模式: SSE 格式与 [DONE] 结尾。"""
    from unittest.mock import patch
    import app.guide.graph as gg
    import app.routers.chat as rc
    with patch.object(gg, "get_llm", return_value=_GuideFakeLLM()), \
         patch.object(rc, "save_pair"):
        r = client.post("/api/chat/", json={"message": "煤层8.8米", "stream": True})
    body = r.text
    assert "data:" in body and "[DONE]" in body


def test_chat_tools_passthrough():
    """tools 字段: 走完确认进入推荐时为 ["run_matching"]。"""
    from unittest.mock import patch
    import app.guide.graph as gg
    import app.routers.chat as rc
    with patch.object(gg, "get_llm", return_value=_GuideFakeLLM()), \
         patch.object(gg, "chat", return_value="推荐说明"), \
         patch.object(rc, "save_pair"):
        r1 = client.post("/api/chat/", json={"message": "倾角2度煤层8.8米低瓦斯"})
        d1 = r1.json()["data"]
        assert d1["stage"] == "confirm_pending"
        r2 = client.post("/api/chat/", json={"message": "对",
                                             "session_id": d1["session_id"]})
        d2 = r2.json()["data"]
        assert d2["stage"] == "explained"
        assert d2["tools"] == ["run_matching"]


def test_chat_messages_saved():
    """一问一答落库两条(真实DB)。"""
    from unittest.mock import patch
    import app.guide.graph as gg
    from app.db import get_conn
    with patch.object(gg, "get_llm", return_value=_GuideFakeLLM()):
        r = client.post("/api/chat/", json={"message": "煤层8.8米"})
    sid = r.json()["data"]["session_id"]
    conn = get_conn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT COUNT(*) AS n FROM chat_messages WHERE session_id=%s", (sid,))
            row = c.fetchone()
            assert (row["n"] if isinstance(row, dict) else row[0]) == 2
    finally:
        conn.close()

def test_match_has_source():
    """溯源: 匹配候选带 source(案例库·矿区·工作面)。"""
    from app.services.matcher import run_match
    r = run_match(coal_thickness=8.8, dip_angle=2.0, top_n=3)
    assert all("source" in it and "案例库" in it["source"] for it in r["items"])

def test_knowledge_has_source():
    """溯源: 知识检索带 source/loc。"""
    from app.services.knowledge import search
    rs = search("支护强度")
    assert rs and all("source" in r for r in rs)

def test_recalc_has_source():
    """溯源: 公式估算带依据说明。"""
    from app.services.support_calc import recalc
    r = recalc(bore_mm=360)
    assert "source" in r and "估算" in r["source"]
