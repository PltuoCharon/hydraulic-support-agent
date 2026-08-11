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
    return {
        "reply": reply,
        "session_id": sid,
        "stage": stage,
        "params": state.get("params", {}),
        "missing": state.get("missing", []),
        "tools": ["run_matching"] if stage == "explained" else [],
    }


@router.post("/")
def chat_endpoint(req: ChatReq):
    data = _run_turn(req)
    if not req.stream:
        return ok(data)

    def gen():
        for i in range(0, len(data["reply"]), 4):
            yield f"data: {json.dumps({'chunk': data['reply'][i:i+4]}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'session_id': data['session_id'], 'stage': data['stage']}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
