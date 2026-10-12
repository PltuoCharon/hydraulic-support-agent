# W42-D3 Random Search Baseline V1

项目：液压支架智能辅助设计系统 V3.0。
开发基线 HEAD：a533da153ab432c2e4a2a3415a77eb570003bf3b。
范围：首个合成域搜索闭环，用于优化框架验证；不是工程优化或 GA/PSO。

## 1. 设计目标与接口

新增 [app/services/random_optimizer.py](../../../app/services/random_optimizer.py)。
接口：

```python
run_random_search(
    problem: OptimizationProblem,
    *,
    random_seed: int = 0,
    budget: int | None = None,
    run_id: str = "random-search-v1",
) -> OptimizationRun
```

返回的 run.result 为 OptimizationResult，包含所有尝试候选和实际最佳记录。
工程问题返回 status=NOT_RUN、candidate_count=0、result=None，不生成或评价。
random_seed 必须是非负整数，不能为 bool 或 None。budget 默认使用问题预算，
显式预算必须是正整数且不超过 problem.evaluation_budget。参数在采样前校验。
调用示例：

```python
run = run_random_search(problem, random_seed=42, budget=10, run_id="rs-42")
result = run.result
best = result.best_candidate if result is not None else None
```

既有 [OptimizationRun](../../../app/models/optimization_contract.py) 唯一补充为
algorithm_name 允许 RANDOM_SEARCH_V1；不改变字段或既有运行不变量。
这个字段只记录服务身份，随机采样及真实评价位于服务中，不由元数据执行。

## 2. 系统架构与 W41 评价链

```text
OptimizationProblem（重新校验的不可变快照）
    → 独立 random.Random(seed)，按 AB/BC/CD 顺序生成长度
    → 显式边界检查
        → 真正越界：D2 FAILED / OUT_OF_RANGE，无目标，无伪造求解结果
        → 其余：构造 W41 原始评价请求
             → D5 evaluate_candidate_safely()
             → D4 evaluate_design()
             → D3 build_closure_task_from_design()
             → W39 solve_closure() / W40 sweep_rear_link_angles()
    → OptimizationCandidate.from_w41() 绑定真实记录
    → 在排名合格的已评价候选中比较目标
    → OptimizationResult → OptimizationRun
```

真实评价仍只支持 SAMPLED_C_X_RANGE / MINIMIZE / mm。C 为四杆移动铰点，
不是顶梁尖端 T。服务不计算随机目标，也不从未完成运动前缀生成目标。
只有 FEASIBLE、COMPUTED、有限值且比较合同一致的候选能参与最佳选择。
数据模型还独立校验最佳值必须等于已记录合格候选中的最小值。

每次构造请求保留问题比较合同中的案例/域、固定 A/D、参考角/分支、完整
角列表/方向、容差、原声明边界和来源。仅更换 AB/BC/CD。
生成长度标记 CALCULATED/PARTIAL、来源明确为有种子的合成随机样本；这仅
表示随机数计算来源，不是工程核验、Formula Registry 或外部资料认证。
工程 verified 标记不提升，不改变 W41 来源等级。

## 3. Random Search 流程与确定性

1. 重新验证 OptimizationProblem，拒绝绕过验证的坏模型或调用元数据。
2. 未就绪工程问题保持 NOT_RUN；合成 READY 问题取得固定比较合同。
3. 创建私有 Random(random_seed)，不设置或消耗全局 random 状态。
4. 每次按问题三变量顺序，各调用一次 uniform(lower, upper)。
5. 分配确定性标识 rs-000001 等；在当前运行内唯一。
6. 数值有限、正但越界时，保存真实 mm 超出量的 OUT_OF_RANGE；不夹紧。
   非法类型/非有限值等交给原 W41 输入验证，形成 INVALID_INPUT。
7. 其他候选进入 D5/D4 真实评价；以 from_w41 保存状态、请求和结果证据。
8. 无论成功或失败，计入一次尝试；不重试、不丢弃失败、不补额外抽样。
9. 合格候选有更小目标才更新 best；相等时保留先出现的真实候选。
10. 保存全部候选、计数和最佳；完整预算处理完后记录 COMPLETED。

合成运行 budget=N 时恰有 N 条候选记录。budget 计候选尝试（包括输入/边界
失败），不是 W39 调用次数、成功候选数或时间。D4 沿用首角预检和 W40 中
再次求解首角的既有行为，本服务不修改或优化该调用链。

同一问题、seed、budget、run_id 和同一执行环境产生完全相同的完整模型及
JSON。没有时间戳、随机 UUID 或其他不可复现字段。默认 run_id 是固定值，
若未来持久化多个不同实验，调用者应提供运行标识，服务目前没有存储系统。
不承诺不同 Python 版本/数值平台之间位级一致。

## 4. 失败保存与最佳语义

| 状态 | 保存方式 | 最佳/目标处理 |
| --- | --- | --- |
| INVALID_INPUT | W41 独立输入验证错误；无类型化设计时保留 design_vector=None 和 D5 追踪 | FAILED，无 objective_values，不排名 |
| NO_SOLUTION | 保存真实 W39/W40 数学无解及 D5 原始记录 | FAILED，违反幅度未知，不填 0 或罚值 |
| DEGENERATE | 保存真实退化数值结果和来源记录 | 同上，不提升为可行 |
| OUT_OF_RANGE | 显式边界超出距离，unit=mm、source=DECLARED_BOUNDS；没有伪造 W41 记录 | FAILED，无目标，不夹紧或重试 |
| FULL_MOTION_INFEASIBLE | D5 保留相切等完整采样不可行语义 | 无前缀目标，不排名 |
| NUMERICAL_ERROR / SERVICE_ERROR | 复用 D5 阶段分类及固定诊断信息 | 保存 FAILED，继续后续候选 |

正确的 uniform 采样正常不应产生 INVALID_INPUT 或 OUT_OF_RANGE，但防御分支
保留这些事件；测试用明确标注的采样故障注入验证，没有把故障注入当作正常
随机运行或真实数值异常。未知内部采样/模型合同错误仍传播，不伪造失败解。
KeyboardInterrupt、SystemExit、MemoryError 等进程/资源终止继续传播。

全部候选失败时 run.status 仍可 COMPLETED：它表示预算已处理并保存，不表示
优化成功。result.feasible=false、best_candidate=None、objective_vector=()，
failed_candidates=total_candidates。合法有限零目标允许成为最佳；失败绝不
转成零目标、无限优先级、任意大数或其他评分替代值。
最佳仅是本次随机样本中已评价合格候选的最小值，不是全局最优证明。

## 5. 与未来 GA/PSO 的关系

本服务只验证“生成候选→真实评价→类型化保存→资格比较→运行结果”的链路。
未来获授权的 GA/PSO 可复用问题、候选、运行合同和 W41 评价边界，替换的是
候选生成/迭代策略，不是目标或求解器。算法比较需同一问题、配置、目标、
采样计划、变量边界和评估预算，并记录随机种子。

当前没有 GA/PSO 迭代、遗传算子、粒子更新、scipy.optimize、pymoo 或专业
软件接入。Random Search 结果不能冒充这些算法的性能或工程优化证据。

## 6. 当前限制及运行风险

- 仅 SYNTHETIC_MATH/READY，变量仍是 AB/BC/CD；不开放工程变量或 ER-001。
- 仅一个离散 Cx 目标；没有一般多目标、数值违反量聚合或工程目标。
- 搜索数值盒域由显式边界描述，但不证明盒域全部几何数值安全；固定绝对
  容差下的极小尺度分类限制保留，不自动改容差或推导安全阈值。
- 没有真实工作高度映射、顶梁 T 轨迹、质量/强度/干涉或 80 mm 合规验证。
- 同步执行，保存全部候选及 W41 快照；预算/样本数增大会增加内存与运行量。
- 无可中断 TIMEOUT、并行进程、取消、资源清理或有限时完成保证；一个不返回
  的求解任务仍可阻塞，进程终止后不承诺部分结果持久化或恢复。
- 没有数据库、自动运行归档、进度回调、收敛统计或算法效果报告。
- 测试数据和来源均为合成声明，不提升工程来源等级，不代替正式阶段批准。

## 7. 实际验证与交付范围

执行已有虚拟环境，按要求顺序运行；实际命令和完整输出保存
[W42D3_validation.log](W42D3_validation.log)。

| 检查 | 实际结果 | 退出码 |
| --- | --- | --- |
| venv/bin/python -m pytest -q -ra tests/test_w42d3_random_optimizer.py | 27 passed，1.76s | 0 |
| venv/bin/python -m pytest -q -ra | 1447 passed，1 warning，16.91s | 0 |
| venv/bin/python -m pip check | No broken requirements found | 0 |
| git diff --check、git status 及范围检查 | 最终实际输出追加到验证日志 | 见日志 |

全量 1420+新增27=1447，专项包含在全量内。唯一警告为既有
StarletteDeprecationWarning（httpx 测试客户端弃用提示），没有安装建议包。

测试覆盖 seed=42/budget=10 完整相等、N 条记录、不同种子、真实 D4 调用及
目标绑定、真实无解、精确重合圆退化、真实算术容量失败、合法零目标、采样
非法/越界与服务错误隔离、问题及全局随机状态不变、结果/运行 JSON 往返、
工程未运行、非法元数据提前拒绝及终止信号传播。精确退化测试固定采样值
以到达真实 B=D，仍由 W41 求解，未伪造数学结果。

新增：app/services/random_optimizer.py、tests/test_w42d3_random_optimizer.py、
本文件及实际验证日志。修改：app/models/optimization_contract.py 中仅新增
RANDOM_SEARCH_V1 枚举值。没有修改 W39/W40/W41 文件或既有 D2 测试/文档。
已有两个 W41 草案保留不动。日志受既有 *.log 忽略规则约束，不改忽略规则。
没有安装或升级依赖，没有 git add/commit/push/reset。

当前完成 Random Search 合成优化框架验证，不是工程优化。停止等待人工审核。
