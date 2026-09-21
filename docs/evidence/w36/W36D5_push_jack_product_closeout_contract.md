# W36-D5 推移千斤顶产品级收口契约

## 1. 目标

W36-D5 对已经完成的推移千斤顶设计能力进行产品级收口。

本阶段不新增物理公式，不扩展工程语义。

重点解决：

- 计算结果必须与当前输入保持一致
- 输入改变后不得继续显示旧结果
- 计算失败后不得保留旧结果
- 页面明确显示当前计算依据与标准边界
- 完成 W36 千斤顶功能最终验收

## 2. 结果有效性

JackView 在已经存在计算结果时：

只要任一设计输入发生变化，旧 result 必须失效。

输入包括：

- push_required_kn
- pressure_mpa
- rod_mm
- pull_required_kn
- stroke_mm

第一版采用最保守策略：

输入变化 -> result = null

不采用自动重算。

## 3. 请求失败

每次开始新的计算请求前：

result 必须先清空。

如果 API 请求失败：

- 不恢复旧 result
- 不显示上一轮计算结果
- 错误继续由现有 axios interceptor 提示

不得让旧结果看起来仍对应当前输入。


## 4. 页面计算依据与边界

JackView 增加只读的“计算依据与边界”说明。

必须明确：

- 当前推力和拉力为压力-面积理论计算结果
- 未引入液压效率修正
- 候选缸径来自项目当前已录入的 GB/T 2348 常用缸径列表
- 候选缸径不等于 MT/T94 合规判定
- MT/T94 千斤顶缸径与活塞杆径系列仍待独立核验
- stroke_mm 为用户输入，不参与本阶段力学反算
- 不自动推断推输送机和移架对应的油腔方向

不得增加：

- F-JACK Formula ID
- calculation record
- record_id
- eta
- 默认工作压力
- 自动活塞杆直径
- 自动行程
- 厂家型号推荐

## 5. 现有能力保持不变

保持：

POST /api/calc/push-jack-design

以及：

- push_required_kn 必填
- pressure_mpa 必填且无默认值
- rod_mm 可选
- pull_required_kn 可选
- stroke_mm 可选
- pull_required_kn 需要 rod_mm
- mt_t94_verified = false

不得修改 W36-D3 已冻结的纯计算语义。

## 6. 完成条件

必须满足：

- 输入改变后旧结果自动失效
- 新请求开始前旧结果清空
- 请求失败不恢复旧结果
- 页面显示计算依据与标准边界
- Jack UI 不出现 F-JACK / record_id / FormulaCard
- Vue production build 通过
- Python 全量测试通过
- git diff --check 通过

W36-D5 完成后，W36 千斤顶功能线冻结。
