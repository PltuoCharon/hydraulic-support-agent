"""对话接口。W18-D7：接入四工具Agent（自主工具决策），替换W17固定if-else流程。
说明：Agent 工具调用为同步阻塞，流式模式采用"完成后分片推送"（真·token级流式
需 LangGraph，列为后续改进）。"""
import time, uuid
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.core.response import ok
from app.db import get_conn
from app.agent.agent import ask

router = APIRouter()
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

def sse_answer(answer: str, session_id: str, question: str):
    """Agent 回答分片推送 + 落库 + [DONE]。"""
    try:
        for i in range(0, len(answer), 4):
            yield f"data: {answer[i:i+4]}\n\n"
            time.sleep(0.02)
    except Exception as e:
        yield f"data: [ERROR] {type(e).__name__}\n\n"
    finally:
        if answer:
            save_pair(session_id, question, answer)
        yield "data: [DONE]\n\n"

@router.post("/")
def chat_endpoint(req: ChatReq):
    sid = req.session_id or uuid.uuid4().hex[:16]
    history = load_history(sid)
    result = ask(req.message, history)
    answer = result["answer"]
    tools = [t for t, _ in result["steps"]]
    if req.stream:
        return StreamingResponse(
            sse_answer(answer, sid, req.message),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
    save_pair(sid, req.message, answer)
    return ok({"reply": answer, "session_id": sid, "tools": tools})


# ---- W17-D3 SSE 实验端点（保留备用）----
@router.get("/stream_demo")
def stream_demo():
    def gen():
        for ch in "液压支架选型需考虑煤层厚度、倾角、瓦斯等级。":
            yield f"data: {ch}\n\n"
            time.sleep(0.05)
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
