"""对话接口。W17-D2：一次性返回；D4 改流式；D5 加会话历史。"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.response import ok
from app.services.llm import chat

router = APIRouter()

SYSTEM_PROMPT = """你是"液压支架智能选型助手"，服务于煤矿综采工作面设备选型。
规则：
1. 只回答液压支架选型、综采地质条件分析相关问题，其他话题礼貌拒绝；
2. 涉及具体型号推荐时，说明本回答仅基于通用知识，精确推荐请使用 /api/match 匹配接口；
3. 回答简洁专业，不超过 300 字。"""

class ChatReq(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None   # D5 启用

@router.post("/")
def chat_once(req: ChatReq):
    reply = chat(req.message, system=SYSTEM_PROMPT)
    return ok({"reply": reply, "session_id": req.session_id})


# ---- W17-D3 SSE 实验端点（D4 后删除）----
from fastapi.responses import StreamingResponse
import time

@router.get("/stream_demo")
def stream_demo():
    """假流式：逐字推送固定文本，体验 SSE 格式。"""
    def gen():
        for ch in "液压支架选型需考虑煤层厚度、倾角、瓦斯等级。":
            yield f"data: {ch}\n\n"
            time.sleep(0.05)
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
