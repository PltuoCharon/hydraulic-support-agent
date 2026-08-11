# 01 LangChain 基础

## 概念
LangChain 是大语言模型应用框架，核心抽象：
- **ChatModel**：对话模型封装（本项目用 ChatOpenAI 兼容接口接智谱 GLM）；
- **PromptTemplate**：把变量注入提示词模板；
- **消息结构**：("system"/"human"/"ai", content) 元组列表。

## 本项目用法
- 单例模式：`app/services/llm.py` 的 `get_llm()` 全局只建一次 ChatOpenAI，
  避免每次请求重建连接；
- 参数定稿：model=glm-4-flash、temperature=0，集中在 config（W20-D4）；
- 兼容技巧：智谱提供 OpenAI 兼容端点，
  `ChatOpenAI(base_url="https://open.bigmodel.cn/api/paas/v4/", api_key=...)` 直连。

## 踩坑
1. **LangChain 1.0 破坏性变更**：`AgentExecutor`/`create_tool_calling_agent`
   从 `langchain.agents` 移除，需安装 `langchain-classic` 并
   `from langchain_classic.agents import ...`；
2. **str.format 与 JSON 花括号冲突**：提示词里若有 JSON 示例（`{"key": ...}`），
   format 会把花括号当占位符报 KeyError → 改用 `.replace("{var}", val)`；
3. **GLM 输出爱包 ```json 围栏**：解析前先正则提取首个 `{...}` 块
   （`_parse_json`），不能直接 `json.loads`；
4. **temperature=0 不是万能**：结构化抽取稳定了，但话术会变得模板化，
   追问话术多样性需要靠 prompt 约束而非温度。
