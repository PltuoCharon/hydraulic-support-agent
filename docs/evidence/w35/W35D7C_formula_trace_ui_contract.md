# W35-D7-C 计算记录 Formula Registry 前端追溯契约

## 1. 目标

在 W35-D6 计算记录详情中，
允许用户从 calculation record 保存的 formula_ids
追溯到 W35-D7-B Formula Registry 只读详情。

D7-C 只消费已冻结接口：

GET /api/formulas/{formula_id}

不创建第二份公式数据，
不在前端硬编码公式正文、来源或验证结论。

## 2. 入口

追溯入口位于：

计算记录详情 Drawer -> Formula ID

recordDetail.formula_ids 中的每一个 Formula ID
显示为可点击标签。

点击标签后请求对应 Formula Registry detail。

D7-C 不改变 calculation record，
不把 Formula Registry 内容写回 calculation_records。

## 3. 展示容器

Formula Registry 详情使用只读 Dialog。

不使用第二层 Drawer。

Dialog 与现有计算记录 Drawer 相互独立，
关闭公式详情不得关闭计算记录详情。

Dialog 不提供编辑、保存、恢复、重算或删除操作。


## 4. 展示字段

Formula detail 按后端返回内容展示：

- formula_id
- module
- name
- status
- formula
- input_vars
- output
- unit
- source
- verification
- current_callers
- notes

前端不得根据 formula_id 自行生成：

- 公式表达式
- 来源
- verification
- notes
- 工程可信度结论

## 5. status 语义

status 直接展示 Registry 返回值。

active 保持 active。

legacy_review 保持 legacy_review。

前端不得：

- 把 legacy_review 显示成 active
- 隐藏 legacy_review
- 因为 current_callers 存在而把公式标成已核实
- 根据 source 文本重新推断 verification 状态

未知未来 status 应显示原值，
不得静默解释成 active 或 legacy_review。

## 6. 证据边界

source、verification、notes
只是 Formula Registry 当前登记内容。

UI 不得把这些字段描述成：

- 完整标准原文
- 参数级 provenance
- 制造依据
- 独立第三方验证结果

D7-C 不实现 parameter_evidence / evidence_sources UI。


## 7. 请求与错误行为

点击 Formula ID 后：

1. 打开公式详情 Dialog；
2. 进入 loading；
3. 调用 GET /api/formulas/{formula_id}；
4. 成功后展示 Registry detail。

请求失败时：

- 不伪造公式内容；
- 不回退到前端硬编码内容；
- 公式详情保持为空；
- 错误提示继续由全局 Axios 拦截器处理。

每次打开新的 Formula ID 前，
必须清空上一条 formula detail，
避免旧内容在 loading 期间被误认为当前公式。

## 8. 只读边界

D7-C 不增加：

- POST /api/formulas
- PUT /api/formulas
- PATCH /api/formulas
- DELETE /api/formulas
- 公式编辑
- 公式状态修改
- 计算记录重算
- 历史参数恢复
- calculation record 修改

## 9. 范围

D7-C 只实现：

计算记录详情 -> Formula ID -> Registry detail

本阶段不：

- 建独立 Formula Registry 管理页面
- 加 Registry 搜索/筛选
- 修改 FormulaCard 全局行为
- 修改工程公式
- 修改后端 Formula Registry schema
- 开始参数级证据数据库
