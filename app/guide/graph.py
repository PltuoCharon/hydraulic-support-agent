"""LangGraph 对话状态机：参数收集 → 确认 → 推荐 → 解释。

D5: recommend 调 run_match 拿真实匹配结果; explain 让 LLM 仅基于
工具返回的 JSON 组织语言——数字不经过 LLM 生成, 只做复述。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.guide.state import GuideState, PARAM_LABELS, calc_missing
from app.services.llm import get_llm, chat

EXTRACT_PROMPT = """从用户消息中抽取液压支架选型工况参数，只输出 JSON。
已知参数: {known}
可抽取字段: coal_thickness(煤层厚度,米,数值), dip_angle(煤层倾角,度,数值),
gas_level(瓦斯等级,取值为"低瓦斯"/"高瓦斯"/"突出"之一)。
用户消息: {text}
只输出 JSON 对象，没有的字段不要出现，例如: {{"coal_thickness": 8.8}}"""

ASK_PROMPT = """你是液压支架选型助手。已知参数: {known}。
还缺少: {missing}。请用一句话自然地向用户追问这些参数，不要解释，不要编造数值。"""

EXPLAIN_PROMPT = """你是液压支架选型助手。下面是匹配引擎对工况参数 {params} 的真实检索结果(JSON)：
{result}
请基于且仅基于这份 JSON 向用户讲解推荐结论：
1. 先报最推荐型号及其相似度，再简列其余候选；
2. 相似度、型号、工况数值必须与 JSON 一字不差，禁止编造任何数字；
3. 每条推荐后括注来源(取 JSON 中的 source 字段), 如"依据: 案例库·兴隆庄4301";
4. 末尾提示"以上为案例匹配结果，供参考"。
不超过300字。"""

AFFIRM_WORDS = ("是", "对", "嗯", "好", "确认", "可以", "没错", "行", "ok", "OK")


def _last_text(state) -> str:
    """取最后一条用户消息的纯文本。"""
    for m in reversed(state.get("messages", [])):
        if isinstance(m, tuple):
            role, text = m
        else:
            role = getattr(m, "type", None) or getattr(m, "role", None)
            text = getattr(m, "content", "")
        if role in ("user", "human"):
            return str(text)
    return ""


def _is_affirm(text: str) -> bool:
    """纯肯定（不含数字——含数字视为改口）。"""
    t = text.strip()
    if any(c.isdigit() for c in t):
        return False
    return any(t.startswith(w) for w in AFFIRM_WORDS)


def _chat(llm, prompt: str) -> str:
    """统一调用入口: 兼容 .invoke 返回对象/字符串, 便于 mock。"""
    r = llm.invoke(prompt)
    return r.content if hasattr(r, "content") else str(r)


def _parse_json(text: str) -> dict:
    """剥离 ```json 围栏, 取第一个 {...} 块。"""
    import re as _re
    m = _re.search(r"\{.*\}", text, _re.S)
    return json.loads(m.group(0)) if m else {}


def extract_params(text: str, known: dict) -> dict:
    """LLM 抽取参数；解析失败返回 {}。"""
    llm = get_llm()
    prompt = (EXTRACT_PROMPT
              .replace("{known}", json.dumps(known, ensure_ascii=False))
              .replace("{text}", text))
    try:
        return _parse_json(_chat(llm, prompt))
    except Exception as e:
        print(f"[extract] 解析失败: {e}")
        return {}


def collect(state: GuideState) -> dict:
    llm = get_llm()
    """参数收集节点: 抽取→合并→缺则追问。"""
    text = _last_text(state)
    params = dict(state.get("params", {}))
    # 领域闸: 无任何已知参数且消息不含数字(工况数值), 视为越界问题拒答
    if not params and not any(c.isdigit() for c in text):
        return {"messages": [("ai", "我是液压支架选型助手，只能回答选型相关问题。"
                                    "请提供工况参数，如\"煤层厚度8.8米\"。")],
                "stage": "collect", "missing": calc_missing(params)}
    new = extract_params(text, params)
    params.update({k: v for k, v in new.items() if v is not None})
    missing = calc_missing(params)
    out = {"params": params, "missing": missing, "_changed": bool(new)}
    if missing:
        known = json.dumps(params, ensure_ascii=False)
        miss_labels = "、".join(PARAM_LABELS[m] for m in missing)
        reply = _chat(llm, ASK_PROMPT.replace("{known}", known)
                                   .replace("{missing}", miss_labels))
        out["messages"] = [("ai", reply)]
        out["stage"] = "collect"
    return out


def confirm(state: GuideState) -> dict:
    """确认节点: 模板复述——数字不经过 LLM, 与抽取结果一字不差。"""
    params = state.get("params", {})
    lines = "\n".join(f"- {PARAM_LABELS[k]}: {params[k]}" for k in params if k in PARAM_LABELS)
    reply = (f"请确认工况参数：\n{lines}\n"
             '对吗？(可回复"对"或直接改口，如"倾角是10度")')
    return {"messages": [("ai", reply)], "stage": "confirm_pending"}


def recommend(state: GuideState) -> dict:
    """推荐节点: 调真实匹配引擎 run_match, 结果存 state。"""
    from app.services.matcher import run_match
    params = state.get("params", {})
    try:
        result = run_match(coal_thickness=params.get("coal_thickness"),
                           dip_angle=params.get("dip_angle"), top_n=3)
    except (ValueError, LookupError) as e:
        return {"messages": [("ai", f"匹配失败：{e}，请调整参数后重试。")],
                "stage": "recommend_failed"}
    except Exception as e:
        print(f"[recommend] 意外错误: {e}")
        return {"messages": [("ai", "匹配引擎暂时不可用，请稍后重发\"对\"重试。")],
                "stage": "recommend_failed"}
    if not result.get("items"):
        return {"messages": [("ai", "案例库中没有找到相似工况的案例，"
                                    "可调整参数(如煤层厚度)后重试。")],
                "stage": "recommend_failed"}
    return {"match_result": result, "stage": "explain"}


def explain(state: GuideState) -> dict:
    """解释节点: LLM 仅复述 match_result 的 JSON, 数字零生成。"""
    params = state.get("params", {})
    result = state.get("match_result", {})
    prompt = (EXPLAIN_PROMPT
              .replace("{params}", json.dumps(params, ensure_ascii=False))
              .replace("{result}", json.dumps(result, ensure_ascii=False, default=str)))
    reply = chat(prompt)
    return {"messages": [("ai", reply)], "stage": "explained"}


def route(state: GuideState) -> str:
    """条件边: 缺参→ask; 等确认+纯肯定→recommend; 其余→confirm。"""
    if state.get("missing"):
        return "ask"
    if state.get("stage") == "confirm_pending":
        if not state.get("_changed") and _is_affirm(_last_text(state)):
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
    g.add_edge("recommend", "explain")
    g.add_edge("explain", END)
    return g.compile(checkpointer=MemorySaver())


def chat_once(graph, session_id: str, text: str) -> dict:
    """单轮对话: checkpointer 按 thread_id 自动续历史, 返回新状态。"""
    config = {"configurable": {"thread_id": session_id}}
    return graph.invoke({"messages": [("user", text)]}, config)


if __name__ == "__main__":
    graph = build_graph()
    sid = "demo-001"
    turns = ["煤层厚度8.8米",
             "倾角2度，低瓦斯",
             "对的"]
    for i, t in enumerate(turns, 1):
        print(f"=== 轮{i}: {t} ===")
        state = chat_once(graph, sid, t)
        last = state["messages"][-1]
        print("stage:", state.get("stage"), "| 助手:",
              last.content if hasattr(last, "content") else last)
    # 会话隔离验证: 换 thread_id 应从零开始
    print("=== 新会话 demo-002 ===")
    state = chat_once(graph, "demo-002", "你好")
    last = state["messages"][-1]
    print("stage:", state.get("stage"), "| 助手:",
          last.content if hasattr(last, "content") else last)
