"""引导式选型对话状态机。W19。
D2: 骨架。D3: collect节点(LLM抽参数+确定性算缺失+LLM追问)。D4 条件边。D5 推荐+解释。D6 记忆。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import json, re
from langgraph.graph import StateGraph, START, END
from app.guide.state import GuideState, calc_missing, PARAM_LABELS
from app.services.llm import get_llm

EXTRACT_PROMPT = """从用户的这句话中提取液压支架选型工况参数，只输出JSON，不要其他文字：
{"coal_thickness": 煤层厚度米数(float)或null, "dip_angle": 煤层倾角度数(float)或null,
 "gas_level": "低瓦斯"/"高瓦斯"/"突出"或null}
已知参数(不要重复提取除非用户改口): {known}
规则：只提取用户明确说的数值，不确定就 null；瓦斯只取三个标准等级之一。
用户的话："""

ASK_PROMPT = """你是液压支架选型顾问，正在收集工况参数。
已知参数: {known}
还缺: {missing}
请自然地追问缺失项(以第一项为主)，一两句话即可，不要重复询问已知项，不要解释原因。"""

def extract_params(text: str, known: dict) -> dict:
    """LLM 抽参数，任何失败安全降级为空 dict。"""
    try:
        prompt = EXTRACT_PROMPT.format(known=json.dumps(known, ensure_ascii=False)) + text
        txt = get_llm().invoke([("human", prompt)]).content
        m = re.search(r"\{.*\}", txt, re.S)
        d = json.loads(m.group(0)) if m else {}
        out = {}
        for k in ("coal_thickness", "dip_angle", "gas_level"):
            v = d.get(k)
            if v in (None, ""):
                continue
            if k == "gas_level":
                if v in ("低瓦斯", "高瓦斯", "突出"):
                    out[k] = v
            else:
                out[k] = float(v)
        return out
    except Exception:
        return {}

def collect(state: GuideState) -> dict:
    """节点1 参数收集：抽参数→合并→算缺失→缺则LLM追问。"""
    params = dict(state.get("params") or {})
    last = state["messages"][-1].content if state.get("messages") else ""
    params.update(extract_params(last, params))
    missing = calc_missing(params)
    if missing:
        ask_txt = get_llm().invoke([("human", ASK_PROMPT.format(
            known=json.dumps(params, ensure_ascii=False),
            missing="、".join(PARAM_LABELS[m] for m in missing)))]).content
        return {"params": params, "missing": missing, "stage": "collect",
                "messages": [("assistant", ask_txt)]}
    return {"params": params, "missing": [], "stage": "collect"}

def confirm(state: GuideState) -> dict:
    return {"stage": "confirm"}

def recommend(state: GuideState) -> dict:
    return {"stage": "recommend"}

def explain(state: GuideState) -> dict:
    return {"stage": "explain"}

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
    print("=== 只给煤层厚度 ===")
    out = graph.invoke({"messages": [("user", "我的综放面煤层厚度8.8米")]})
    print("params:", out.get("params"))
    print("missing:", out.get("missing"))
    print("助手追问:", out["messages"][-1].content)
