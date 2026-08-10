"""四工具 Agent 组装：GLM-4 function calling + create_tool_calling_agent。W18-D5。
Agent 自主决定调不调工具、调哪个。铁律写进 system prompt：
一切数字必须来自工具返回，禁止凭记忆报参数。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.config import settings
from app.agent.tools import TOOLS

SYSTEM = """你是"液压支架智能选型Agent"，服务煤矿综采工作面设备选型。

【可用工具】
1. query_database —— 查矿区地质/支架型号/工况案例的事实数据
2. run_matching —— CBR案例匹配：给工况参数，返回相似案例实际用架
3. recalc_params —— 部件修改重算：缸径/泵站压力变化后的阻力与支护强度
4. search_knowledge —— 检索 MT/T 556 设计规范等手册知识

【决策原则】
- 推荐支架型号 → 必须调 run_matching，以返回的 Top-1 为首选
- 问具体矿区/型号参数 → 调 query_database
- 问"缸径/压力改了会怎样" → 调 recalc_params
- 问设计规则/规范依据 → 调 search_knowledge，回答注明来源页码
- 一般概念问答（支护强度是什么） → 可直接回答，不用工具

【铁律】
1. 一切数字（阻力、强度、采高、重量等）必须来自工具返回，禁止凭记忆报参数；
2. 工具没给的数据，明确说"数据库中暂无此项"，不得编造；
3. 引用规范内容必须注明来源；
4. 只答液压支架选型相关问题，其他话题礼貌拒绝；
5. 回答简洁专业，不超过300字。"""

_executor = None

def get_agent() -> AgentExecutor:
    """AgentExecutor 单例。return_intermediate_steps=True 供 D6 打印工具调用链。"""
    global _executor
    if _executor is None:
        llm = ChatOpenAI(model="glm-4-flash", temperature=0,
                         api_key=settings.ZHIPUAI_API_KEY,
                         base_url=settings.ZHIPUAI_BASE_URL)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        agent = create_tool_calling_agent(llm, TOOLS, prompt)
        _executor = AgentExecutor(agent=agent, tools=TOOOLS if False else TOOLS,
                                  verbose=False, return_intermediate_steps=True,
                                  max_iterations=6, handle_parsing_errors=True)
    return _executor

def ask(question: str, history: list | None = None) -> dict:
    """问 Agent 一个问题。返回 {answer, steps: [(tool, input), ...]}"""
    out = get_agent().invoke({"input": question, "chat_history": history or []})
    steps = [(s[0].tool, s[0].tool_input) for s in out.get("intermediate_steps", [])]
    return {"answer": out["output"], "steps": steps}

if __name__ == "__main__":
    r = ask("煤层厚度8.8米、倾角2度的综放工作面，推荐什么支架？")
    print("工具调用链:", r["steps"])
    print("回答:", r["answer"])
