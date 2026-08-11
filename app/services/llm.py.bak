"""LLM 客户端：LangChain ChatOpenAI 单例，接智谱 GLM（OpenAI 兼容端点）。
W17-D1。Key 从 .env 读取（经 app.config.settings），temperature=0 保证选型解释稳定可复现。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from langchain_openai import ChatOpenAI
from app.config import settings

_llm = None

def get_llm() -> ChatOpenAI:
    """ChatOpenAI 单例。模型 glm-4-flash（免费档，响应快，演示够用）。"""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="glm-4-flash",
            temperature=0,
            api_key=settings.ZHIPUAI_API_KEY,
            base_url=settings.ZHIPUAI_BASE_URL,
        )
    return _llm

def chat(prompt: str, system: str = "") -> str:
    """一次性对话（D2 接口用）。"""
    msgs = []
    if system:
        msgs.append(("system", system))
    msgs.append(("human", prompt))
    return get_llm().invoke(msgs).content

if __name__ == "__main__":
    out = chat("用一句话说明液压支架的工作阻力是什么意思",
               system="你是煤矿综采设备专家，回答简洁专业")
    print(out)
