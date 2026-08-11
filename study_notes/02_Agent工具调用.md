# 02 Agent 与工具调用（Function Calling）

## 概念
Agent = LLM + 工具集 + 循环执行器。模型每轮决定"直接回答"或"调用工具"，
工具结果回喂后继续推理，直到给出最终答案或达到迭代上限。

## 本项目用法（W18）
- 四个 `@tool` 封装的工具（`app/agent/tools.py`）：
  - `query_database`：白名单表查询（mining_areas/support_models/working_conditions），
    参数化 SQL，禁止 LLM 生成原生 SQL（注入防线）；
  - `run_matching`：CBR 匹配引擎，入参范围校验 (0.5, 25)；
  - `recalc_params`：部件修改重算（缸径 320→360，Support 类公式）；
  - `search_knowledge`：规范知识库检索，结果带 source/loc 溯源；
- 组装：`create_tool_calling_agent` + `AgentExecutor`
  （return_intermediate_steps=True 把工具链透传给前端 tools 字段）；
- SYSTEM 铁律四条：一切数字来自工具 / 工具没有就说"暂无此项" /
  引用注明来源 / 只答选型。

## 踩坑
1. **Agent 会自主组合工具**：问"缸径320改360差多少"，它连调两次
   recalc_params 求差——能力超出预期，也说明提示词无需写死流程；
2. **max_iterations 必须设**：防止工具结果不满足时死循环烧钱，本项目定 6；
3. **工具的 docstring 就是给模型看的"使用说明书"**：写清"什么时候调用、
   参数含义、返回什么"，调用准确率明显提高；
4. **测试绝不打真实 LLM**：patch `app.routers.chat.ask`（换心后改为
   patch get_llm/_chat 统一入口），用 FakeLLM 按 prompt 内容分支返回。
