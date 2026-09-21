# W36-D4 推移千斤顶 API / UI 接入契约

## 1. 目标

W36-D4 将 W36-D3 已验证的 push_jack_design()
接入现有设计计算中心。

本阶段新增：

- POST /api/calc/push-jack-design
- 前端 postPushJackDesign()
- JackView.vue
- /calc?m=jack 可访问

本阶段不新增任何新的物理计算关系。

所有计算必须调用：

app/services/calc/push_jack.py

不得在 Router 或 Vue 页面复制压力、面积、推力、拉力公式。

## 2. API 请求

请求模型：

PushJackDesignReq

必填：

- push_required_kn: float
- pressure_mpa: float

可选：

- rod_mm: Optional[float]
- pull_required_kn: Optional[float]
- stroke_mm: Optional[float]

pressure_mpa 无默认值。

不得默认 31.5 MPa。

不得由 API 自动生成：

- rod_mm
- stroke_mm
- eta
- 安全系数
- 厂家型号

缺少必填 Pydantic 字段时，
保持 FastAPI 当前行为，返回 HTTP 422。

业务参数违反纯计算内核约束时，
保持当前 calc 路由风格：

HTTP 200

{
  "code": 1,
  "msg": "..."
}


## 3. API 成功响应

POST /api/calc/push-jack-design

成功时：

{
  "code": 0,
  "data": {
    ...
  }
}

data 必须直接来自 push_jack_design()。

第一版可能包含：

- push_required_kn
- pressure_mpa
- bore_calc_mm
- bore_candidate_mm
- push_actual_kn
- push_ok
- mt_t94_verified

可选：

- rod_mm
- pull_required_kn
- pull_actual_kn
- pull_ok
- stroke_mm
- stroke_origin

## 4. Calculation Record

W36-D4 不调用：

create_calculation_record()

不写入：

calc_type = push_jack_design

API 返回中不得伪造：

record_id

现有 calculation_records 仍保持 column_design 范围。

## 5. Formula Registry

W36-D4 不增加 F-JACK-*。

Jack API 和 JackView 不得把：

F-COL-001
F-COL-002
F-COL-003

显示为千斤顶正式 Formula ID。

第一版 JackView 不显示 FormulaCard。


## 6. 前端 API

web/src/api/index.js 新增：

postPushJackDesign(data)

调用：

POST /api/calc/push-jack-design

现有 axios interceptor 会：

- code=0 时直接返回 body.data
- code!=0 时 Promise reject

因此 JackView 必须直接接收计算结果。

不得再次读取：

result.code
result.data

## 7. JackView 输入

页面标题：

推移千斤顶参数设计

必填：

- 无杆腔推力需求 / kN
- 工作压力 / MPa

可选：

- 活塞杆直径 / mm
- 杆腔拉力需求 / kN
- 行程 / mm

初始状态下：

push_required_kn = null
pressure_mpa = null

不得在页面初始化时预填：

31.5 MPa

rod_mm 和 stroke_mm 不得自动生成。

如果填写 pull_required_kn 但未填写 rod_mm，
前端应阻止提交并给出明确提示。

后端仍保留相同依赖校验作为最终守门。


## 8. JackView 结果

结果区至少显示：

- 理论缸径
- 候选缸径
- 实际无杆腔推力
- 推力需求校核

rod_mm 存在时显示：

- 活塞杆直径
- 实际杆腔拉力

pull_required_kn 存在时显示：

- 杆腔拉力需求
- 拉力需求校核

stroke_mm 存在时显示：

- 行程
- 明确标记“用户输入”

必须显示：

MT/T94 尺寸系列核验状态

当：

mt_t94_verified == false

页面必须显示警告语义，例如：

“当前候选缸径仅按项目已录入的 GB/T 2348 常用缸径列表圆整，
尚未完成 MT/T94 千斤顶缸径和活塞杆径系列核验。”

不得把 bore_candidate_mm 显示为：

- MT/T94标准缸径
- 标准千斤顶缸径
- 已验证标准尺寸

推荐使用：

“候选缸径”


## 9. CalcCenter 接入

CalcCenterView.vue：

validModules 增加：

jack

新增：

import JackView from "./JackView.vue"

module-stage 增加：

JackView
v-else-if="mod === 'jack'"

千斤顶导航项删除：

disabled: true

阀组和泵站继续 disabled。

不新增新的 Vue Router path。

现有：

/calc

继续作为计算中心入口。

通过 query：

/calc?m=jack

进入千斤顶设计。

页面总说明允许同步调整为：

“围绕支护需求、立柱与千斤顶参数进行可追溯的参数化工程计算。”

但是不得宣称 Jack 当前已经完成 Formula Registry
或 Calculation Record 追溯。


## 10. W36-D4 禁止事项

不得：

- 修改 push_jack_design() 公式语义
- 默认 pressure_mpa
- 自动生成 rod_mm
- 自动生成 stroke_mm
- 引入 eta
- 加入 D/d 经验比例
- 自动使用 360 kN
- 自动使用支架重量 2.5~4 倍
- 自动判断推输送机/移架对应哪个油腔
- 写 calculation_records
- 创建 F-JACK Formula ID
- 显示伪造 record_id
- 显示 Jack FormulaCard
- 宣称 MT/T94 已核验
- 把 bore_candidate_mm 标成 MT/T94标准缸径

## 11. D4 完成条件

后端：

- push-jack-design 成功 API 测试
- 非法输入 API 测试
- 缺少必填字段 422 测试
- 无 calculation record 副作用测试

前端：

- API wrapper 存在
- jack 加入 validModules
- jack 导航开放
- JackView 条件渲染
- required 输入无默认值
- pull_required_kn 对 rod_mm 有依赖保护
- MT/T94 未核验警告可见
- 不出现 F-JACK / record_id / FormulaCard

最终要求：

- Python 全量测试通过
- npm build 通过
- git diff --check 通过
