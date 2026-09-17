# W34D3 ModifyView 迁移分析

## 当前定位

ModifyView 是 W23 时代的“支架部件修改重算”页面。

当前功能链：

已有推荐支架

↓

修改：

- 立柱缸径
- 立柱数量
- 泵站压力

↓

调用旧 /api/recalc

↓

计算：

- setting_load
- working_resistance
- intensity

↓

与旧 requirement 需求值比较

---

## 当前问题

### 1. 计算模型已经进入 legacy_review

/api/recalc：

legacy_review

/api/requirement：

legacy_review

因此 ModifyView 不应继续作为长期主设计页面。

### 2. 与新 Design Center 功能重叠

W33 已有：

- 支护需求
- 立柱缸径
- 立柱强度

后续还将增加：

- 千斤顶
- 阀组
- 管路
- 泵站

继续维护 ModifyView 会形成第二套设计入口。

### 3. 支护面积口径尚未统一

旧链依赖：

beam_length
+
roof_end_distance
+
center_distance

而数据库另有：

center_dist
canopy_len

目前不能认为两套参数等价。

---

## 迁移决定

ModifyView：

状态：

DEPRECATE_AFTER_MIGRATION

不是立即删除。

---

## 迁移内容

### A. 缸径修改

迁入：

设计计算 → 立柱

由：

旧 /api/recalc

迁向：

/api/calc/column-design

---

### B. 工作阻力

以后由统一设计链产生。

不得继续通过：

setting_load / setting_ratio

作为唯一工作阻力设计方法，
除非该公式在 Formula Registry 中重新核实。

---

### C. 支护强度

迁入：

总体设计 / 支护需求与支架参数复算

等待：

支护面积口径完成统一。

---

### D. 泵站压力

不再作为“立柱设计页上的万能修改参数”。

以后进入：

设计计算 → 泵站匹配

同时向立柱/千斤顶提供液压系统边界条件。

---

## 兼容方案

阶段1：

旧 /modify 保留。

页面增加：

“历史计算模块”状态。

阶段2：

结果页“修改部件”按钮改为进入 Design Center。

阶段3：

旧 /modify 自动 redirect 到新设计中心，
但保留 legacy 参数查看。

阶段4：

确认：

- 无前端调用
- 无Agent依赖
- 无测试依赖
- 历史结果可追溯

之后才删除旧页面和 API。

---

## 结论

ModifyView 不作为未来一级功能。

其有价值能力迁移到：

设计计算中心。

其旧计算模型保留为：

legacy evidence

直到 Formula Registry 完成最终裁定。
