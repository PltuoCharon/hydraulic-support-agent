# W42-D2 优化实验合同 V1

项目：液压支架智能辅助设计系统 V3.0。
开发基线 HEAD：a0c8f33133638a6b2b2dd61f873b0dde00e32ab9。
范围：纯数据模型、输入校验及 W41 评价记录绑定，不是工程优化或搜索算法。

## 1. 设计目标及文件

新增 app/models/optimization_contract.py，提供 OptimizationProblem、
OptimizationCandidate、ConstraintViolation、OptimizationResult、OptimizationRun。
辅助模型为 VariableBounds、VariableValue、ObjectiveValue。
专项测试：tests/test_w42d2_optimization_contract.py。
实际命令、结果及退出码：docs/evidence/w42/W42D2_validation.log。

保留既有 optimization_objective.py 空占位，不覆盖其他未跟踪草案。
不修改 W39/W40/W41 求解器、D4 DesignEvaluationResult 或工程门禁。
没有 GA、PSO、专业软件、数据库持久化、运行服务或搜索入口。
本次用户授权仅落实实验合同；模型和测试通过不等于正式 G1 或工程批准。

## 2. 不可变及序列化合同

全部新模型 frozen=True、extra=forbid、strict=True、revalidate_instances=always。
集合存为 tuple；输入 list/JSON array 仅复制为 tuple，不修改调用者输入。
数值不进行字符串或布尔转换，浮点必须有限，来源文字不能空白，单位显式。
嵌套新模型同样冻结。model_copy(update=...) 仍是 Pydantic 绕过校验的底层
接口，但进入新的结果/运行模型时会重新验证，不能借此保存伪目标。
不把 model_construct 或任意 Python 内部篡改当作合法合同入口。

W41 的模型保持原可变合同。新模型以经过验证和规范序列化的 JSON 字符串
保存比较合同及 D5 记录；访问 comparison_contract/evaluation_record 属性时
返回重新验证的独立实例。修改返回实例或原始 W41 请求/记录，不改变已存
实验快照。JSON 字符串是完整结构化快照，不是只保存状态标签。
设计来源字段继续保留声明，不能把完整记录未经筛选地发布到公共日志。

## 3. 数据结构与字段

### OptimizationProblem

| 字段 | 类型 / 语义 |
| --- | --- |
| version | 固定整数 1，拒绝布尔冒充版本 |
| problem_id | 1–128 个字母/数字/点/下划线/连字符的非敏感标识 |
| case_id | 案例标识，保留 ER/SM 域重标防护 |
| domain、readiness | SYNTHETIC_MATH/READY 或 ENGINEERING_REFERENCE/NOT_SOLVER_READY |
| variable_names | 固定 AB/BC/CD 三名称顺序，不增加工程变量 |
| bounds | VariableBounds 元组：variable_name、lower、upper、unit=mm、source；正有限、lower<upper |
| objective_names、objective_units | 合成可执行问题固定一个 SAMPLED_C_X_RANGE 分量及 mm |
| constraints | 合成可执行问题固定 FULL_REGULAR_SAMPLES；不是工程约束集合 |
| evaluation_budget | 正整数，候选记录/校验尝试的上限，不是时间预算或 W39 内部调用次数 |
| comparison_contract_json | 合成问题必需的 W41 ComparisonContract 快照；案例/域和数值边界必须一致 |
| engineering_verified | 固定 literal false，拒绝 true 和数值 0 替代 |

三变量名称为 rear_link_length_mm、shield_beam_effective_length_mm、
front_link_length_mm。固定 A/D、参考角/分支、角列表/方向和容差包含在 W41
比较合同内，不成为新变量。bounds.source 是声明，不是工程来源认证。

工程问题仅描述资料缺口，comparison_contract_json 必须为 null，readiness
必须 NOT_SOLVER_READY。允许 bounds/objective_names/objective_units/constraints
为空元组，不为 ER-001 补造几何或边界。即使记录者提供显式描述边界，也不
开放工程运行。可执行合成问题必须有全部三边界、既有目标及约束。

### OptimizationCandidate

| 字段 | 类型 / 语义 |
| --- | --- |
| candidate_id | 必须与 W41 记录标识一致 |
| problem | 不可变实验问题快照 |
| design_vector | VariableValue 元组：variable_name、正有限 value、unit=mm、source；实际评价设计必须完全匹配 |
| evaluation_status | NOT_EVALUATED / EVALUATED / FAILED / NOT_SOLVER_READY |
| objective_values | ObjectiveValue 元组：objective_name、有限非负 value、unit=mm、direction=MINIMIZE |
| constraint_violations | ConstraintViolation 元组，与真实记录或显式越界量一致 |
| evaluation_record_json | 验证后的 D5 CandidateEvaluationRecord 快照；未评价时为 null |

OptimizationCandidate.from_w41(problem, record) 是纯数据映射工厂，不调用
求解器或执行算法。它重新验证 D5 记录并从其中提取已验证设计、目标和失败。
非法原始输入可能无法形成有效设计，design_vector 允许 null，不伪造请求。

EVALUATED 在本优化合同中严格表示已满足本问题比较条件且 D5 ranking_eligible
为 true；不是“函数曾返回”的同义词。FAILED 包括真实输入/数学/服务失败及
明确的边界校验失败。NOT_SOLVER_READY 保留未执行语义。
已评价候选必须绑定问题的比较合同；有效请求条件不一致不能进入该实验。
无目标、无比较合同或不兼容但数学可行的记录，保留在原 W41 层，本 V1 不把
它提升为实验的已评分候选。NOT_EVALUATED 候选只能有界内设计、无目标/失败
声明；不能进入 OptimizationResult 的已完成候选列表或成为最佳结果。

### ConstraintViolation

| 字段 | 类型 / 语义 |
| --- | --- |
| constraint_name | 实际 W41 约束/错误阶段，或越界的变量名称 |
| status | INVALID_INPUT、NO_SOLUTION、DEGENERATE、OUT_OF_RANGE；另保留 W41 的 FULL_MOTION_INFEASIBLE、BRANCH_UNRESOLVED、NUMERICAL_ERROR、SERVICE_ERROR |
| violation_value | 有明确公式时的有限量，否则 null；不能作为替代目标 |
| unit | 已定义越界量为 mm；未定义幅度时为 null |
| severity | V1 分类固定 ERROR，非数值罚值、权重或工程严重度核验 |
| source | W41_D5_RECORD 或 DECLARED_BOUNDS |

OUT_OF_RANGE 唯一定量公式：max(lower-value, value-upper, 0)，必须严格大于 0，
单位 mm，来源 DECLARED_BOUNDS，且候选验证器核对实际变量/边界和每个违反
量。此候选为 FAILED，不产生 objective_values，无需伪造 W41 求解结果。

其他失败类型缺少统一数值幅度定义，violation_value/unit 均必须为 null，
来源 W41_D5_RECORD；禁止填 0/1、任意大数或把失败写成优秀目标。
NOT_SOLVER_READY 不虚构违反事件。TIMEOUT 未实现，不新增可执行超时记录。
这不是已完成一般数值约束违反函数、加权聚合或连续工程约束评价。

### OptimizationResult

| 字段 | 类型 / 语义 |
| --- | --- |
| problem、candidates | 同一问题的已完成记录；标识唯一、没有 NOT_EVALUATED |
| best_candidate | 实际候选列表中的可比较已评价候选；无可用候选则 null |
| objective_vector | 与 best_candidate.objective_values 完全一致；无最佳时为空元组 |
| feasible | 当且仅当存在已评价、可比较的最佳候选为 true |
| total_candidates | 等于记录数量且不超过 problem.evaluation_budget |
| failed_candidates | 等于未具备排名资格的记录数量，包含 NOT_SOLVER_READY；不是异常次数或求解器调用数 |

最佳候选必须拥有实际 W41 快照，目标必须相等于其中的真实 metrics，并在
该结果所有可比较记录中取得最小目标值；等值时允许任选真实记录。
这只是已记录有限候选的一致性校验，不执行搜索，不证明全局最优。
失败、无目标、未评价候选不能成为最佳；合法已评价目标值 0 可以。
无可行候选时最佳为 null、向量为空、feasible=false，禁止任意罚分填空。

### OptimizationRun

| 字段 | 类型 / 语义 |
| --- | --- |
| run_id、problem | 运行标识和固定实验问题快照 |
| algorithm_name | MANUAL / GA / PSO / UNSPECIFIED；仅元数据，无算法执行 |
| random_seed | 非负严格整数或显式 null，拒绝布尔 |
| budget | 正整数且不超过问题预算，计量候选尝试，不计时间 |
| candidate_count | 非负整数，不能超过本次 budget |
| status | NOT_STARTED / RUNNING / COMPLETED / FAILED / CANCELLED / NOT_RUN |
| result | 可选 OptimizationResult；存在时问题、数量、预算必须一致 |

NOT_STARTED/NOT_RUN 不能声称已处理候选或已有结果；COMPLETED 必须有结果。
工程运行只能 NOT_RUN、count=0、result=null。RUNNING/FAILED/CANCELLED 可保存
已验证记录快照，但状态枚举本身不提供执行、取消、中止、恢复或清理机制。
算法名字不证明 GA/PSO 曾运行，也不能将 MANUAL 记录当作算法效果证据。

## 4. 与 W41 的关系

W41 D3 的变量、单位和域门禁不变；D4 仍是原 evaluate_design()，目标只为
完整规则离散运动的 C 铰点 X 范围，不是 T 位移；D5 仍负责异常分类和比较
资格；D6 Oracle 仍给出有限合成输入上的独立数值证据。

新模型要求来源 W41 的评分符合 FEASIBLE、COMPUTED、有限值和同一比较合同。
记录中的设计变量、案例、单位、比较条件、状态、目标、失败必须与快照一致。
数字正确/结构一致不构成记录来源真实性的外部认证；调用方应使用真实 D5
入口并通过 from_w41() 保存记录，而不是手工伪造一致 JSON。没有认证签名、
工程来源验证或数据库审计系统。

模型保存和验证数据，不执行新的数学求解、优化迭代或最优搜索。
没有更改 DesignEvaluationResult，没有赋予 W41 未定义违反量新的罚分意义。

## 5. 当前限制

- 目标向量 V1 只有已存在的一个分量；不支持额外目标、Pareto 排序、权重或
  任意归一化。通用多目标及完整工程指标仍未实现。
- 只有显式输入边界的超出距离定义了定量违反量；无解、退化等幅度仍未知，
  未定义统一聚合指标，不推广为工程可行性评价。
- 没有 GA/PSO 引擎、运行服务、持久化/查询、并行执行、收敛历史或统计报告。
- budget 是记录/尝试数量合同，不证明实际算法预算执行，也不保证完成时间。
- TIMEOUT、进程隔离、中止与资源清理仍未实现；CANCELLED 状态不提供取消能力。
- 冻结和重新验证不构成防恶意 Python 内部篡改或来源认证；输入模型仍需正常
  校验入口，W41 证据快照须由真实服务取得。
- 固定绝对容差下 s=1e-10 的理想双解可数值分类为退化；保持 W41 行为，不
  调容差、不夹紧变量、不由少数成功点推导安全搜索域。
- ER-001 未就绪；没有真实工程边界、工作高度映射、独立顶梁 T 轨迹、80 mm
  工程合规或来源升级。本阶段明确只是优化实验合同，不是工程优化。

## 6. 实际验证与工作区

使用既有 venv/bin/python；命令、输出、退出码保存 W42D2_validation.log。

| 检查 | 实际结果 | 退出码 |
| --- | --- | --- |
| W42-D2 专项 | 62 passed，0.55s | 0 |
| W41-D3/D4/D5/D6 + W42-D2 组合 | 339 passed，1.46s | 0 |
| 全量 pytest | 1420 passed，1 warning，15.28s | 0 |
| pip check | No broken requirements found | 0 |
| Git 范围及差异 | 最终实际输出追加到同一验证日志 | 见日志 |

首轮 60 passed、1 failed（退出 1）：发现严格 tuple 与 JSON arrays 不兼容；
修复仅复制集合为不可变 tuple，并新增输入列表独立性测试；最终 62 项通过。
首轮失败输出保留，不用最终结果覆盖。全量 1358+新增62=1420；组合和专项
已包含在全量内，不重复累加。唯一警告仍是既有 StarletteDeprecationWarning，
没有安装其建议包或升级依赖。

测试覆盖五类模型创建、显式单位/完整字段、有限数与严格类型、真实无解/退化/
非法输入/越界、拒绝未经评价/伪造最佳、真实零目标、最小值一致性、预算与
计数、JSON 往返、嵌套冻结/独立快照、工程门禁和算法名字仅作记录。

本次新增模型、测试、本合同及一个实际日志，既有七个未跟踪文件保留不动。
HEAD 保持基线，无既有跟踪文件或暂存区变更。日志被既有 *.log 规则忽略。
没有 git add/commit/push/reset，没有安装依赖或接入专业软件。
开发与测试完成，停止等待人工验收；不宣布工程优化、GA/PSO 或 G1 已完成。
