"""对话接口。W17-D7 进阶：Agent 工具调用——从消息提取工况参数，命中则内部调用
CBR 匹配引擎(run_match)，GLM 基于真实匹配结果写选型建议(架构级防幻觉)。"""
import json, re, time, uuid
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.core.response import ok
from app.db import get_conn
from app.services.llm import get_llm
from app.services.matcher import run_match

router = APIRouter()

SYSTEM_PROMPT = """你是"液压支架智能选型助手"，服务于煤矿综采工作面设备选型。
规则：
1. 只回答液压支架选型、综采地质条件分析相关问题，其他话题礼貌拒绝；
2. 涉及具体型号推荐时，说明本回答仅基于通用知识，精确推荐请使用 /api/match 匹配接口；
3. 回答简洁专业，不超过 300 字。"""

EXTRACT_PROMPT = """从用户消息中提取液压支架选型工况参数，只输出JSON，不要任何其他文字：
{"coal_thickness": 煤层厚度米数或null, "dip_angle": 倾角度数或null}
用户消息："""

ADVISE_PROMPT = """用户工况：{message}

CBR匹配引擎已在案例库中检索，Top结果（真实案例数据）：
{summary}

请基于以上真实匹配结果给出选型建议：首选推荐相似度排名第1的案例用架（说明推荐理由：相似案例条件与差异），备选推荐第2、3名，并给出工作阻力等级与注意事项。
只允许使用上面列出的型号和数据，禁止编造其他型号。不超过300字。"""

HISTORY_ROUNDS = 10

class ChatReq(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None
    stream: bool = False

def load_history(session_id: str) -> list[tuple[str, str]]:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content FROM chat_messages WHERE session_id=%s ORDER BY id DESC LIMIT %s",
            (session_id, HISTORY_ROUNDS * 2))
        return [(r["role"], r["content"]) for r in reversed(cur.fetchall())]
    finally:
        conn.close()

def save_pair(session_id: str, question: str, answer: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO chat_messages(session_id, role, content) VALUES (%s,%s,%s)",
            [(session_id, "user", question), (session_id, "assistant", answer)])
        conn.commit()
    finally:
        conn.close()

def extract_params(message: str) -> dict:
    """LLM 参数提取：煤层厚度/倾角。任何失败都安全降级为 None。"""
    try:
        txt = get_llm().invoke([("human", EXTRACT_PROMPT + message)]).content
        m = re.search(r"\{.*\}", txt, re.S)
        d = json.loads(m.group(0)) if m else {}
        ct, da = d.get("coal_thickness"), d.get("dip_angle")
        return {"coal_thickness": float(ct) if ct else None,
                "dip_angle": float(da) if da is not None else None}
    except Exception:
        return {"coal_thickness": None, "dip_angle": None}

def summarize(items: list[dict]) -> str:
    lines = []
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. 案例:{it.get('area_name')} 用架:{it.get('support_model')} "
                     f"阻力:{it.get('working_resistance')}kN 相似度:{it.get('similarity')} "
                     f"差异:{'; '.join(it.get('diffs', []))}")
    return "\n".join(lines)

def agent_match(message: str):
    """Agent 主流程：提取参数→有效则调CBR引擎。返回 match_data 或 None。"""
    params = extract_params(message)
    ct = params["coal_thickness"]
    if ct and 0.5 < ct < 12:
        try:
            data = run_match(coal_thickness=ct, dip_angle=params["dip_angle"] or 0, top_n=3)
            return data if data["items"] else None
        except Exception:
            return None
    return None

def build_msgs(session_id: str, message: str, match_data: dict | None):
    history = load_history(session_id)
    if match_data:
        content = ADVISE_PROMPT.format(message=message, summary=summarize(match_data["items"]))
    else:
        content = message
    return [("system", SYSTEM_PROMPT)] + history + [("user", content)]

def sse_gen(msgs, session_id, question):
    parts = []
    try:
        for chunk in get_llm().stream(msgs):
            if chunk.content:
                parts.append(chunk.content)
                yield f"data: {chunk.content}\n\n"
    except Exception as e:
        yield f"data: [ERROR] {type(e).__name__}\n\n"
    finally:
        if parts:
            save_pair(session_id, question, "".join(parts))
        yield "data: [DONE]\n\n"

@router.post("/")
def chat_endpoint(req: ChatReq):
    sid = req.session_id or uuid.uuid4().hex[:16]
    match_data = agent_match(req.message)
    msgs = build_msgs(sid, req.message, match_data)
    if req.stream:
        return StreamingResponse(
            sse_gen(msgs, sid, req.message),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
    reply = get_llm().invoke(msgs).content
    save_pair(sid, req.message, reply)
    resp = {"reply": reply, "session_id": sid, "matched": bool(match_data)}
    if match_data:
        resp["matches"] = [{"model": it["support_model"], "similarity": it["similarity"],
                            "area": it.get("area_name"), "wr": it.get("working_resistance")}
                           for it in match_data["items"]]
    return ok(resp)


# ---- W17-D3 SSE 实验端点（验收后可删）----
@router.get("/stream_demo")
def stream_demo():
    def gen():
        for ch in "液压支架选型需考虑煤层厚度、倾角、瓦斯等级。":
            yield f"data: {ch}\n\n"
            time.sleep(0.05)
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
