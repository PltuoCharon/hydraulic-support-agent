# W35-D6 计算记录查询与追溯查看契约

## 1. 范围

W35-D4 已建立 calculation_records 写入闭环。

W35-D6 增加只读查询：

计算成功
→ calculation record
→ 最近记录列表
→ 单条记录详情
→ 输入 / 输出 / Formula ID / provenance 查看

D6 不新增数据库表，不修改 calculation_records schema。

D6 不实现：
- 修改或删除历史记录
- 恢复历史参数到当前表单
- rerun / replay
- 自动重新计算
- CAD / FEA

查看历史记录不等于重新执行历史计算。

## 2. D4 provenance 前置补强

example：
- context_source_type = NULL
- context_confirmed = NULL
- context_snapshot = NULL

直接 user_input：
- context_source_type = user_input
- context_confirmed = NULL
- context_snapshot = NULL

example 和直接输入不得保存伪造的上游 provenance。

selected_support / calculated_requirement：
- 必须 confirmed=true
- 必须有 target.resistance_kn
- 输入与 reference 一致时保留 provenance
- p_kn 被修改时降级为 user_input
- 降级后保留 snapshot，并写 actual_input_override

## 3. Service 查询契约

新增只读函数：

list_calculation_records(calc_type="column_design", limit=20)

get_calculation_record(record_id)

当前只开放 calc_type=column_design。

limit：
- 默认 20
- 最小 1
- 最大 100

排序固定为：

created_at DESC, id DESC

所有 SQL 请求参数使用绑定参数，不拼接用户输入 SQL。

列表只返回摘要：
- id
- record_version
- calc_type
- run_mode
- formula_ids
- context_source_type
- context_confirmed
- created_at

单条详情返回：
- id
- record_version
- calc_type
- run_mode
- formula_ids
- inputs_snapshot
- outputs_snapshot
- context_source_type
- context_confirmed
- context_snapshot
- created_at

## 4. JSON 完整性

读取时严格解析：

formula_ids: list
inputs_snapshot: dict
outputs_snapshot: dict
context_snapshot: dict | NULL

非法 JSON、顶层类型错误或非预期 NULL：
必须显式抛出 CalculationRecordDataError。

禁止：
解析失败 → {}
解析失败 → []
解析失败 → NULL

不得静默伪造历史记录。

context_source_type 保留数据库原值。

不得重新解释 selected_support / calculated_requirement / user_input / example。

## 5. API

新增：

GET /api/calc/records
GET /api/calc/records/{record_id}

列表成功：

{"code":0,"data":[]}

详情不存在：

{"code":1,"msg":"calculation record not found"}

created_at 在 API 层输出 ISO 8601 字符串。

## 6. 只读边界

D6 查询接口只执行 SELECT。

查询接口本身不得产生任何 calculation_records 写操作。

既有 POST /column-design 成功后继续按 D4 写入记录。

## 7. 前端边界

增加：

最近计算记录
→ 点击记录
→ 查看详情

暂不增加：
- 再次计算
- 恢复参数
- 修改记录
- 删除记录
