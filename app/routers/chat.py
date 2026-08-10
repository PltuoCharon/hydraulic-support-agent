"""对话接口。W17-D4：stream=true 时 SSE 打字机流式返回；否则一次性返回。"""
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.core.response import ok
from app.services.llm import chat, get_llm

router = APIRouter()

SYSTEM_PROMPT = """你是"液压支架智能选型助手"，服务于煤矿综采工作面设备选型。
规则：
1. 只回答液压支架选型、综采地质条件分析相关问题，其他话题礼貌拒绝；
2. 涉及具体型号推荐时，说明本回答仅基于通用知识，精确推荐请使用 /api/match 匹配接口；
3. 回答简洁专业，不超过 300 字。"""

class ChatReq(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None   # D5 启用
    stream: bool = False            # D4：true 走 SSE 流式

def sse_gen(msgs):
    """把 LLM 的流式 chunk 包装成 SSE 格式：data: ...\n\n，结尾 [DONE]。"""
    try:
        for chunk in get_llm().stream(msgs):
            if chunk.content:
                yield f"data: {chunk.content}\n\n"
    except Exception as e:
        # LLM 挂了也给前端一个可识别的结尾，不裸 500
        yield f"data: [ERROR] {type(e).__name__}\n\n"
    finally:
        yield "data: [DONE]\n\n"

@router.post("/")
def chat_endpoint(req: ChatReq):
    if req.stream:
        msgs = [("system", SYSTEM_PROMPT), ("human", req.message)]
        return StreamingResponse(
            sse_gen(msgs),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    reply = chat(req.message, system=SYSTEM_PROMPT)
    return ok({"reply": reply, "session_id": req.session_id})


# ---- W17-D3 SSE 实验端点（验收后可删）----
@router.get("/stream_demo")
def stream_demo():
    def gen():
        for ch in "液压支架选型需考虑煤层厚度、倾角、瓦斯等级。":
            yield f"data: {ch}\n\n"
            time.sleep(0.05)
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
