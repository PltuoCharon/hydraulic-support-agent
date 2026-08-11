"""引导式选型对话状态机。W19。
D2: 骨架（节点占位）。D3 填 collect，D4 条件边，D5 recommend+explain，D6 记忆。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from langgraph.graph import StateGraph, START, END
from app.guide.state import GuideState

def collect(state: GuideState) -> dict:
    """节点1 参数收集（D3 实现）：LLM 抽参数 + 缺什么问什么。"""
    return {"stage": "collect"}

def confirm(state: GuideState) -> dict:
    """节点 参数确认（D4 实现）：复述参数请用户确认。"""
    return {"stage": "confirm"}

def recommend(state: GuideState) -> dict:
    """节点2 推荐（D5 实现）：调 run_matching。"""
    return {"stage": "recommend"}

def explain(state: GuideState) -> dict:
    """节点 解释（D5 实现）：LLM 基于工具返回组织语言。"""
    return {"stage": "explain"}

def route(state: GuideState) -> str:
    """条件边（D4 实现）：先占位直通。"""
    return "collect"

def build_graph():
    g = StateGraph(GuideState)
    g.add_node("collect", collect)
    g.add_node("confirm", confirm)
    g.add_node("recommend", recommend)
    g.add_node("explain", explain)
    g.add_edge(START, "collect")
    g.add_edge("collect", END)      # D4 换成条件边
    return g.compile()

if __name__ == "__main__":
    graph = build_graph()
    out = graph.invoke({"messages": [("user", "帮我推荐支架")]})
    print("骨架跑通, stage =", out["stage"])
