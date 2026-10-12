# W42-D1 连杆优化范围审计

项目：液压支架智能辅助设计系统 V3.0。
实际 HEAD：a0c8f33133638a6b2b2dd61f873b0dde00e32ab9。
范围：只读审计 W41 遗留优化入口，为后续合成域 GA/PSO 开发明确边界。
本次仅新增本报告，不修改代码、测试、既有文档或占位文件，不接入专业软件。

## 1. 审计结论与当前能力

当前具备“合法候选输入→D3 闭环任务适配→D4 数学评价→D5 独立记录及比较
资格检查”的执行链；没有优化搜索引擎、优化运行模型或工程优化能力。
唯一可选目标是离散 C 铰点的 X 坐标范围，不能解释为顶梁 T 位移。
数值约束违反量未定义，TIMEOUT 无真正中止机制。
证据：[D3 模型](../../../app/models/linkage_optimization.py)、
[D4 模型](../../../app/models/linkage_evaluation.py)、
[D4 服务](../../../app/services/linkage_evaluation.py)、
[D5 模型](../../../app/models/linkage_optimization_evaluation.py)、
[D5 服务](../../../app/services/linkage_optimization_evaluation.py)。

本次用户明确授权 W42-D1 只读审计，故完成该审计。仓库内
[W41-D7 决策文件](../w41/W41D7_gate_decision_draft.md)仍是未签署草案，
建议 BLOCKED_PENDING_SCOPE_RESOLUTION；不能将“进入 W42”或本报告自动
转写为正式 G1 批准、GA/PSO 实施授权或工程范围开放。本报告仅列后续建议。

## 2. 实际检查文件与方法

已阅读或检索的主要文件：

| 文件 | 检查用途 |
| --- | --- |
| app/models/linkage_optimization.py | 设计向量、变量边界、域门禁与固定配置 |
| app/services/linkage_optimization_adapters.py | 候选到 W39 任务的适配及算术容量保护 |
| app/models/linkage_evaluation.py | ObjectiveSpec、约束结果、评价请求与结果不变量 |
| app/services/linkage_evaluation.py | 真正目标计算入口和异常传播 |
| app/models/linkage_optimization_evaluation.py | 批量记录、比较合同、覆盖信息及未实现能力 |
| app/services/linkage_optimization_evaluation.py | 安全候选评价、批量隔离与比较检查 |
| app/models/optimization_objective.py | 已存在的未跟踪零字节占位，无类或实现 |
| docs/evidence/w42/W42D1_design_vector_v2.md | 未跟踪零字节占位，无 V2 合同 |
| docs/evidence/w42/W42D1_optimization_objective_contract.md | 未跟踪零字节占位，无新增目标定义 |
| docs/evidence/w42/W42D1_optimizer_architecture.md | 未跟踪零字节占位，无搜索架构实现 |
| docs/evidence/w41/W41D7_gate_decision_draft.md、W41_closeout_draft.md | 阶段门槛草案及规划差异 |
| docs/evidence/w41/W41D6_targeted_pytest.log、W41D6_independent_full_pytest.log | 已有数值分类及回归证据 |
| requirements.txt | 优化包声明搜索，不安装或探测新依赖 |

另在活动代码目录 app、api、core、src、scripts、tests 中检索 DesignVector、
ObjectiveVector、ConstraintViolation、OptimizationRun、优化入口及 GA/PSO 名称。
未找到 OptimizationRun/ConstraintViolation/ObjectiveVector 实现；GA/PSO 命中
属于历史合同测试文本，没有发现相应搜索引擎。此结论限于实际检查目录，
不把备份、外部系统或未提供的代码算作已接入能力。
requirements.txt 未命中 scipy/pymoo/pyswarms/deap；不据此声称当前环境所有
已安装包都已独立复核。本次没有执行 pytest、pip check 或依赖安装。

## 3. 六项核心核对

### 3.1 DesignVector 定义位置

实际类名为 FourBarDesignVector，位于
[app/models/linkage_optimization.py](../../../app/models/linkage_optimization.py)。
没有发现另一个通用 DesignVector 或可执行 DesignVector V2。

固定顺序：

1. rear_link_length_mm：AB。
2. shield_beam_effective_length_mm：BC。
3. front_link_length_mm：CD。

三者是独立候选参数，单位 mm，有限且严格正，要求显式来源；as_vector()
按该顺序返回三元组。LengthBounds 与 DesignVariableBounds 提供正有限上下
界、lower<upper、闭区间范围及域一致性校验。来源声明不等于独立工程核验。

A 固定为归一化原点，D 为显式固定 x/y，AD 从坐标计算；参考角、参考分支、
来源及 NumericalTolerance 是评价条件，不是当前优化变量。D_y 可以非零。
不要把 D 坐标和 AD 同时改为互不一致的独立变量，也不覆盖 W38 的派生几何。
依据：[D3 变量合同](../w41/W41D3_design_vector_contract.md)。

### 3.2 Objective 评价入口

入口为 evaluate_design(request: DesignEvaluationRequest) -> DesignEvaluationResult，
位于 [app/services/linkage_evaluation.py](../../../app/services/linkage_evaluation.py)。
请求目标由 ObjectiveSpec 定义，只接受 SAMPLED_C_X_RANGE / MINIMIZE / mm。

公式为 max(C_i.x)-min(C_i.x)，仅在 FULL_SAMPLED_REGULAR_MOTION 的所有
请求样本均为选定规则双解、W40 返回 COMPLETED 后计算。单姿态可评价数学
可行性，但不能配置这一运动目标。切点边界即使位于最后请求角，也不评分。
objective=None 保持 OBJECTIVE_NOT_CONFIGURED，值为 null；失败目标也是 null，
指标为空。当前结果只有一个标量 objective_value，metrics 最多一个。
依据：[D4 目标合同](../w41/W41D4_objective_constraint_contract.md)。

C 是四杆前连杆与掩护梁的移动铰点，不是顶梁尖端 T。该代理目标不计算顶梁
位移、支架高度、质量、应力、干涉或 80 mm 工程合规。

### 3.3 ConstraintViolation 结构

没有发现名为 ConstraintViolation 的模型或统一数值违反量实现。
已有 ConstraintOutcome 包含约束类型 SELECTED_POSE / FULL_REGULAR_SAMPLES、
PASS/FAIL/NOT_EVALUATED、reason 与可用时的真实失败 sample_index。
这是一项硬可行性结果，不是数值违反量。

D5 CandidateEvaluationRecord 明确规定：

- constraint_violation_status=UNDEFINED。
- constraint_violation_value=null。

没有违反量的量纲、分量向量、归一化、加权聚合或罚函数定义。后续 GA/PSO
消费者不得把 null 填成 0 或 1，也不能把布尔 FAIL 擅自当作统一违反幅度。
依据：[D5 记录模型](../../../app/models/linkage_optimization_evaluation.py)、
[D5 合同](../w41/W41D5_failure_contract.md)。

### 3.4 OptimizationRun 模型

活动代码检索未发现 OptimizationRun 模型、运行仓库、运行查询/持久化接口。
evaluate_candidates() 返回按输入顺序排列的候选记录列表，不是运行对象。
CandidateEvaluationRecord 也不能替代运行级算法配置与生命周期。

目前缺少运行标识与状态、算法及参数版本、随机种子、代数/评估预算、搜索
边界与比较合同版本、运行历史、最佳候选轨迹、终止原因、失败统计及复现
信息等运行级合同。上述字段是后续设计建议，本次没有实现或假造。

### 3.5 当前支持的搜索空间

实际是可声明/验证/评价的三维连续候选空间，不是已执行的搜索器：

```text
x=(AB, BC, CD)，各分量为显式合成 mm 闭区间内的有限正数
固定：案例、A/D、参考角/分支、角列表/方向、数值容差和来源声明
可行：由给定计划下的 W39/W40 实际数值结果决定
```

不存在全局预设、工程认证或已证明数值安全的搜索盒域。调用方必须显式给出
边界；测试构造器的范围是人工合成范围，不是液压支架设计边界。
只允许 SYNTHETIC_MATH / READY 进入求解。ENGINEERING_REFERENCE，包括
ER-001，仍强制 NOT_SOLVER_READY，禁止假称 READY、verified=true 或域重标。

现有输入模型接受很小的正长度，但与容差相比不可分辨时可能退化；D3 的
算术容量检查只防部分巨大尺度溢出，不定义工程上界或普遍数值安全域。
依据：[D3](../w41/W41D3_design_vector_contract.md)、[D6 矩阵](../w41/W41D6_oracle_matrix.md)。

### 3.6 当前缺失的优化指标

| 类别 | 缺失指标/合同 | 边界 |
| --- | --- | --- |
| 目标 | 一般目标向量、多目标分量、目标归一化/权重、Pareto 比较 | 当前只支持单一 Cx 标量；设计 as_vector 不是目标向量 |
| 约束 | 定量违反量、统一聚合、连续可行性、干涉或工程约束 | 未定义者保持未知，不生成罚值 |
| 搜索效果 | 收敛轨迹、最佳目标随评估次数变化、可行候选比例、失败类型统计 | 单条记录可提供部分原料；尚无运行级汇总或搜索过程 |
| 对比复现 | 随机种子、重复运行分布、基准/最优差距、相同评估预算下 GA/PSO 比较 | 评价器确定性不能替代随机算法复现验证 |
| 效率与可靠性 | 实际耗时、资源消耗、评估预算、取消/中止及有限时完成保证 | 当前同步批量无可中断 TIMEOUT |
| 工程指标 | T 点轨迹、全工作高度域位移、80 mm 合规、质量、强度、稳定性等 | 需要真实几何/工况/公式证据，本阶段不扩大至工程优化 |

## 4. 已实现接口及接入合同

| 接口/模型 | 位置 | 实际用途与边界 |
| --- | --- | --- |
| FourBarDesignVector.as_vector() | linkage_optimization.py | 固定顺序三长度输出，非目标向量 |
| CandidateDesignInput / DesignVariableBounds | linkage_optimization.py | 候选、边界、来源和域校验 |
| build_closure_task_from_design(candidate) | linkage_optimization_adapters.py | 重校验输入，构造 W39 任务，不搜索或修改求解器 |
| evaluate_design(request) | linkage_evaluation.py 服务 | D4 原评价入口，保留异常传播 |
| evaluate_candidate_safely(id, raw, comparison_contract=None) | linkage_optimization_evaluation.py 服务 | 保存单候选真实结果或阶段化错误，不造解/目标 |
| evaluate_candidates(candidates, comparison_contract=None) | 同上 | 同步、按顺序批量，候选局部异常可记录后继续 |
| ComparisonContract.from_request(request) | linkage_optimization_evaluation.py 模型 | 冻结比较条件的独立快照 |
| assert_comparison_compatible(records) | linkage_optimization_evaluation.py 服务 | 检查全部记录可比较，不实施排序或搜索 |
| CandidateEvaluationRecord / SamplingCoverage | linkage_optimization_evaluation.py 模型 | 请求/结果/错误快照、资格和离散样本记录信息 |

排名资格要求 FEASIBLE、COMPUTED、有限目标和 COMPATIBLE；合法目标 0 可用，
失败或无目标不能填零。无显式比较合同可评价但不可自动排名。
比较校验案例/域、目标定义、角列表/方向、分支、固定配置、容差、声明边界
及来源；AB/BC/CD 作为优化变量，其值不同不造成比较拒绝。

NO_SOLUTION/DEGENERATE 保留数学结果；BRANCH_UNRESOLVED、NOT_SOLVER_READY
及 FULL_MOTION_INFEASIBLE 保持独立语义。INVALID_INPUT 在独立输入阶段归类；
明确算术异常归 NUMERICAL_ERROR，其他内部异常保守归 SERVICE_ERROR。
内部 ValueError 不自动归输入错误。TIMEOUT 仅保留词汇，当前不产生超时记录。
KeyboardInterrupt、SystemExit 和 MemoryError 继续传播。
依据：[D5 合同](../w41/W41D5_failure_contract.md)。

覆盖是 requested_count、recorded_count、regular_selected_count 与 recorded_ratio。
首姿态失败记一次真实尝试，异常无可靠样本时相关计数/比例未知；记录比例
不证明规则可行率、连续角域或工作高度覆盖。

## 5. W42 GA/PSO 开发边界与修改建议

以下是未来获授权后的建议，不是本次代码变更：

1. 复用现有三长度 DesignVector、D4 评价器和 D5 候选记录；新增搜索消费层，
   不复制评价器、不更改 W39/W40 分支与停止语义，不扩大优化变量到工程附件。
2. 先明确单目标合成范围、显式边界和固定比较合同；GA/PSO 的初始化、交叉/
   变异或粒子更新不得静默替换案例、角域、分支、来源、单位或容差。
3. 单独定义 OptimizationRun 及运行级复现/终止/汇总合同，再开发搜索引擎。
   空占位文件与未来文档必须经过真实实现和专项验证后才算能力。
4. 在数值违反量尚未定义时，只能按已明确的可行性/评分资格筛选；不可给
   无效候选任意零分或罚分。算法若需要不合法候选排序，须先定义并审查数学
   规则，不能靠选择一个“大数”掩盖失败语义。
5. GA/PSO 比较采用同一目标、边界、配置、采样和评估预算，记录随机种子及
   多次运行结果；增加搜索层测试，保留现有 D4/D5/D6 回归与 Oracle。
6. 新搜索范围先补独立数值证据，不能用几个尺度点推导普遍安全下限，也不能
   仅凭输入范围校验通过认定该候选的理想数学状态可可靠恢复。
7. 本阶段仅人工监督、合成离线实验；若后续要求有限等待或无人值守，先独立
   实现并验证隔离、中止和资源清理。计时和服务 TimeoutError 不能替代中止。
8. 不引入真实工程几何、工程边界、T/80 mm 合规、CAD/仿真等专业软件接入；
   不升级来源等级。规划范围与门槛的正式处理另行记录，本审计不代为批准。

## 6. 风险列表与已有验证证据

| 风险 | 证据 / 当前影响 |
| --- | --- |
| 数值分类随尺度变化 | [D6 专项日志](../w41/W41D6_targeted_pytest.log)：固定 absolute_mm=1e-9、relative=1e-12 下，s=1、1e-8 为双解；s=1e-10 理想双解但程序退化。可能漏掉理想可行候选，不是伪优或输入错误 |
| 合成盒域未普遍验证 | [D6 矩阵](../w41/W41D6_oracle_matrix.md)只验证有限输入，不能将 s≥1e-8 或测试上界 20 mm 解释为通用安全域 |
| 目标被误读成工程性能 | [D4 合同](../w41/W41D4_objective_constraint_contract.md)明确 C 铰点代理，不是 T 或工程合规 |
| 失败候选被消费者填零 | [D5 合同](../w41/W41D5_failure_contract.md)要求资格检查；未来搜索层若绕过此合同仍可能制造伪优成绩 |
| 运行模型和预算缺失 | 无 OptimizationRun 或搜索记录，难以复现随机搜索、核对评估预算或审计最佳候选来源 |
| 同步批量阻塞 | TIMEOUT 未实现；一个不返回任务可阻塞后续候选，不能承诺有限时完成 |
| 来源与域误提升 | source_text/REFERENCE_POSE 是声明及解析语义，不是工程核验；ER-001 未就绪 |
| 极端数值与历史合同差异 | [D3 合同](../w41/W41D3_design_vector_contract.md)保留正长度输入与历史近零政策差异；超大尺度保护不覆盖所有病态条件 |
| 尚未批准的范围被当成既成事实 | [D7 草案](../w41/W41D7_gate_decision_draft.md)仍未批准；本次只读审计授权不等于优化搜索/工程准入 |
| 空文件被误算为实现 | 四个现存 W42 相关占位均为 0 字节，无新增 DesignVector V2、Objective 或搜索架构能力 |
| 依赖兼容告警 | [D6 人工全量日志](../w41/W41D6_independent_full_pytest.log)保留 Starlette/httpx 弃用警告；本次不升级依赖 |

历史验证：D6 专项 42 passed（0.32s，日志退出 0），人工全量 1358 passed、
1 warning（15.19s；退出 0 由 [D6 人工收口](../w41/W41D6_closeout.md)记载）。
这是 W41 的已有证据，不是本次重跑结果，也不证明 GA/PSO 已存在或工程优化
已完成。D5 83 项修复后测试与原异常传播、失败资格合同见
[D5 收口](../w41/W41D5_closeout.md)，本次未新增测试结果。

## 7. Git 状态与本次改动

审计前 HEAD 为 a0c8f33133638a6b2b2dd61f873b0dde00e32ab9；已有 6 个未跟踪
文件：两个 W41 草案、一个空 Python 占位和三个空 W42 文档占位。
这些均作为既有工作区内容保留，本次不覆盖、不删除、不暂存。

本次唯一新增为 docs/evidence/w42/W42D1_optimization_audit.md；代码改动为零。
最终检查要求已跟踪文件和暂存区均无差异，原 6 个未跟踪文件仍保留，加上
本报告共 7 个未跟踪文件。未执行安装、git add/commit/push/reset 或专业软件
接入。本次完成只读范围审计，停止等待人工审阅，不宣称工程优化完成。
