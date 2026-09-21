# W36.5-D2 系统状态与副线差距矩阵

## 1. 基线

W36 最终冻结提交：

af1bf0c7e1f2308b09e11cd0008ae85fdf88342a

当前设计计算主链已开放：

- 支护需求 q_need
- 立柱参数设计
- 立柱强度校核
- 推移千斤顶参数设计

当前仍未开放：

- 阀组设计
- 泵站匹配

## 2. 状态定义

本项目使用以下五种状态：

COMPLETE
已完成实现并通过当前验收。

PARTIAL
已有正式实现，但覆盖范围仍有限。

INTENTIONALLY_DEFERRED
已经明确决定延期，不属于缺陷。

EVIDENCE_GAP
功能或参数存在，但工程证据尚不足。

TECH_DEBT
历史兼容、命名、测试或工程治理债务。

NOT_IMPLEMENTED
仅有设计或规划，生产实现尚不存在。


## 3. 当前裁定

### 3.1 HydraulicCylinder / Push Jack

状态：

COMPLETE

W36 已完成：

HydraulicCylinder
→ push_jack_design
→ API
→ JackView
→ 输入失效保护
→ stale request 防回填
→ 工程边界显示。

MT/T94 完整尺寸系列核验不属于 W36 完成条件。

### 3.2 Formula Registry

状态：

PARTIAL

当前共 24 条：

- active: 16
- legacy_review: 8

8 条 legacy_review 必须继续保持可见。

不得为了提高“完成率”直接升级为 active。

Jack 当前没有正式 F-JACK Formula ID。

该状态属于 INTENTIONALLY_DEFERRED，
不是缺陷。

### 3.3 Calculation Records

Column：

COMPLETE

当前正式 calc_type：

column_design

Push Jack：

INTENTIONALLY_DEFERRED

不得在未扩展：

- ALLOWED_CALC_TYPES
- query contract
- API tests
- Formula Registry

之前直接写入 push_jack_design record。


### 3.4 Parameter-level Provenance

Schema / migration strategy：

COMPLETE

Production implementation：

NOT_IMPLEMENTED

当前只有：

- W35D1_provenance_schema.md
- W35D1_provenance_migration_draft.sql
- W35D1_迁移策略.md

当前没有：

- 正式 scripts/migrations provenance migration
- production parameter_evidence service
- parameter_evidence API
- parameter_evidence UI
- 正式字段级证据回填

该项保持为后续数据治理主线。

第一批正式 parameter evidence backfill
仍放在原定 W38 范围。

### 3.5 canopy_len

状态：

TECH_DEBT

正式裁定保持：

canopy_len = 支护长度参数

不得自动解释为：

- 控顶距
- 顶梁长度
- 控顶宽度
- 梁端距

新主链不得从 canopy_len 静默产生 Bc。

历史脚本、legacy API 和数据库 COMMENT
中的旧称谓暂作为兼容债务保留。

### 3.6 eta

状态：

EVIDENCE_GAP

当前正式称谓：

历史立柱修正系数 η（物理口径待核）

规则：

- 必须显式输入
- 不提供默认值
- 不等同于 Ks
- 不宣称为机械效率或液压效率


### 3.7 浏览器 E2E

状态：

NOT_IMPLEMENTED

当前 Python 单元、契约、API、源码守门测试较完整。

但尚未建立真实浏览器 E2E 测试。

W36.5-D3 增加最小 smoke：

/calc?m=jack
→ 填写参数
→ 执行计算
→ 验证候选缸径
→ 修改输入
→ 验证旧结果失效。

### 3.8 artifacts

状态：

TECH_DEBT

artifacts 当前保存：

- W34 审计输出
- W35 审计输出
- W34-D6 数据恢复文件

当前未加入 .gitignore。

W36.5-D3 必须先分类：

- 临时审计产物
- 恢复备份
- 应正式保存的证据

不得直接 rm -rf artifacts。

## 4. W36.5 不处理的范围

W36.5 不：

- 新增阀公式
- 新增泵站公式
- 开始 W37
- 强行升级 legacy_review
- 建立未经审核的 parameter evidence
- 给 Jack 伪造 Formula ID
- 给 Jack 直接开启 calculation record
- 修改历史数据库字段语义
- 删除 legacy API

## 5. 后续归属

W37：
阀与阀组。

W38：
管路、软管、泵站，
并开始第一批正式 parameter evidence 回填。

W36.5-D3：
真实浏览器 E2E smoke
与 artifacts 工作区治理。

W36.5-D4：
系统最终收口和后续路线冻结。
