# W41-D5 外围失效与批量接入合同 V1

项目：液压支架智能辅助设计系统 V3.0。
基线：9d82424824949db105ac0435a45dbed64c334958。
范围：在 W41-D4 统一数学评价器外围保存候选记录，不实现搜索或工程验证。

## 1. 接口与冻结边界

新增模型：app/models/linkage_optimization_evaluation.py。
新增服务：app/services/linkage_optimization_evaluation.py。

- evaluate_candidate_safely(candidate_id, raw_request, comparison_contract=None)
  返回 CandidateEvaluationRecord。
- evaluate_candidates(candidates, comparison_contract=None)
  接收按顺序排列的 (candidate_id, raw_request)，返回同顺序独立记录。
- ComparisonContract.from_request(request) 显式建立比较条件快照。
- assert_comparison_compatible(records) 校验全部记录的资格及同一比较合同；
  条件不满足或列表为空则抛 ValueError。没有自动排名或搜索。

raw_request 支持 dict、JSON 文本及 DesignEvaluationRequest。JSON 入口沿用
D3 的重复键拒绝合同。类型化输入先序列化再校验，不能用模型构造或可变字段
绕过验证。非法输入不能生成有效请求快照。

candidate_id 限制为 1 至 128 个字母、数字、下划线、点或连字符，调用者应使用
不含敏感信息的标识。非法标识、批量重复标识、非法比较合同属于调用配置错误，
抛异常；批量先检查这些配置，再评价候选。候选局部失败不会阻止下一个候选。
输入迭代器自身的异常不是候选失败，也不会被包装。

保持 evaluate_design(request) -> DesignEvaluationResult 原接口、目标函数、
结果模型和异常传播不变。未修改 W38/W39/W40、W41-D3/D4 冻结文件。
预检首角重复求解是 D4 的既有行为，本层不改求解调用链。

## 2. 记录与失效映射

每条记录包含 candidate_id、输入追踪、可用时的请求快照、原始评价结果或
类型化错误（二者恰有一个）、outcome、full_motion_infeasible、
objective_computed、comparison_contract、comparison_status、ranking_eligible、
离散 coverage、未定义违反量、未独立核验来源及超时能力声明。
请求、结果、比较合同均为独立快照；服务返回前再次从序列化内容验证记录。
模型仍可变；比较入口同样重新验证，修改过的对象不得绕过资格检查。

| 状态 | 依据与处理 |
| --- | --- |
| NO_SOLUTION | 来自真实首姿态或运动末样本的 W39 状态；保留完整 D4 结果，不创建程序错误 |
| DEGENERATE | 同上，保留真实退化状态 |
| INVALID_INPUT | 独立输入验证阶段的 ValueError（含 ValidationError/JSON 解码错误）、TypeError、OverflowError 或 RecursionError；无类型化请求，无求解结果 |
| NUMERICAL_ERROR | 已验证输入进入 D4 后抛 ArithmeticError 或其子类；这是明确的算术异常证据，保留异常类型；不宣称定位到具体求解样本 |
| SERVICE_ERROR | 已验证输入后的其他 Exception，包括内部 ValueError、结果 ValidationError、RuntimeError 和 TimeoutError；保守分类 |
| TIMEOUT | 仅保留状态词汇；当前错误模型和结果不变量禁止生成 TIMEOUT 记录 |
| BRANCH_UNRESOLVED | 保留单姿态未解析分支，不猜测分支 |
| NOT_SOLVER_READY | 保留 D4 NOT_RUN 结果；工程和其他未准备案例不调用求解器 |
| FULL_MOTION_INFEASIBLE | 规则全采样遇到相切边界，包括首角或最后请求角相切 |

规则全采样中的 NO_SOLUTION/DEGENERATE 同时具有
full_motion_infeasible=true，从而保留数学失败类型与整段不可行两个维度。
单姿态 TANGENT 沿用 D4 FEASIBLE 语义；它没有目标，不能排名。
数学 INFEASIBLE 的 error=null。执行异常则 result=null，不虚构 ClosureResult、
MotionSegmentResult、失败索引、罚值或前缀目标。

不能由异常类名或消息判断输入错误：阶段决定边界。内部 ValueError 即使消息
看起来像输入校验也归 SERVICE_ERROR。数值算法内部使用 ValueError 的情况没有
可靠细分依据，仍归 SERVICE_ERROR，不用消息匹配猜测 NUMERICAL_ERROR。
不捕获 BaseException：KeyboardInterrupt、SystemExit 等原样传播。
MemoryError 也继续传播，不把资源耗尽当作可恢复候选失败。

## 3. 诊断信息与来源

错误诊断仅保存异常类型、阶段和固定诊断码；不保存 str(exception)、栈、
Pydantic 原始输入值或非法输入正文。原始异常消息可能含令牌、私有路径和
服务数据，故有意不持久化。固定诊断码描述本次可可靠确认的失败边界。

InputTrace 保存表示类型和可确定时的 SHA-256。dict 用排序键的 JSON 表示
生成摘要；JSON 文本按原文本生成摘要；两种表示不保证相同摘要。非 JSON
嵌套对象、循环结构等无法可靠摘要时使用 null；不调用任意对象 repr。
摘要仅用于核对调用方保留的输入，不是加密、匿名化或来源认证。

合法类型化快照按任务要求保留既有 source_text、域和 provenance，属于设计
数据记录，不应无筛选地发布到公共日志。调用方应避免将秘密放入设计来源文本。
SYNTHETIC_MATH、ENGINEERING_REFERENCE 和 readiness 门禁不变。
source_assessment 固定为 NOT_INDEPENDENTLY_VERIFIED；既有 PARTIAL、
engineering_verified=false、Formula/Calculation IDs 原样保留。
case_id 前缀、来源声明或 REFERENCE_POSE 不提升工程核验等级。

## 4. 目标资格与比较

ranking_eligible 当且仅当实际结果为 FEASIBLE、目标状态 COMPUTED、目标值
有限且与显式比较合同 COMPATIBLE。无合同仍可评价和计算目标，但不自动排名。
objective=None 与失败目标 null 均不能变成零或罚值；合法有限零值允许比较。
仍只支持 D4 的 SAMPLED_C_X_RANGE/MINIMIZE/mm，完整规则采样才计算。

比较合同精确比较以下模型内容（包括单位、来源与证据字段）：

- 完整案例与数学域、readiness。
- 目标定义。
- 角度采样列表、方向及计划来源。
- 固定 A/D、参考角、参考分支及来源、数值容差、声明 AD。
- 声明变量边界及其域。

AB/BC/CD 杆长及其候选变量来源不进入比较合同；不同设计变量是允许的。
采用保守的精确声明比较，不推断两个不同来源声明或等价容差是否实质相同。
assert_comparison_compatible 拒绝失败、未评分、无合同或不同合同的记录，
即使这些记录分别在各自合同下具备资格。批量函数允许保存不兼容记录，但将
ranking_eligible=false，不静默丢弃候选或替调用方选定比较域。

## 5. 覆盖与违反量

coverage.scope 固定 DISCRETE_REQUESTED_SAMPLES。

- requested_count：采样计划角数；单姿态为 1；无可验证计划时未知。
- recorded_count：真实结果中记录的计划样本数，包括末端失败边界；不是
  W39 调用次数，重复首角预检不重复计入。
- regular_selected_count：已记录的选定规则 TWO_SOLUTIONS 数，不含切点、
  无解、退化或未解析分支。
- recorded_ratio：recorded_count/requested_count；任一未知则 null。

首姿态预检失败有真实 closure_result，因此 recorded_count=1；不补运动段。
正常运动按 W40 返回样本计数。未执行案例 recorded_count=0；无计划则比例未知。
输入失败没有可靠计划，计数未知。执行异常虽可保留请求数，但没有可靠返回
样本，记录数、规则数和比例均未知，不能推断预检或运动前缀。
记录比例不是规则可行率，更不是连续角域或工程工作高度域覆盖率。
最后一个角相切时比例可为 1，但候选仍不可行。

constraint_violation_status=UNDEFINED，constraint_violation_value=null。
没有统一数值违反量的数学定义，不生成 0、1、归一化量或任意惩罚。

## 6. TIMEOUT 合同与 W42 风险

真正的执行超时需要明确定义预算、截止时刻和执行范围，并可靠停止或取消
超出预算的任务，确认任务已终止、资源已清理、后续候选不被遗留工作干扰。
应区分候选计算截止时间、批量总预算、排队时间和外部服务自身超时。
内部服务抛 TimeoutError 不证明本地求解已被终止，本版本归 SERVICE_ERROR。

简单测量耗时或任务结束后发现超预算，只能描述耗时；不能阻止阻塞、继续
计算、后台资源占用或批量卡死。线程等待超时也不等于终止计算线程。

未来需设计隔离工作进程、父进程截止时间监控、取消/终止及确认、必要时的
强制结束、进程回收、临时文件/连接/子进程清理和结果传递的原子性；支持
协作取消的服务也需确认取消生效。只有这一机制实际实施并独立测试后才允许
产生可证明的 TIMEOUT 记录。

当前 timeout.status=NOT_IMPLEMENTED、can_interrupt=false；无时间预算参数、
进程隔离或取消机制。TIMEOUT 枚举仅合同定义，不能声称执行能力已实现或测试。
若 W42 要求有限等待、无人值守服务或保证批量完成时间，该能力缺失是阻塞项；
本层同步批量可被一个不返回的候选阻塞，不能提供此类运行保证。
有限、可返回的离线合成算例可使用本层，但不因此解除生产超时阻塞。

## 7. 阶段边界

D5：外围记录、异常阶段分类、显式比较资格、离散记录覆盖和保留状态合同。
D6：独立执行验证与 G1 判定；不得将本次开发测试等同于 G1 通过。
W42：在共享评价器上接入算法；本任务没有 GA/PSO/NSGA-II 或优化搜索。
真实工程几何、边界、工作高度映射、顶梁 T 轨迹及工程验证仍需真实资料，
本次不生成、不推断、不解除工程门禁。
