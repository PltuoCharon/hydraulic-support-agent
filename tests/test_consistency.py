"""W28-D5: 两路径一致性测试。
命题: HTTP API 路径(routers/match.py → matcher.run_match → matching) 与
Agent 工具路径(tools.run_matching → matching.match_by_params) 对同一工况
返回相同的 Top-5(型号+顺序)。10 组工况, 10/10 一致才过。
若未来某次改动导致不一致, 说明两路径出现逻辑分叉, 必须修回单点实现。"""
import re
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.agent.tools import run_matching

client = TestClient(app)

# 覆盖: 薄煤层/中厚/厚煤层/放顶煤, 近水平~缓斜; 均在 (0.5,25) 有效域内
CONDITIONS = [
    (1.3, 0), (2.2, 3), (3.5, 8), (4.5, 5), (5.0, 12),
    (6.8, 2), (8.8, 2), (10.0, 1), (15.0, 0), (22.0, 3),
]

@pytest.mark.parametrize("coal_thickness,dip_angle", CONDITIONS)
def test_api_and_agent_tool_give_same_top5(coal_thickness, dip_angle):
    # 路径A: HTTP API
    r = client.post("/api/match/", json={
        "coal_thickness": coal_thickness, "dip_angle": dip_angle, "top_n": 5})
    assert r.status_code == 200, r.text
    api_models = [it["support_model"] for it in r.json()["data"]["items"]]

    # 路径B: Agent 工具(返回格式化文本, 解析出型号序列)
    text = run_matching.invoke({"coal_thickness": coal_thickness,
                                "dip_angle": dip_angle, "top_n": 5})
    tool_models = re.findall(r"实际用架 (\S+?)，", text)

    assert api_models == tool_models, (
        f"两路径不一致 @煤厚{coal_thickness}m/倾角{dip_angle}°:\n"
        f"  API: {api_models}\n  工具: {tool_models}")

def test_both_paths_reject_out_of_range():
    """边界行为也要一致: 越界输入两路径都不应返回推荐"""
    r = client.post("/api/match/", json={"coal_thickness": 99, "top_n": 5})
    assert r.status_code == 422
    text = run_matching.invoke({"coal_thickness": 99})
    assert "参数错误" in text
