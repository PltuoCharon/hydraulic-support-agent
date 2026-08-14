"""对话接口。W20-D1: 回答生成由 LangGraph 引导式状态机接管。

- 外壳不变: session_id / stream / chat_messages 持久化;
- 与 /api/guide 共享同一图实例(同一 MemorySaver), 会话状态互通;
- data.tools: 本轮完成推荐时为 ["run_matching"], 否则 [];
- data 新增 stage/params/missing, 便于前端展示进度。
"""
import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.response import ok
from app.db import get_conn
from app.guide.graph import chat_once
from app.routers.guide import _graph

router = APIRouter()

# ===== W24-D5 追问分支：'为什么推荐它' 等意图，复用已收参数回执推荐理由+出处 =====
WHY_KEYWORDS = ("为什么", "原因", "依据", "理由", "为何", "解释", "怎么推荐")
_SESSION_PARAMS = {}   # sid -> params（内存缓存；重启后丢失，可接受）

def _explain_recommendation(sid, params):
    """复用已收参数重新匹配，给出推荐理由 + 案例出处。失败返回 None（fallback 状态机）。"""
    if not params:
        return None
    try:
        from app.services.matcher import run_match
        H = float(params.get("coal_thickness"))
        d = float(params.get("dip_angle") or 0)
        g = params.get("gas_level") or ""
        res = run_match(coal_thickness=H, dip_angle=d, top_n=3)
        if not res.get("items"):
            return None
        top = res["items"][0]
        sim = round((top.get("similarity") or 0) * 100)
        reply = (
            f"根据您提供的工况（煤层厚度 {H} m、倾角 {d}°、瓦斯等级 {g}），"
            f"系统在案例库 {res['total']} 个相似工况中匹配出最合适的支架："
            f"**{top['support_model']}**（相似度 {sim}%）。\n\n"
            f"该支架工作阻力 {top.get('working_resistance')} kN、"
            f"支护强度 {top.get('intensity')} MPa。\n\n"
            f"推荐依据：案例库中 **{top.get('area_name')}·{top.get('working_face_name')}** 工作面的实际使用经验"
            f"（数据来源：{top.get('source')}）。"
        )
        return {
            "reply": reply,
            "session_id": sid,
            "stage": "explained",
            "params": params,
            "missing": [],
            "tools": ["run_matching"],
        }
    except Exception as e:
        print(f"[chat] 为什么分支失败: {e}")
        return None



class ChatReq(BaseModel):
    message: str
    session_id: str | None = None
    stream: bool = False


def save_pair(session_id: str, user_msg: str, ai_msg: str):
    """一问一答落库(两条)。"""
    conn = get_conn()
    try:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO chat_messages(session_id, role, content) "
                "VALUES (%s,'user',%s),(%s,'assistant',%s)",
                (session_id, user_msg, session_id, ai_msg))
        conn.commit()
    finally:
        conn.close()


def _run_turn(req: ChatReq) -> dict:
    """跑一轮状态机, 返回统一 data。"""
    sid = req.session_id or uuid.uuid4().hex[:12]
    try:
        state = chat_once(_graph(), sid, req.message)
    except Exception as e:
        print(f"[chat] 状态机意外错误: {e}")
        return {"reply": "系统处理出现异常，请重发消息或换个说法。",
                "session_id": sid, "stage": "error",
                "params": {}, "missing": [], "tools": []}
    last = state["messages"][-1]
    reply = last.content if hasattr(last, "content") else str(last[1])
    save_pair(sid, req.message, reply)
    stage = state.get("stage", "")
    data = {
        "reply": reply,
        "session_id": sid,
        "stage": stage,
        "params": state.get("params", {}),
        "missing": state.get("missing", []),
        "tools": ["run_matching"] if stage == "explained" else [],
    }
    if data.get("params"):
        _SESSION_PARAMS[sid] = data["params"]
    return data


@router.post("/")
def chat_endpoint(req: ChatReq):
    # W24-D5 追问分支：'为什么' 意图且已有参数缓存 → 直接回执推荐理由+出处
    if req.session_id and any(k in req.message for k in WHY_KEYWORDS):
        why = _explain_recommendation(req.session_id, _SESSION_PARAMS.get(req.session_id))
        if why is not None:
            save_pair(req.session_id, req.message, why["reply"])
            if not req.stream:
                return ok(why)
            def why_gen():
                for i in range(0, len(why["reply"]), 4):
                    yield f"data: {json.dumps({'chunk': why['reply'][i:i+4]}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'session_id': why['session_id'], 'stage': why['stage'], 'params': why['params'], 'missing': why['missing'], 'tools': why['tools']}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(why_gen(), media_type="text/event-stream")
    data = _run_turn(req)
    if not req.stream:
        return ok(data)

    def gen():
        for i in range(0, len(data["reply"]), 4):
            yield f"data: {json.dumps({'chunk': data['reply'][i:i+4]}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'session_id': data['session_id'], 'stage': data['stage'], 'params': data['params'], 'missing': data['missing'], 'tools': data['tools']}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
