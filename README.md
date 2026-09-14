# hydraulic-support-agent
## 架构（W28 services 层重构后）
用户 → 前端(Vue)
↓ HTTP
FastAPI routers（薄壳：参数校验/异常映射，无 SQL）   Agent tools（白名单+格式化，无 SQL）
↓ 委托                                        ↓ 委托
└───────────────→  app/services  ←────────────┘
┌──────────────────────────────────────────────────────────┐
│ matching.py   匹配核心：load_area/load_cases(数据层,SQL唯一 │ 纯函数match_supports(不碰DB,可REPL直接调用)
│ queries.py    查询服务：list/get/search_rows(白名单)        │
│ filter.py     硬约束筛选(纯函数)  support_calc.py 参数重算  │
│ knowledge.py  规范检索  normalize/entropy_weight/ahp 评分件 │
└──────────────────────────────────────────────────────────┘
↓
app/db.py → MySQL hydraulic_support

**铁律**（W28-D7 冻结的接口契约）：
1. SQL 只允许出现在 services 层；router/agent 出现 SQL 即视为退化
2. 同一逻辑全系统只许一份实现（两路径一致性由 tests/test_consistency.py 守门，10/10 才绿）
3. 盲测矿区（is_test=1）永不在前端列表可见、永不入匹配候选池
4. suspect 型号默认退出一切候选池（queries 用 verified 白名单，matching 用 suspect 黑名单，两口径在当前数据下等价——2026-09-14 核实 verified=157/suspect=2）
5. 估算参数来源标注三处一致：DB source 字段、前端徽标、论文表述
