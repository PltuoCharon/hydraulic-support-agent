# W35-D4 计算记录契约

## 目标

W35-D4 只建立“立柱缸径设计”的最小可追溯计算记录闭环。
不扩展 CAD、仿真、案例库写入，也不修改纯计算公式。

## 分层

- app/services/calc/column.py：保持纯计算，不写数据库。
- API / record service：成功计算后保存记录。
- 失败请求不得写入正式成功记录。
- calculation_records 与 working_conditions 案例库严格分离。

## calculation_records

第一版采用单表 + TEXT JSON 快照，避免提前拆成多表。

字段：

- id：INT AUTO_INCREMENT 主键。
- record_version：记录契约版本，当前为 1。
- calc_type：当前固定 column_design。
- run_mode：engineering 或 example。
- formula_ids：JSON 数组文本。
- inputs_snapshot：请求输入 JSON 文本。
- outputs_snapshot：成功结果 JSON 文本。
- context_source_type：selected_support / calculated_requirement / user_input / NULL。
- context_confirmed：1 / 0 / NULL。
- context_snapshot：设计上下文 JSON 文本，可为 NULL。
- created_at：TIMESTAMP DEFAULT CURRENT_TIMESTAMP。

JSON 文本统一由 Python json.dumps(..., ensure_ascii=False, sort_keys=True) 生成。
未知值保持 null，不补 verified，不构造不存在的来源。

## 公式记录规则

column_design 成功记录：

- F-COL-001：总是记录。
- F-COL-002：总是记录。
- F-COL-003：仅当 p_set_kn 不为 null 时记录。

标准缸径向上圆整属于当前 column.py 的算法步骤；
在没有独立 Formula ID 前，不伪造新的 formula_id。

## 上下文规则

### selected_support

来自 D3 推荐支架传递。
必须保存 support_model、resistance_kn、source_text、data_status、confirmed。
若作为正式工程上下文使用，confirmed 必须为 true。

### calculated_requirement

为后续 D2→D3 接入预留。
不得在当前未实现的前端路径中伪造该来源。

### user_input

直接进入立柱设计、无 transfer context 时使用。
此时 context_confirmed 为 NULL。

### example

“填入计算示例”是 run_mode=example，不是新的 provenance source。
示例值不得伪装成数据库参数或厂家参数。

## 参数来源边界

D4 不解决 eta 的物理定义，不把 eta 与 Ks 等同。
n、p_mpa、eta、p_set_kn 不从推荐支架自动推断。
如果用户修改了从推荐支架带入的 p_kn，记录不得继续声称该 p_kn 来自原推荐值；
实现时必须把该输入视为 user_input，或明确保存实际输入与上游参考值的差异。

## API 返回

成功计算保持现有计算结果字段，并新增 record_id。
record_id 只代表“该次成功计算已持久化”，不代表制造级设计认证。

## 非目标

W35-D4 不做：

- CAD / FEA / 数字孪生任务记录；
- working_conditions 自动新增案例；
- evidence_sources / parameter_evidence 外键；
- 用户权限与审计账号；
- eta / 材料 / 阀泵物理口径重新核定。
