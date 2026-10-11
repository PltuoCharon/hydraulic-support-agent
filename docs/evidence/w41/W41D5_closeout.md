# W41-D5 开发收口：外围失效记录与批量适配

项目：液压支架智能辅助设计系统 V3.0。
基线 HEAD：9d82424824949db105ac0435a45dbed64c334958。
开发前实际 HEAD 与基线一致，git status --porcelain 为空。
仓库及父目录检查未发现适用 AGENTS.md。无安装、升级、提交或推送操作。

## 1. 已实现

- 独立外围接口 evaluate_candidate_safely / evaluate_candidates；复用既有 D4
  评价器，不改变冻结算法、目标、数学可行性或异常传播。
- 输入验证与评价执行阶段分离，非法输入没有伪造请求。
- 原始数学结果与程序错误分离；六类状态中的无解、退化有真实结果，输入、
  明确算术异常和其他内部异常有结构化诊断。
- 独立保留 BRANCH_UNRESOLVED、NOT_SOLVER_READY、完整运动不可行语义。
- 显式 ComparisonContract 和 assert_comparison_compatible；目标有限、
  可行、实际已计算且比较条件一致才有排名资格。未实现排名或搜索算法。
- 离散请求数、已记录数、规则双解数和记录比例；异常无样本时为未知。
- 请求、结果、合同独立快照、JSON 往返及入口重新校验。
- 诊断过滤：固定码、阶段和异常类型，不保存未经筛选的异常消息或非法输入。
  可变类型化输入的序列化警告关闭，避免通过警告泄露输入值。

## 2. 状态完成范围

| 状态 | 实现与测试 |
| --- | --- |
| NO_SOLUTION | 已实现并测试真实 W39 单姿态及 W40 边界；保留原结果 |
| DEGENERATE | 已实现并测试真实 W39 单姿态及 W40 边界；保留原结果 |
| INVALID_INPUT | 已实现并测试单位、缺项、非有限值、数值类型、超大整数、边界及重复 JSON 键 |
| NUMERICAL_ERROR | 已实现；真实测试使用既有 D3 尺度算术容量保护，不冒充工程算例 |
| SERVICE_ERROR | 已实现；内部 ValueError、RuntimeError、TimeoutError、结果校验错误用明确命名的故障注入测试 |
| TIMEOUT | 仅合同定义；执行能力 NOT_IMPLEMENTED；拒绝虚假状态，没有真实终止测试 |

KeyboardInterrupt、SystemExit 和 MemoryError 传播。D4 直接调用仍传播原异常
对象。数学失败的 error=null，不等同于异常。最后请求样本相切可有 100%
记录比例，但仍不可行；首姿态失败只有一次真实预检记录。

## 3. 初版验证记录（Unicode 修复前，保留历史）

使用已有 venv/bin/python，按以下顺序执行；命令、输出及退出码在日志保存。

| 检查 | 最终结果 | 退出码 | 日志 |
| --- | --- | --- | --- |
| D5 专项 pytest | 77 passed，0.50s | 0 | W41D5_targeted_pytest.log |
| D4 + D5 pytest | 151 passed，0.58s | 0 | W41D5_combined_pytest.log |
| 全量 pytest | 1310 passed，1 warning，16.41s | 0 | W41D5_full_pytest.log |
| pip check | No broken requirements found | 0 | W41D5_pip_check.log |
| git diff --check / 冻结变更检查 / 完整状态 | 无 tracked/staged 变更，HEAD 不变，6 个新增文件 | 0 | W41D5_git_checks.log |

全量增量：D4 文档基线 1233 + D5 新增 77 = 1310。
既有警告为 fastapi/testclient.py 的 StarletteDeprecationWarning（httpx 弃用）；
没有据此安装或升级依赖。

首轮 73 项通过，保存 W41D5_initial_targeted_pytest.log。补充输入溢出及快照
测试后 76/150/1309 项通过，保存 W41D5_before_diagnostic_hardening.log。
随后发现可变类型化输入序列化警告可能泄露字段，修正并新增一项专项测试，
再按完整顺序得到上表最终结果。初轮和中间结果均保留，不替代最终验证。

测试涵盖成功/失败独立记录、失败后继续、数学三类失败/切点、非法输入、
真实算术容量异常、内部错误保守分类、D4 合同不变、失败及无目标不排名、
真实有限零目标允许比较、不同杆长允许比较、采样/分支/配置/容差/案例/
边界/来源声明不一致拒绝比较、正常/提前/首姿态/未知覆盖、ER-001 门禁、
来源不升级、超时保留能力、快照独立、诊断过滤与 JSON 往返。
零目标使用明确声明的极小不同角度、实际浮点求解得到相同 Cx，仅证明
离散有限零目标资格，不证明连续或工程零运动。

## 4. 实际新增文件

核心及专项测试：

- app/models/linkage_optimization_evaluation.py
- app/services/linkage_optimization_evaluation.py
- tests/test_w41d5_optimization_evaluation_models.py
- tests/test_w41d5_optimization_evaluation_service.py

合同、收口与实际日志：

- docs/evidence/w41/W41D5_failure_contract.md
- docs/evidence/w41/W41D5_closeout.md
- docs/evidence/w41/W41D5_initial_targeted_pytest.log
- docs/evidence/w41/W41D5_before_diagnostic_hardening.log
- docs/evidence/w41/W41D5_targeted_pytest.log
- docs/evidence/w41/W41D5_combined_pytest.log
- docs/evidence/w41/W41D5_full_pytest.log
- docs/evidence/w41/W41D5_pip_check.log
- docs/evidence/w41/W41D5_git_checks.log

Git 最终状态由日志记录：6 个源码、测试和文档文件未跟踪，tracked/staged diff
为空，HEAD 保持基线。7 个 .log 文件已真实保存，但被既有 .gitignore 第 36 行
的 *.log 规则忽略，故不显示在普通 git status 中。本次没有修改忽略规则或
强制暂存。交付不 staging、不 commit、不 push；文件保留在工作区供人工验收。
另对新增文件逐项执行 git diff --no-index --check /dev/null；无空白错误输出，
退出码 1 表示新文件相对空文件存在差异，不表示测试失败。

## 5. 仅合同定义、未实现及工程依赖

- TIMEOUT 只有保留词汇和 NOT_IMPLEMENTED 能力模型；未实现计时预算、
  进程隔离、取消、终止确认或资源清理。其模型拒绝测试不等于终止能力测试。
- 统一数值约束违反量未定义，固定 UNDEFINED/null；没有罚函数或任意替代值。
- 来源没有独立工程核验；source_text 和 REFERENCE_POSE 不升级等级。
- 没有连续角域/工作高度域覆盖、工程目标、工程边界、GA/PSO/NSGA-II。
- 工程 READY、高度映射、附件几何、独立顶梁姿态、T 轨迹及 80 mm 工程验证
  需要真实工程资料；ER-001 仍 NOT_SOLVER_READY。

## 6. 剩余风险及 D6/G1

同步批量可能被一个不返回的候选阻塞。W42 若要求有限等待、无人值守或有界
批量完成时间，可中断执行机制缺失是阻塞项，不能用简单计时替代。
数值内部 ValueError 无可靠细分类证据时保守归 SERVICE_ERROR；不修改冻结
求解器来扩充异常类型。异常时没有可靠部分样本，覆盖未知。
比较采用精确声明匹配，来源不同但可能数值等价的条件也会被保守拒绝。
类型化快照保留设计来源字段，调用者不得把未经筛选的完整记录公开日志化。
继承既有极小尺度/数值条件性和重复首角求解边界，本次不改变这些算法。

本次结论是开发及实际回归检查完成，等待人工验收。
G1 未判定、未宣称通过；W41-D6 负责独立验证与判定。

## 7. 非法 Unicode 输入追踪定向修复

以上测试数字保留为原 D5 开发历史。随后独立复现 JSON_TEXT 含孤立 Unicode
代理项时，输入追踪先于正式验证抛 UnicodeEncodeError，导致批量中断。
本次仅在 _trace 的 UTF-8 编码处局部捕获 UnicodeEncodeError，返回 JSON_TEXT
及 sha256=null，再进入既有正式验证形成 INVALID_INPUT。正常文本继续按原始
UTF-8 字节计算 SHA-256；不删除字符、不保存非法原文或异常消息。

修改范围仅服务、服务专项测试和本收尾文档；冻结文件及其他 D5 合同不变。
新增 6 个测试实例，覆盖高/低孤立代理项、后续非法及有效候选、诊断不泄露、
正常 UTF-8 指纹不变及编码阶段 KeyboardInterrupt/SystemExit/MemoryError 传播。
既有 D4 原异常对象传播测试继续通过。

按指定顺序实际执行：精确复现修复后批量继续，D5 83 passed（0.53s），
D4+D5 157 passed（0.68s），全量 1316 passed、1 个既有警告（17.31s），
pip check 通过；上述退出码均为 0。随后执行 Git 差异、范围及完整状态检查。
实际命令、输出和退出码保存 W41D5_unicode_fix_validation.log；该新增日志也
被既有 *.log 规则忽略，原有 7 份日志不覆盖。最终 Git 结果见该日志。

本次消除该编码错误导致的批量中断；同步任务无法真正超时中止、工程资料
缺失等原风险仍在。未安装依赖、暂存、提交或推送；G1 判定仍留给 D6。

## 8. 人工独立终端复验

基于 Unicode 定向修复后的实际工作区进行独立复验。

- 原缺陷已确认：修复前批量抛 UnicodeEncodeError。
- 修复后复现：UNICODE_FIX_VERIFICATION=PASS。
- D5 专项：83 passed，0.57s，退出码 0。
- D4+D5 组合：157 passed，0.72s，退出码 0。
- 全量回归：1316 passed，1 warning，13.04s，退出码 0。
- pip check：No broken requirements found，退出码 0。
- HEAD：9d82424824949db105ac0435a45dbed64c334958。
- 证据：W41D5_independent_final_pytest.log。

修复前的 77/151/1310 数据仅作为历史记录，
不得替代上述修复后的最终验收结果。

验收范围：软件合同与独立回归。
TIMEOUT 仍未实现可中止执行；G1 尚未判定。
