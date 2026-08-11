"""LLM 服务: ChatOpenAI 单例 + 带重试兜底的 chat()。

W20-D3: chat() 失败重试1次, 仍失败返回友好提示而不抛异常——
状态机各节点拿到提示文本照常往下走, checkpointer 状态不丢。
"""
import time

from langchain_openai import ChatOpenAI

from app.config import settings

_LLM = None


def get_llm() -> ChatOpenAI:
    """ChatOpenAI 单例: temperature=0 防幻觉。"""
    global _LLM
    if _LLM is None:
        _LLM = ChatOpenAI(
            model="glm-4-flash",
            temperature=0,
            api_key=settings.ZHIPUAI_API_KEY,
            base_url=settings.ZHIPUAI_BASE_URL,
        )
    return _LLM


def _chat_once(prompt: str, system: str | None = None) -> str:
    """单次调用(原 chat 逻辑)。"""
    msgs = []
    if system:
        msgs.append(("system", system))
    msgs.append(("human", prompt))
    resp = get_llm().invoke(msgs)
    return resp.content if hasattr(resp, "content") else str(resp)


def chat(prompt: str, system: str | None = None, retries: int = 1) -> str:
    """LLM 调用: 失败重试 retries 次, 仍失败返回友好提示(不抛异常)。"""
    for attempt in range(retries + 1):
        try:
            return _chat_once(prompt, system)
        except Exception as e:
            print(f"[llm] 第{attempt+1}次调用失败: {e}")
            if attempt < retries:
                time.sleep(2)
    return "模型服务暂时不可用，请稍后重试。（本次对话状态已保留，可直接重发消息）"
