# W36.5-D4 系统最终收口

## 1. 收口基线

W36 产品冻结提交：

af1bf0c7e1f2308b09e11cd0008ae85fdf88342a

W36.5 系统审计与治理提交：

- 62f8f82：W36.5-D2 系统副线差距矩阵
- 32d3aa6：W36.5-D3 E2E 与 artifacts 治理契约
- eef47a6：W36.5-D3 真实浏览器 E2E 与工作产物治理

W36.5 的目的不是扩展新模块，而是确认：

- 哪些能力已经完成；
- 哪些能力明确延期；
- 哪些属于 evidence gap；
- 哪些属于 technical debt；
- 下一阶段从哪里继续。

## 2. W36.5 最终状态

### 2.1 W36 推移千斤顶主链

状态：

COMPLETE

已完成：

HydraulicCylinder
→ push_jack_design
→ FastAPI
→ JackView
→ 输入失效保护
→ stale result 防回填
→ 真实浏览器 E2E。

真实浏览器已经验证：

300 kN + 31.5 MPa
→ 候选缸径 125 mm
→ 推力校核“满足”
→ 修改输入后旧结果立即失效。

31.5 MPa 仅为测试输入，不是产品默认压力。

MT/T94 完整缸径/杆径系列核验仍不属于 W36 已完成内容。


### 2.2 Formula Registry

状态：

PARTIAL

当前共 24 条：

- active：16
- legacy_review：8

W36.5 不强制把 legacy_review 升级为 active。

推移千斤顶当前没有正式 F-JACK Formula ID。

原因不是遗漏，而是：

INTENTIONALLY_DEFERRED

在独立标准核验完成前不得伪造 Jack Formula ID。

### 2.3 Calculation Records

立柱：

COMPLETE

当前正式 calc_type：

column_design

推移千斤顶：

INTENTIONALLY_DEFERRED

在正式扩展以下内容前，不写入 push_jack calculation record：

- ALLOWED_CALC_TYPES
- record query contract
- API
- tests
- Formula Registry traceability

### 2.4 Parameter-level Provenance

设计与迁移策略：

COMPLETE

生产实现：

NOT_IMPLEMENTED

当前尚无正式：

- production parameter_evidence migration
- parameter evidence service
- parameter evidence API
- parameter evidence UI
- 批量 field-level backfill

首轮正式 parameter-level evidence backfill 保留到 W38。


## 3. Evidence Gap 与 Technical Debt

### 3.1 eta

状态：

EVIDENCE_GAP

当前口径：

历史立柱修正系数 η（物理口径待核）。

约束：

- 必须显式输入；
- 不设默认值；
- η 不等同于 Ks；
- 不宣称为机械效率；
- 不宣称为液压效率。

### 3.2 canopy_len

状态：

TECH_DEBT

当前正式 UI 语义：

支护长度参数

不得自动解释为：

- 控顶距
- 顶梁长度
- 控顶宽度 Bc
- 梁端距

历史脚本、legacy API 与数据库注释中的旧术语继续作为兼容债务保留。

新主链不得静默把 canopy_len 映射为 Bc。

### 3.3 legacy_review formulas

状态：

TECH_DEBT / INTENTIONALLY_DEFERRED

当前 8 条 legacy_review 继续可见。

W36.5 不删除、不隐藏、不强制升级。

升级必须依赖独立来源审计和工程语义核验。

### 3.4 Python TestClient warning

状态：

TECH_DEBT

当前存在 Starlette TestClient / httpx deprecation warning。

该 warning 不影响当前 358 条测试通过结果，
但后续依赖升级时需要处理。

### 3.5 Vite chunk warning

状态：

TECH_DEBT

当前 production build 通过。

仍存在部分 bundle > 500 kB warning。

该问题属于前端性能优化，不阻塞 W36.5 收口。


## 4. W36.5 新增的系统能力

### 4.1 Real Browser E2E

状态：

COMPLETE

技术栈：

@playwright/test + Chromium

真实链路：

Chromium
→ Vue Hash Router
→ /#/calc?m=jack
→ Vite :5173
→ /api proxy
→ FastAPI :8000
→ push_jack_design
→ Vue rendering

测试不 mock push-jack API 或计算服务。

E2E 已实际发现并修复：

JackView 中 success / danger / 满足 / 不满足
被错误解释为 Vue 运行时变量的问题。

E2E 通过证明系统交互链可运行，
不等同于证明工程公式或物理语义绝对正确。

### 4.2 artifacts 治理

状态：

COMPLETE

/artifacts/ 已作为本地工作目录加入 .gitignore。

本地 artifacts 未被删除。

data_recovery/w34d6 的 5 个关键恢复文件继续本地保留。

Git 中保存：

W36_5D3_data_recovery_sha256.md

用于记录其 SHA256 完整性。

Playwright test-results / report / blob-report 同样不进入 Git。


## 5. W36.5 最终验收基线

截至 D4 收口前：

- Python：358 passed，1 warning
- Real Browser E2E：1 passed
- Vite production build：PASS
- git diff --check：PASS
- data recovery SHA256：5 files verified
- 工作区：clean

这些结果证明当前软件实现和交互链通过既定验收。

它们不应被描述为：

- 制造级设计认证；
- 标准符合性认证；
- MT/T94 合规认证；
- 工程公式物理有效性的独立证明。

## 6. 后续路线冻结

下一阶段：

W37：
阀与阀组设计，
同时继续改善设计中心与公式追溯。

W38：
管路 / 胶管 / 泵站，
并执行第一轮正式 parameter-level evidence backfill。

W39：
二维参数化图纸，
引入 A/B/C 数据等级与 benchmark geometry。

W40：
三维骨架 / Model Center / structure provenance。

W41：
四连杆运动学与共享 geometry。

W42：
一维液压动态与参数证据。

W43：
单组件结构 / FEA prototype 与材料证据。

W44：
Agent toolization，
所有工程回答尽量携带 formula / source / time / data status。

## 7. W36.5 关闭条件

W36.5 关闭后：

- 不回补未经核验的参数证据；
- 不制造 F-JACK Formula ID；
- 不提前创建 push_jack calculation record；
- 不修改历史数据库字段语义；
- 不把测试通过描述为工程认证；
- 不在 W36.5 中开始 W37 功能开发。

W36.5-D4 完成后，
下一开发阶段正式进入 W37。
