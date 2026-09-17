# W35D1 参数级 Provenance Schema

## 总体关系

evidence_sources
    1
    |
    N
parameter_evidence
    N
    |
    1
support_models

support_models 保存当前业务规范值。

parameter_evidence 保存某型号某字段的证据断言。

## evidence_sources

建议字段：

- id
- source_type
- title
- authors
- publication_year
- publisher
- url
- note
- created_at

source_type 初步允许：

- manufacturer
- standard
- paper
- thesis
- patent
- government
- handbook
- product_page
- web
- other

页码、章节、表号不放 evidence_sources，
而放 parameter_evidence.source_locator。

因为同一文献支持不同字段时，
引用位置可能不同。

## parameter_evidence

建议字段：

- id
- support_id
- field_name
- value_text
- value_num
- value_min
- value_max
- unit
- value_origin
- verification_status
- source_id
- source_locator
- formula_id
- is_derived
- is_selected
- note
- created_at
- updated_at

## 范围值

单值：

value_num = 1.46

范围：

value_min = 0.48
value_max = 0.54

原始范围不得静默取中值。

## value_origin

冻结五类：

- original
- supplemented
- calculated
- estimated
- missing

original：
来源直接给出。

supplemented：
后期可靠来源回溯补录。

calculated：
已知输入 + 已登记公式的确定性计算。

estimated：
包含经验参数、近似参数、类比或非唯一工程假设。

missing：
当前无可靠值。

## verification_status

冻结四类：

- verified
- provisional
- conflicting
- unverified

value_origin 与 verification_status 是两个独立状态轴。

合法组合包括：

- original + verified
- original + conflicting
- supplemented + verified
- calculated + verified
- estimated + provisional
- missing + unverified

## is_derived

建议：

- original = 0
- supplemented = 0
- calculated = 1
- estimated = 1
- missing = 0

## is_selected

同一个：

support_id + field_name

允许存在多条来源断言。

is_selected 表示哪条断言对应当前 support_models 采用值。

冲突未解决时，
允许全部 is_selected = 0。

## formula_id

formula_id 保存 Formula Registry 字符串 ID。

W35D1 不建立 FK。

Formula Registry 当前仍以版本化 CSV 为权威来源。

## canopy_len

数据库字段名保持 canopy_len。

专业语义保持：

“支护长度参数”。

不得自动解释为顶梁长度、控顶宽度或梁端距。
