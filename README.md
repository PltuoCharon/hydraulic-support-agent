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


---

## 数据冻结声明（W31-D2，2026-09-15）

按 W31–W46 计划"限期冻结"原则，自本声明起数据口径冻结如下：

1. **支护强度覆盖率 95.6%**（159 架型中 152 条非空），达到并超过 ≥60% 的冻结阈值，冻结于此值，不再回源补录。
2. **重量覆盖率 8.2%**，覆盖率偏低如实注明：本系统与论文**不做重量相关结论**，重量字段仅作展示。
3. **案例数 41 条**为暂值：W31-D3 扩充至 ≥50 后，随 `git tag data-v4` 一并冻结并更新 manifest。
4. 冻结后数据**只允许新增、不允许回头返工**；任何新增数据沿用既有来源标注纪律（查不到标"未查到公开参数"，估算值三处同标）。
5. 论文一律使用冻结口径数字；会进论文的数字归档 `docs/thesis_data/` 并记入 `FREEZE_manifest.txt`。
