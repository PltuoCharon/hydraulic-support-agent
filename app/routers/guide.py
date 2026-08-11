"""引导式选型对话接口: LangGraph 状态机, thread_id=session_id。"""
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from app.guide.graph import build_graph, chat_once

router = APIRouter()

_GRAPH = None


def _graph():
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = build_graph()
    return _GRAPH


class GuideReq(BaseModel):
    message: str
    session_id: str | None = None


@router.post("")
def guide_endpoint(req: GuideReq):
    sid = req.session_id or uuid.uuid4().hex[:12]
    state = chat_once(_graph(), sid, req.message)
    last = state["messages"][-1]
    reply = last.content if hasattr(last, "content") else str(last[1])
    return {"ok": True, "data": {
        "reply": reply,
        "session_id": sid,
        "stage": state.get("stage"),
        "params": state.get("params", {}),
        "missing": state.get("missing", []),
    }}
