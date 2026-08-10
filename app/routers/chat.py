"""对话接口。W17-D5：session_id 会话管理，chat_messages 表存历史，最近10轮进上下文。"""
import time, uuid
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.core.response import ok
from app.db import get_conn
from app.services.llm import get_llm

router = APIRouter()

SYSTEM_PROMPT = """你是"液压支架智能选型助手"，服务于煤矿综采工作面设备选型。
规则：
1. 只回答液压支架选型、综采地质条件分析相关问题，其他话题礼貌拒绝；
2. 涉及具体型号推荐时，说明本回答仅基于通用知识，精确推荐请使用 /api/match 匹配接口；
3. 回答简洁专业，不超过 300 字。"""

HISTORY_ROUNDS = 10   # 只带最近10轮(20条)，防 token 膨胀

class ChatReq(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None
    stream: bool = False

def load_history(session_id: str) -> list[tuple[str, str]]:
    """最近 HISTORY_ROUNDS*2 条，按时间正序返回 LangChain 消息元组。"""
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
    """一问一答两条落库。"""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO chat_messages(session_id, role, content) VALUES (%s,%s,%s)",
            [(session_id, "user", question), (session_id, "assistant", answer)])
        conn.commit()
    finally:
        conn.close()

def build_msgs(session_id: str, message: str):
    return [("system", SYSTEM_PROMPT)] + load_history(session_id) + [("user", message)]

def sse_gen(msgs, session_id, question):
    """流式生成 + 结束后把完整问答落库。"""
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
    msgs = build_msgs(sid, req.message)
    if req.stream:
        return StreamingResponse(
            sse_gen(msgs, sid, req.message),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    reply = get_llm().invoke(msgs).content
    save_pair(sid, req.message, reply)
    return ok({"reply": reply, "session_id": sid})


# ---- W17-D3 SSE 实验端点（验收后可删）----
@router.get("/stream_demo")
def stream_demo():
    def gen():
        for ch in "液压支架选型需考虑煤层厚度、倾角、瓦斯等级。":
            yield f"data: {ch}\n\n"
            time.sleep(0.05)
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
