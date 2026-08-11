# 03 LangGraph 对话状态机

## 概念
把对话建模为有向图：节点是处理函数（读状态→返回增量），边是转移规则，
状态是全局快照（TypedDict）。与 Agent 的区别：Agent 的流程由模型即兴决定，
状态机的流程由开发者显式编排——选型这类"流程固定、容错要求高"的场景
更适合后者。

## 本项目用法（W19）
- **State 定义**（`app/guide/state.py`）：messages（add_messages reducer 自动
  追加）、params、missing、stage、match_result、confirmed；
- **四节点**（`app/guide/graph.py`）：
  - collect：LLM 抽参数（EXTRACT_PROMPT 只许输出 JSON），缺参则追问；
  - confirm：**模板复述**而非 LLM 生成——确认数字与抽取结果一字不差；
  - recommend：调 run_match 真实引擎，结果存 match_result，不生成文字；
  - explain：LLM 仅复述结果 JSON，prompt 明令数字一字不差、括注来源；
- **条件边** route：缺参→END(等用户)；等确认+纯肯定词→recommend；
  其余（含改口）→confirm 重确认；
- **持久化**：`compile(checkpointer=MemorySaver())`，
  `config={"configurable": {"thread_id": session_id}}`——
  每轮只需传新增消息，历史自动续上；不同 thread_id 会话隔离。

## 踩坑
1. **肯定词判定要排除数字**：用户说"倾角改成10度"含肯定口吻却是改口，
   `_is_affirm` 规则：以肯定词开头 且 不含任何数字；
2. **checkpointer 保存全部 state 字段**（不只是 messages），params/stage
   跨轮自动恢复；
3. **图是进程内单例**：改了代码必须重启 uvicorn，否则验收跑的旧逻辑；
4. **mock 要按入口 patch**：节点统一走 `_chat(llm, prompt)` 后，
   patch `get_llm` 一处即可拦截所有 LLM 调用；
5. **与 /api/chat 共享图实例**：两个接口同一 MemorySaver，
   会话状态互通（W20-D1 换心的关键设计）。

## 踩坑
1. **肯定词判定要排除数字**：用户说"倾角改成10度"含肯定口吻却是改口，
   `_is_affirm` 规则：以肯定词开头 且 不含任何数字；
2. **checkpointer 保存全部 state 字段**（不只是 messages），params/stage
   跨轮自动恢复；
3. **图是进程内单例**：改了代码必须重启 uvicorn，否则验收跑的旧逻辑；
4. **mock 要按入口 patch**：节点统一走 `_chat(llm, prompt)` 后，
   patch `get_llm` 一处即可拦截所有 LLM 调用；
5. **与 /api/chat 共享图实例**：两个接口同一 MemorySaver，
   会话状态互通（W20-D1 换心的关键设计）。
