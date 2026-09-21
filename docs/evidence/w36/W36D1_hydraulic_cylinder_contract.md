# W36-D1 HydraulicCylinder 统一执行元件契约

## 1. 目标

W36 建立统一液压执行元件基础内核 HydraulicCylinder。

目标是为后续：

- 立柱
- 推移千斤顶
- 平衡千斤顶
- 护帮千斤顶
- 侧推千斤顶
- 抬底千斤顶

提供可复用的基础液压缸计算关系。

本契约只冻结公共计算边界。

W36-D1 不实现新的千斤顶业务公式，
不修改现有 column-design 结果，
不修改现有 Formula Registry 状态。

## 2. 分层原则

HydraulicCylinder 只负责液压缸基础物理关系。

Column 负责液压支架立柱业务语义。

Jack 类负责具体千斤顶的载荷、安装、行程和动作语义。

不得为了代码复用，
把立柱专用参数静默下沉到 HydraulicCylinder。


## 3. HydraulicCylinder 公共候选关系

D1 冻结以下通用候选能力：

- piston_area
- annular_area
- push_force
- pull_force
- bore_for_push_force
- standard bore rounding

基础推力关系：

F_push = p * pi * D^2 / 4

工程单位换算：

MPa * mm^2 = N

因此输出 kN 时除以 1000。

杆腔有效面积：

A_annular = pi * (D^2 - d_rod^2) / 4

拉力：

F_pull = p * A_annular

这些基础关系不得包含：

- 支架型号
- 支架工作阻力
- 承载立柱根数 n
- 历史立柱修正系数 eta
- 初撑力比
- canopy_len
- center_dist
- 支护强度
- calculation record context

## 4. eta 边界

HydraulicCylinder 不定义 eta。

现有 active column_design 中的 eta 继续保持：

历史立柱修正系数 eta（物理口径待核）。

eta 不得解释成：

- 液压缸效率
- 支撑效率
- 机械效率
- Ks

不得给 HydraulicCylinder 设置隐式 eta 默认值。


## 5. Column 兼容边界

现有 app/services/calc/column.py
在 W36-D1 保持现有公开行为。

以下入口暂不删除：

- column_force
- bore_diameter
- round_up_bore
- setting_ratio
- design

现有 /api/calc/column-design 契约保持：

- p_kn
- n
- p_mpa
- eta
- p_set_kn

现有返回字段保持兼容：

- d_calc_mm
- d_std_mm
- p_actual_kn
- setting_ratio_pct
- setting_ok

未来允许 column_force 内部复用 HydraulicCylinder.push_force，
但旧公开入口必须继续工作。

bore_diameter 仍属于 Column 层，
因为它同时包含：

- 支架工作阻力 p_kn
- 承载立柱根数 n
- 历史 eta

不得把该函数整体定义成通用液压缸缸径公式。

## 6. F-COL-003 不变

初撑力比仍定义为：

P_set / P_rated

在 column_design 中：

P_rated 映射为 p_kn。

不得使用 p_actual_kn 作为分母。

W36-D1 不修改 F-COL-001 / F-COL-002 / F-COL-003。


## 7. Legacy 边界

以下链保持 legacy：

core.support.Cylinder
-> core.support.Support
-> app.services.support_calc.recalc
-> app.agent.tools.recalc_params

旧 Cylinder.thrust 中的基础压力面积关系可作为数学对拍参考。

但是旧 Support 包含：

- eta 默认值
- resistance 历史公式链
- center_dist
- canopy_len
- intensity 历史公式链

因此不得把 Support 直接迁入新的 active HydraulicCylinder 主链。

旧 support_calc / Agent recalc 不因 W36 而自动升级为 active。

## 8. Strength 边界

app/services/calc/column_strength.py
在 W36-D1 保持独立。

D1 不重构：

- allowable_stress
- wall_thickness
- check_stress
- euler_buckling
- MATERIALS

原因是这些函数涉及：

- 材料口径
- 安全系数
- 壁厚适用范围
- 稳定性边界

它们需要独立证据和后续工程核定。

不得因为 HydraulicCylinder 建立，
就默认所有千斤顶共享相同材料或安全系数。


## 9. Provenance 数据层兼容性结论

真实数据库：

MySQL 8.0.46

数据库：

hydraulic_support

真实 migration 目录：

scripts/migrations/

当前最近 migration：

004_calculation_records.sql

因此后续 provenance 正式 migration
应继续使用该目录和连续编号。

support_models.id 当前类型：

INT AUTO_INCREMENT PRIMARY KEY

因此 W35 draft 中：

parameter_evidence.support_id INT

与现有主键类型兼容。

support_models 与 calculation_records 当前排序规则均为：

utf8mb4_0900_ai_ci

evidence_sources 与 parameter_evidence 当前均不存在。

## 10. D1 禁止事项

W36-D1 不：

- 执行 provenance migration
- 修改 support_models
- 创建 evidence_sources
- 创建 parameter_evidence
- 修改 Formula Registry
- 修改 column-design API
- 修改 eta 语义
- 删除 legacy support_calc
- 修改 ColumnView
- 新增千斤顶正式业务公式

D1 的出口是统一执行元件边界被明确冻结，
后续 D2 才开始实现 HydraulicCylinder 基础内核。
