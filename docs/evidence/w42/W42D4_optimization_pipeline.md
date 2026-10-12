# W42-D4 Optimization Evaluation Pipeline V1

项目：液压支架智能辅助设计系统 V3.0。
开发基线 HEAD：ae3a72d48541cd5e25d64d26562132d3c66d6f1b。
范围：合成优化基础评价设施，不是工程优化或 GA/PSO。

## 1. 设计目标与交付

统一 OptimizationCandidate 的评价、失败记录、批量统计及最佳选择入口。
每条记录绑定新的 W41 评价证据，不能把历史 objective_values 或候选标签
当作本次已评价成绩；同时保留输入历史，避免重评价时丢失旧失败原因。

新增：

- [app/models/optimization_pipeline.py](../../../app/models/optimization_pipeline.py)
- [app/services/optimization_pipeline.py](../../../app/services/optimization_pipeline.py)
- [tests/test_w42d4_optimization_pipeline.py](../../../tests/test_w42d4_optimization_pipeline.py)
- 本合同及 [W42D4_validation.log](W42D4_validation.log)

没有修改 W39/W40/W41、DesignEvaluationResult、OptimizationContract、
Random Search 服务或已有测试。没有安装依赖或接入专业软件。

## 2. 数据模型

### OptimizationEvaluationRecord

| 字段 | 语义 |
| --- | --- |
| candidate_id | 与输入和本次评价候选标识一致 |
| evaluation_status | SUCCESS / FAILED，依据本次实际 W41 比较资格，不使用历史状态冒充 |
| objective_values | 既有 ObjectiveValue 元组，含名称、有限值、mm、MINIMIZE；失败为空 |
| feasible | 本配置下完整规则采样成功且目标可比较，非工程可行性 |
| violations | 既有 ConstraintViolation 元组；保留原始失败与新失败，去除完全重复项 |
| source | 固定 W41_EVALUATOR；表示 W41 入口处理来源，不表示工程认证或一定运行过求解器 |
| input_candidate | 不可变的原输入候选，包含已有请求/错误/目标历史 |
| evaluated_candidate | 绑定新的 D5 CandidateEvaluationRecord 快照的候选 |
| request_mode | REPLAY / DESIGN_VECTOR / MISSING_DESIGN / READINESS_GATE |
| failure_reason | 新 W41 outcome 及固定诊断码/实际约束原因；成功时 null |

模型验证：标识、问题、变量与真实证据一致；REPLAY 保留完整原始类型化请求；
SUCCESS/feasible/目标必须来自新的可比较结果；失败信息不能删除或改写。
新模型冻结且深层结构由既有不可变模型及 tuple 组成；JSON arrays 转换为
独立 tuple，往返后不变量仍生效。访问 W41 快照返回独立验证对象。

### OptimizationPipelineResult

| 字段 | 语义 |
| --- | --- |
| records | 完整候选评价记录，不能仅保留统计而丢失失败原因 |
| total_candidates | 本批输入候选数 |
| evaluated_candidates | 本批已由 W41 入口处理并形成记录的次数，包括输入校验失败/未就绪门禁 |
| successful_candidates | SUCCESS 记录数 |
| failed_candidates | FAILED 记录数 |
| best_candidate_id | 实际 SUCCESS、feasible=true 且目标最小的记录标识；无则 null |
| best_objective | 完整 ObjectiveValue（使用 .value 读取数值、.unit 读取单位）；无则 null |

正常返回时每个输入都调用一次 W41 安全入口，因此 total=evaluated=success+failed。
这些数目不是 W39 调用次数、数学求解完成次数或工程已验证数量。门禁返回
NOT_RUN 仍产生一条 FAILED 流水线记录，数学未执行事实保留在 W41 快照中。
空列表返回全部计数为 0、records=()、两个最佳字段均 null。
聚合模型校验全部计数、同一问题、唯一标识、预算及最佳值来源。

## 3. 服务接口与数据流程

```python
pipeline = OptimizationEvaluationPipeline()
record = pipeline.evaluate_candidate(candidate)
summary = pipeline.evaluate_candidates(candidate_list)
best_record = pipeline.select_best_candidate(summary.records)
```

select_best_candidate 输入的是评价记录列表，返回完整最佳记录或 None。
它重新校验记录，仅筛选 SUCCESS 且 feasible=true 的记录，再按真实目标值
最小选择；失败不参与排序、不分配罚值，等值时保持输入顺序。

```text
OptimizationCandidate 重新验证及独立快照
    → 获取原请求或按明确模式构造输入
    → W41-D5 evaluate_candidate_safely()
    → W41-D4 evaluate_design()
    → 既有 D3 / W39 / W40 链（仅满足门禁时）
    → OptimizationCandidate.from_w41()
    → OptimizationEvaluationRecord
    → 批量统计、资格筛选、最小目标选择
    → OptimizationPipelineResult
```

批量先复制并校验所有候选，不修改调用者列表或顺序。相同标识、不同问题/
比较合同或超过问题预算在调用 W41 前拒绝，作为调用配置错误抛 ValueError。
一批必须具有完全一致的 OptimizationProblem；同一问题中 AB/BC/CD 取值
不同是正常候选变化，不影响比较资格。输入模型本身损坏时也不伪造失败对象。

## 4. 请求模式与 W41 关系

- REPLAY：已有有效类型化 W41 请求时，使用原请求完整独立快照，重新评价。
  Random Search 的正常/数学失败记录走此路径；保留全部原变量与来源元数据。
- DESIGN_VECTOR：没有旧请求但有设计向量时，从问题固定比较合同构造原始
  输入，仅填 AB/BC/CD 及来源；单位保持 mm，条件/分支/角域/容差不变化。
  新声明标记 USER_INPUT/PARTIAL，表示本次提供的设计数据，不作外部核验。
- MISSING_DESIGN：D5 为安全原因未保留非法原始输入，且没有可验证设计时，
  明确将缺失 candidate 交给 W41 输入验证，得到失败；不假称重放原非法数据。
  原 INVALID_INPUT 记录、追踪和诊断仍在 input_candidate 中完整保留。
- READINESS_GATE：工程问题没有可用比较合同和旧请求时，仅提交问题的案例/
  域/readiness 元数据，objective=None；不构造几何，沿用 W41 NOT_RUN 门禁。

不复制闭环、分支、运动、目标计算或失效分类算法。所有新目标仅取自新
W41 metrics；C 仍是四杆移动铰点，不是顶梁 T。原 DesignEvaluationResult
与原直接调用异常传播合同不变。默认重新评价，不引入缓存。

Random Search 接入示例：

```python
run = run_random_search(problem, random_seed=42, budget=10)
summary = OptimizationEvaluationPipeline().evaluate_candidates(run.result.candidates)
```

本阶段直接接受 Random Search 的现有输出，不修改搜索服务、不在该服务里
重复嵌入流水线。此接入会产生新的 N 次评价尝试；原 run/result 历史不变。
流水线预算与统计是本批次口径，不是跨搜索/复验步骤的累计预算台账。

## 5. 失败处理与原因保留

数学无解、退化、相切边界继续保留真实 W41 结果；输入、数值和服务错误沿用
D5 分类和诊断过滤，不保存未过滤的原始异常消息。内部 ValueError 不冒充
INVALID_INPUT。单候选可预期失败产生 FAILED，批量继续后续候选。

已知 OUT_OF_RANGE 的原始 mm 超出量保留；重新提交时 W41 的输入验证可能
同时返回 INVALID_INPUT。violations 同时保留这两个事实，不把边界事件转换
成数学无解，不删除旧原因、不产生伪造求解结果或零目标。
缺少几何的工程记录保持 NOT_SOLVER_READY，原 W41 execution_status=NOT_RUN
完整保存；外层 FAILED 仅表示没有可比较成绩，不是工程求解已失败。

历史 transient SERVICE_ERROR 也不会抹去：若实际重新评价现在成功，新的记录
可以 SUCCESS 并排名，历史失败仍保留在 input_candidate。成功必须有新的
真实计算证据，不能依据旧状态或旧目标直接升格。新的 FAILED 始终禁止排序。

所有失败的 objective_values=()，最佳字段不由 0、Infinity 或罚值填充。
合法完整评价得出的有限目标 0 允许；全部失败最佳为 null。
无解/退化等未知幅度继续 null，不发明统一数值违反量。
KeyboardInterrupt、SystemExit、MemoryError 等继续传播，不伪造恢复或部分结果。

## 6. 当前限制

- 仍只开放既有合成域和 AB/BC/CD，不开放工程变量、资料补造或专业软件接入。
- 只支持 SAMPLED_C_X_RANGE 单目标与完整规则离散采样；不存在一般目标向量、
  权重、Pareto 或工程目标；best 是已记录候选的最小值，不是全局最优证明。
- 同步、非缓存流水线，重复接入已评价结果会再次调用 W41；没有跨调用累计
  预算或全局运行账本，不能把本批计数当作整个搜索运行的总消耗。
- 保存输入与新证据，快照随候选数/样本数增长；无数据库、流式持久化、
  并行执行、进度回调或恢复机制。
- 可中断 TIMEOUT、取消和资源清理仍未实现；不保证有限时完成。
- 数值尺度/近退化限制、离散不证明连续域覆盖等 W41 既有边界保持不变。
- W41 来源标签和本层 W41_EVALUATOR 不证明外部记录真实性或工程验证等级。
- 没有 GA/PSO、顶梁 T/工作高度链、80 mm 工程合规或工程优化完成声明。

## 7. 实际验证及 Git 范围

使用现有 venv/bin/python，按用户要求顺序执行，结果与退出码见
[W42D4_validation.log](W42D4_validation.log)。

| 检查 | 实际结果 | 退出码 |
| --- | --- | --- |
| venv/bin/python -m pytest -q -ra tests/test_w42d4_optimization_pipeline.py | 33 passed，1.82s | 0 |
| venv/bin/python -m pytest -q -ra | 1480 passed，1 warning，17.86s | 0 |
| venv/bin/python -m pip check | No broken requirements found | 0 |
| git diff --check / git status -sb / 范围核对 | 最终实际结果追加到同一日志 | 见日志 |

全量 1447+新增33=1480；专项已经包含于全量。唯一警告为既有
StarletteDeprecationWarning，没有安装建议包或升级依赖。
测试涵盖单候选真实评价、混合/全部失败、真退化、计数与最佳来源校验、
序列化、不改变输入列表、Random Search 真实重评价、缺失原设计、越界原因
保留、服务错误隔离、历史失败保留、合法零目标、空输入、混合条件/重复/
超预算提前拒绝、工程门禁及进程终止信号传播。服务故障注入均明确标注，
不冒充真实数值算例。

本次仅新增两份模型/服务、专项测试、本合同与实际日志。既有已跟踪代码、
测试与合同不修改，已有两个 W41 草案保留。日志受既有 *.log 忽略规则约束。
不执行 git add/commit/push/reset，不安装依赖。当前只完成优化基础评价设施，
不是工程优化，停止等待人工审核。
