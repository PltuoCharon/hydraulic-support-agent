# W35-D5 立柱设计参数语义与证据契约

## 1. 范围

W35-D5 只收口当前 column_design 主链的参数语义、来源表达和默认值边界。
不新增 CAD / FEA，不重构强度校核，不改变 D3 参数传递和 D4 计算记录架构。

## 2. 参数裁定

### n

canonical label: 承载立柱根数

定义：参与本次承载计算的立柱数量。

### p_mpa

canonical label: 立柱工作压力

单位：MPa。

不得在同一主链中交替称为“设计工作压力”“系统压力”“泵站压力”，除非另有明确来源证明这些量在具体计算中等同。

### eta

canonical label: 历史立柱修正系数 η（待核）

当前状态：provisional semantics。

规则：

- eta != Ks。
- eta 不得称为“支撑效率”。
- eta 不得由 Ks 自动映射。
- active column_design 主链中 eta 必须显式输入。
- active column_design API 和核心函数不得隐式使用 eta=0.9。
- param_dependencies 中历史 eta=0.9 继续作为 legacy 元数据保留；D5 不把它升级为标准默认值。
- 数据库现有《煤矿支护手册》文字来源缺少可核 locator 旼，不得据此声称 0.9 已完成标准/文献级核验。

## 3. F-COL-001

F-COL-001 保持 active implementation：

P = n * (pi/4) * D^2 * p * eta

反算：

D = sqrt(4P*1000/(n*pi*p*eta))

但必须明确：

- 这是当前项目参数化立柱计算关系。
- eta 语义仍为 provisional。
- GB/T 2348 只用于标准缸径系列来源，不得写成“整个含 eta 的公式均由 GB/T 2348 直接规定”。

## 4. F-COL-002

单柱推力：

F_col = p * pi * D^2 / 4 / 1000

该式与 eta 分离。

圆整后总承载计算仍按当前主链：

P_calc = F_col * n * eta

在 eta 语义未完成核定前，UI 不得把 P_calc 表述为“实际承载力”，统一使用：

圆整后计算承载力

## 5. F-COL-003

初撑力比：

r = P_set / P_rated

60%~85% 校核区间继续使用现有 W35-D2 已核标准证据。
Registry / UI / source 文案应引用 W35-D2 已核证据，不再只写“设计惯例”。

D5 不自动补齐 p_set_kn。

## 6. SOURCE 表达

计算结果 source 必须把三件事分开表达：

1. 标准缸径系列来源；
2. 当前项目计算关系；
3. eta 为显式输入且物理口径待核。

不得使用可能暗示 GB/T 2348 为 eta 或整个 F-COL-001 提供直接依据的合并措辞。

## 7. 默认值边界

“填入计算示例”仍可显式写入：

- p_kn=2533
- n=1
- p_mpa=31.5
- eta=1.0
- p_set_kn=1900

这些值只属于 example，不是工程默认值。

direct column_design：

- p_kn required
- n required
- p_mpa required
- eta required
- p_set_kn optional

## 8. 数据库边界

W35-D5 不删除 param_dependencies 中历史 eta 行，也不修改 legacy support_calc 的行为。

active column_design 与 legacy support_calc 的 eta 语义必须继续隔离。

后续若获得《煤矿支护手册》的版本、页码、章节或其他可复核原文，再单独升级 eta 的 evidence 状态。

## 9. 非目标

W35-D5 不做：

- eta -> Ks 映射；
- 固定 eta=0.9；
- 自动从推荐支架推断 eta；
- 自动从工作压力推断初撑力；
- 材料强度参数重核；
- CAD / FEA / 制造级设计结论。
