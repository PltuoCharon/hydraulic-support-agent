"""引导式选型对话状态机。W19。
D3: collect节点。D4: 条件边+confirm节点(三路分叉: 追问/确认/推荐)。"""
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

AFFIRM_WORDS = ("是", "对", "嗯", "好", "确认", "可以", "没错", "行", "ok", "OK")

def _last_text(state: GuideState) -> str:
    if not state.get("messages"):
        return ""
    m = state["messages"][-1]
    return m.content if hasattr(m, "content") else m[1]

def _is_affirm(text: str) -> bool:
    """肯定判定：以肯定词开头且不含数字(含数字视为改口)。"""
    t = text.strip()
    return t.startswith(AFFIRM_WORDS) and not re.search(r"\d", t)

def extract_params(text: str, known: dict) -> dict:
    try:
        prompt = EXTRACT_PROMPT.replace("{known}", json.dumps(known, ensure_ascii=False)) + text
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
    except Exception as e:
        print(f"[extract_params 降级] {type(e).__name__}: {e}")
        return {}

def collect(state: GuideState) -> dict:
    """节点1 参数收集：抽参数→合并→算缺失→缺则LLM追问。_changed标记供路由。"""
    params = dict(state.get("params") or {})
    new = extract_params(_last_text(state), params)
    params.update(new)
    missing = calc_missing(params)
    result = {"params": params, "missing": missing, "_changed": bool(new)}
    if missing:
        ask_txt = get_llm().invoke([("human", ASK_PROMPT.format(
            known=json.dumps(params, ensure_ascii=False),
            missing="、".join(PARAM_LABELS[m] for m in missing)))]).content
        result["stage"] = "collect"
        result["messages"] = [("assistant", ask_txt)]
    return result

def confirm(state: GuideState) -> dict:
    """节点 参数确认：复述参数请用户确认(模板生成,不走LLM,保证数字零失真)。"""
    p = state.get("params", {})
    lines = [f"- {PARAM_LABELS[k]}: {p[k]}" for k in PARAM_LABELS if p.get(k) not in (None, "")]
    txt = "请确认工况参数：\n" + "\n".join(lines) + "\n对吗？(可回复\"对\"或直接改口，如\"倾角是10度\")"
    return {"stage": "confirm_pending", "confirmed": False,
            "messages": [("assistant", txt)]}

def recommend(state: GuideState) -> dict:
    """节点2 推荐（D5 填真实逻辑）。"""
    return {"stage": "recommend", "confirmed": True,
            "messages": [("assistant", "参数已确认，进入匹配推荐（D5实现）")]}

def explain(state: GuideState) -> dict:
    return {"stage": "explain"}

def route(state: GuideState) -> str:
    """条件边：缺参数→END等用户；等确认+用户肯定且未改数→recommend；否则→confirm。"""
    if state.get("missing"):
        return "ask"
    if (state.get("stage") == "confirm_pending"
            and not state.get("_changed")
            and _is_affirm(_last_text(state))):
        return "recommend"
    return "confirm"

def build_graph():
    g = StateGraph(GuideState)
    g.add_node("collect", collect)
    g.add_node("confirm", confirm)
    g.add_node("recommend", recommend)
    g.add_node("explain", explain)
    g.add_edge(START, "collect")
    g.add_conditional_edges("collect", route,
                            {"ask": END, "confirm": "confirm", "recommend": "recommend"})
    g.add_edge("confirm", END)
    g.add_edge("recommend", END)
    return g.compile()

if __name__ == "__main__":
    graph = build_graph()
    print("=== 轮1: 只给煤厚 ===")
    out = graph.invoke({"messages": [("user", "煤层厚度8.8米")]})
    print("助手:", out["messages"][-1].content if hasattr(out["messages"][-1], "content") else out["messages"][-1][1])
    print("=== 轮2: 补齐 ===")
    out = graph.invoke({**out, "messages": [("user", "倾角2度，低瓦斯")]})
    m = out["messages"][-1]
    print("助手:", m.content if hasattr(m, "content") else m[1])
    print("=== 轮3: 确认 ===")
    out = graph.invoke({**out, "messages": [("user", "对的")]})
    m = out["messages"][-1]
    print("stage:", out.get("stage"), "| 助手:", m.content if hasattr(m, "content") else m[1])
