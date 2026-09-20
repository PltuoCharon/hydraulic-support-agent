# W35-D7-B Formula Registry 只读查询契约

## 1. 目标

为 Formula Registry 提供稳定的只读查询接口，
使计算记录中的 formula_id 可以追溯到当前项目登记的公式语义、来源和验证说明。

D7-B 不创建第二份 Formula Registry，
不把 Registry 搬入数据库。

唯一数据源保持：

docs/evidence/formulas/W34D2_Formula_Registry.csv

## 2. API

提供：

GET /api/formulas

GET /api/formulas/{formula_id}

不得提供：

POST /api/formulas
PUT /api/formulas
PATCH /api/formulas
DELETE /api/formulas

D7-B 查询接口只读。

## 3. Registry 字段

Registry 当前字段保持原样：

- formula_id
- module
- name
- status
- formula
- input_vars
- output
- unit
- source
- verification
- current_callers
- notes

查询层不得重新命名这些字段，
不得从 Markdown 或其他文件重新拼装公式记录。


## 4. List 语义

GET /api/formulas

返回 Registry 中全部登记记录。

不得默认隐藏 legacy_review。

List 返回每条记录的摘要字段：

- formula_id
- module
- name
- status
- formula
- unit

记录顺序保持 Registry 文件顺序。

D7-B 暂不加入分页、排序、状态筛选和模块筛选，
避免在当前仅 24 条记录的 Registry 上提前增加查询语义。

## 5. Detail 语义

GET /api/formulas/{formula_id}

返回该 Formula Registry 行的全部原始字段：

- formula_id
- module
- name
- status
- formula
- input_vars
- output
- unit
- source
- verification
- current_callers
- notes

input_vars 保持 Registry 中现有字符串表示，
D7-B 不自行转换为参数对象或重新解释参数语义。

未知 formula_id：

返回明确业务错误：

formula not found


## 6. 数据完整性

读取 Registry 时必须至少验证：

- CSV 表头包含契约要求的全部字段
- formula_id 非空
- formula_id 唯一

若 Registry 结构损坏，
必须显式失败，
不得伪造空记录、默认公式或静默跳过冲突记录。

普通字段允许保持 Registry 当前原值，
包括空字符串。

## 7. 证据边界

source、verification、notes 仅代表 Formula Registry 当前登记内容。

D7-B 不把这些字段升级解释为：

- 参数级 provenance
- 完整标准原文
- 制造依据
- parameter_evidence 数据
- evidence_sources 数据

W35-D1 中的 evidence_sources / parameter_evidence
仍属于规划结构，
D7-B 不创建对应数据库表。

## 8. 状态边界

active 按 Registry 原状态返回。

legacy_review 也按 Registry 原状态返回。

查询层不得：

- 把 legacy_review 自动改为 active
- 隐藏 legacy_review
- 根据 current_callers 推断验证状态
- 根据 source 文本重新判断工程可信度

## 9. D7-B 范围

D7-B 只实现 Formula Registry 的只读 Service/API。

本阶段不：

- 修改公式计算实现
- 修改 Formula Registry 工程语义
- 修改 calculation_records
- 实现参数级证据数据库
- 实现 Formula Registry 编辑能力
- 实现前端 Formula ID 点击追溯

前端追溯属于后续 D7-C。
