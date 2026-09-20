# W35-D7-A F-COL-003 分母语义修正契约

## 1. 裁定

F-COL-003 保持：

r = P_set / P_rated

依据 W35-D2 已核标准证据：

初撑力一般为额定工作阻力的 60%～85%。

因此 F-COL-003 的分母必须是本次设计/校核所采用的工作阻力基准，
不得使用标准缸径圆整后重新计算得到的承载力代替。

## 2. 当前 column_design 映射

当前 column_design 接口中的 p_kn 是本次立柱设计采用的支架工作阻力基准。

在当前接口不新增第二个额定阻力字段的前提下：

F-COL-003 denominator = p_kn

即：

setting_ratio(p_set_kn, p_kn)

不得使用：

setting_ratio(p_set_kn, p_actual)

## 3. p_actual 语义

p_actual 是：

标准缸径圆整后，
按 F_col * n * eta 得到的圆整后计算承载力。

它继续输出为：

p_actual_kn

UI 名称继续为：

圆整后计算承载力

p_actual 不等于 P_rated，
不得作为 F-COL-003 分母。


## 4. 区间语义

F-COL-003 校核区间保持：

60% <= r <= 85%

该区间来自 W35-D2 已核标准证据。

D7-A 不改变区间，
只修正 denominator。

## 5. 辨别性回归案例

输入：

p_kn = 3000 kN
n = 1
p_mpa = 31.5 MPa
eta = 1.0
p_set_kn = 2400 kN

标准缸径圆整后计算承载力约为 3206.3 kN。

正确：

2400 / 3000 = 80.0%

错误旧实现：

2400 / 3206.3 ≈ 74.9%

因此测试必须断言：

setting_ratio_pct == 80.0

同时：

p_actual_kn 仍约为 3206.3

这样可防止未来再次把 p_actual 当作 P_rated。

## 6. 边界

D7-A 不：

- 修改 eta 语义
- 修改标准缸径系列
- 修改 F-COL-001
- 修改 F-COL-002
- 修改 60%～85% 区间
- 新增隐式默认值
- 新增数据库字段
- 开始 Formula Registry UI

D7-A 仅修正 F-COL-003 denominator。
