# W36.5-D3 真实浏览器 E2E 与 artifacts 治理契约

## 1. 目标

W36.5-D3 不新增工程算法。

本阶段解决两项系统级缺口：

1. 建立第一条真实浏览器 E2E smoke；
2. 治理长期未跟踪的 artifacts 工作目录。

不得开始 W37。

## 2. E2E 技术栈

采用：

@playwright/test + Chromium

原因：

- 当前 web 项目没有浏览器 E2E 框架；
- 当前系统未安装可直接使用的 Chromium / Chrome；
- Playwright 可以提供独立、可复现的测试浏览器；
- E2E 必须覆盖真实 Vue 页面与真实 FastAPI 接口。

Playwright 仅作为 web 开发依赖。

不得把 Playwright 引入生产运行依赖。


## 3. 真实系统链路

E2E 必须经过：

Browser
→ Vite :5173
→ /api proxy
→ FastAPI :8000
→ push_jack_design
→ Vue rendering

不得 mock：

- /api/calc/push-jack-design
- push_jack_design service
- JackView result

允许 Playwright 自动启动：

- FastAPI server
- Vite development server

## 4. Jack smoke 场景

访问：

/#/calc?m=jack

显式输入：

push_required_kn = 300
pressure_mpa = 31.5

点击：

开始计算

必须验证：

- 计算结果出现；
- 候选缸径显示 125 mm；
- 推力需求校核显示“满足”。

31.5 MPa 仅为 E2E 测试输入。

它不得成为：

- JackView 默认值
- API 默认值
- push_jack_design 默认值

不得改变 W36 已冻结的“压力必须显式输入”规则。


## 5. 输入变化结果失效

第一次计算成功后：

修改 push_required_kn。

不得再次点击计算。

浏览器必须观察到：

旧计算结果立即消失。

该测试用于验证：

Vue input
→ form
→ deep watch
→ result invalidation

真实交互链成立。

## 6. 稳定选择器

JackView 可以增加 data-testid。

允许的用途仅包括：

- 推力输入
- 压力输入
- 开始计算按钮
- 结果区域
- 候选缸径
- 推力校核结果
- 空状态

E2E 不依赖：

- 第几个 input
- Element Plus 内部 class
- 自动生成 DOM 层级

data-testid 不改变工程语义。


## 7. artifacts 治理

当前 artifacts 包含：

- audit：可重复生成的阶段审计输出；
- data_recovery：数据恢复过程文件。

正式代码和正式文档当前不依赖 artifacts 路径。

W36.5-D3：

- 在根 .gitignore 忽略 /artifacts/；
- 不删除本地 artifacts；
- 不执行 rm -rf artifacts；
- 不把整个 audit 目录提交进 Git。

data_recovery 文件继续保留在本地。

为关键恢复文件生成 SHA256 manifest，
manifest 进入 docs/evidence/w36，
用于记录恢复资产的完整性。

忽略 artifacts 不等于删除恢复资产。

## 8. 本阶段允许修复的 UI 问题

真实 E2E 若确认现有 JackView 状态文本存在运行时绑定错误，
允许修复：

success / danger
满足 / 不满足

修复仅限：

把静态字符串表达为合法 Vue 字符串。

不得借机修改计算关系、工程参数或 API。

## 9. 完成条件

必须满足：

- Playwright Chromium smoke 可重复运行；
- 使用真实 FastAPI；
- 300 kN / 31.5 MPa 得到候选缸径 125 mm；
- 页面显示推力需求校核“满足”；
- 修改输入后旧结果消失；
- npm run build 通过；
- Python 全量测试通过；
- /artifacts/ 被 gitignore；
- 本地 artifacts 文件未删除；
- data_recovery SHA256 manifest 已生成；
- git diff --check 通过。

完成后进入 W36.5-D4。

不得开始 W37。
