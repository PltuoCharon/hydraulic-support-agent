# W36-D3 推移千斤顶参数设计契约

## 1. 目标

W36-D3 建立推移千斤顶第一版参数设计边界。

本阶段复用 W36-D2 HydraulicCylinder 基础计算原语，
不复制压力-面积-力公式。

第一版重点覆盖：

- 推力需求对应理论缸径
- 按当前项目已录入缸径系列进行候选圆整
- 候选缸径实际推力
- 已知杆径条件下的实际拉力
- 推/拉需求满足性校核

本阶段不自动生成：

- 活塞杆直径
- 行程
- 工作压力
- 效率系数
- 安全系数
- 厂家型号

无来源参数不得通过经验比例自动补全。


## 2. 第一版输入

必填：

- push_required_kn
- pressure_mpa

可选：

- rod_mm
- pull_required_kn
- stroke_mm

其中：

pressure_mpa 必须由用户或上游工程参数显式提供，
不得自动使用 31.5 MPa 等默认值。

rod_mm 未提供时：

- 不计算 pull_actual_kn
- 不计算 pull_ok
- 不猜测活塞杆直径

stroke_mm 当前仅作为显式工程输入保存，
不参与本阶段力学反算，
不得根据支架型号或缸径自动推断。

## 3. 第一版输出

- bore_calc_mm
- bore_candidate_mm
- push_actual_kn
- push_ok

当 rod_mm 存在时：

- rod_mm
- pull_actual_kn

当 rod_mm 与 pull_required_kn 同时存在时：

- pull_ok

stroke_mm 如果输入则原样返回，
并明确标记为 user_input，
不是系统计算结果。


## 4. 基础计算关系

D3 复用：

app/services/calc/hydraulic_cylinder.py

已有基础原语：

- piston_area
- annular_area
- push_force
- pull_force
- bore_for_push_force
- round_up_standard_bore

基础关系：

A_push = pi * D^2 / 4

A_pull = pi * (D^2 - d^2) / 4

F_push = p * A_push

F_pull = p * A_pull

D3 不复制这些公式实现。

## 5. 推移机构方向边界

“推移千斤顶”是部件名称，
不能仅根据名称推断：

- 推输送机一定使用无杆腔
- 移架一定使用杆腔
- 或相反

具体工作方向取决于推移机构连接拓扑。

因此第一版中的：

push_required_kn

只表示“无杆腔推力设计需求”。

pull_required_kn

只表示“杆腔拉力校核需求”。

不得自动把二者映射成：

- 推输送机力
- 移架力

除非后续获得明确机构连接关系。


## 6. 当前标准证据边界

项目现有 MT/T 556-1996 知识内容支持以下要求：

1. 千斤顶技术特征应包含：
   - 型式
   - 缸径
   - 活塞杆径
   - 额定推力
   - 额定拉力
   - 初推力
   - 初拉力

2. 推移装置：
   - 支架推力不得大于输送机可承受的设计推力
   - 过渡支架推输送机力宜小于 360 kN
   - 新研制重型输送机可增大推力
   - 薄及中厚煤层支架移架力一般为支架重量的 2.5~4 倍
   - 移架时间应满足配套采煤机割煤速度要求

3. 千斤顶应符合 MT97。

4. 千斤顶缸径和活塞杆径应符合 MT/T94。

但是当前项目尚未取得并冻结 MT/T94 的完整尺寸系列表。

因此：

- 可以要求杆径最终符合 MT/T94
- 当前不能凭空生成 MT/T94 活塞杆标准系列
- 当前不能自动推荐杆径
- 当前不能把任意计算杆径声明为标准杆径

bore_candidate_mm 当前仅表示：
按项目现有 GB/T 2348 常用缸径列表向上选择的候选值。

它不等同于 MT/T94 合规判定。

第一版结果必须显式返回：

mt_t94_verified = false

直到 MT/T94 缸径和活塞杆径完整系列完成独立核定。

推移装置 360 kN 与 2.5~4 倍重量属于具体工况规则，
不能无条件作为所有推移千斤顶的通用设计目标。


## 7. Formula Registry

当前 Formula Registry 没有 jack 专用 Formula ID。

现有 F-COL-002 虽然使用同一个基础压力-面积关系，
但其 module 为 column，
不得直接把 F-COL-002 当作推移千斤顶正式 Formula ID。

W36-D3 不创建：

- F-JACK-001
- F-JACK-002
- 或任何新的 Jack Formula ID

后续只有在 Jack 公式来源、验证实例和调用方全部冻结后，
才允许增加正式 Formula Registry 条目。

## 8. Calculation Record

当前 calculation_records 查询服务：

ALLOWED_CALC_TYPES = {"column_design"}

因此 W36-D3 不写入：

calc_type = push_jack_design

否则会产生“数据库已写入但现有只读查询接口无法正常列出”的不一致。

后续必须先扩展 calculation record 契约、
允许新的 calc_type，
并增加查询回归测试，
之后才能持久化推移千斤顶设计记录。


## 9. D3 禁止事项

第一版不得：

- 默认 pressure_mpa = 31.5
- 使用 D/d 固定比例自动生成 rod_mm
- 自动生成 stroke_mm
- 引入 eta
- 引入未核实效率
- 自动生成厂家型号
- 把 support_parts 中的 27SiMn 当作完整千斤顶材料设计依据
- 把 360 kN 作为所有支架固定推力
- 把支架重量 2.5~4 倍无条件转成千斤顶额定力
- 自动判断推输送机和移架对应哪个油腔
- 新增未经审计的 Formula ID
- 写入 push_jack_design calculation record

## 10. D3 实现出口

D3 后续实现只允许形成一个纯服务层：

push_jack_design()

它复用 HydraulicCylinder 基础原语。

第一版实现完成后应至少验证：

- 理论缸径反算
- 当前项目已录入缸径系列的候选圆整
- 明确候选圆整不等同 MT/T94 合规判定
- 圆整后推力
- 已知杆径下拉力
- 推力需求校核
- 可选拉力需求校核
- 非法杆径拒绝
- 无 rod_mm 时不生成拉力结果

API、页面、Calculation Record 和 Formula Registry
均留到后续子任务单独接入。
