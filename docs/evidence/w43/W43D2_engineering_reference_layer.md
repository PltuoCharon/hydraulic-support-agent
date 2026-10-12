# W43-D2 Engineering Reference Layer

## 1. 设计目标

建立工程参考隔离层。

核心原则：

SYNTHETIC_MATH 证据
不能混淆为
ENGINEERING_REFERENCE。

所有进入优化系统的
工程定义与参数
必须登记来源
与验证等级。

目标：

- 来源可追溯
- 验证等级显式
- 禁止静默升级
- 为 W44+ 工程模型扩展
  提供登记入口


## 2. 数据结构


### EngineeringReference

字段：

- reference_id：唯一标识
- name：名称
- source_type：来源类型
- verification_level：验证等级
- description：说明
- created_time：登记时间

source_type：

- SYNTHETIC_MATH：数学合成定义
- ENGINEERING_REFERENCE：工程参考资料
- EXTERNAL_DATA：外部数据

verification_level：

- UNKNOWN：未验证
- MODEL_ONLY：仅模型内自洽
- DATA_SUPPORTED：有数据支持
- ENGINEERING_VERIFIED：工程验证


### EngineeringParameter

字段：

- name：参数名
- value：数值（必须有限）
- unit：单位
- source_reference：来源 reference_id
- verified：是否已核验

模型约束：

- pydantic 模型
- 不可变（frozen）
- JSON 可序列化


### EngineeringReferenceRegistry

功能：

- register：登记
- get：按 reference_id 查询
- list：列出全部

禁止：

- 自动提升 verification_level
- 重复登记覆盖


## 3. 与 W41/W42 关系

W41：统一设计评价器。
当前 domain = SYNTHETIC_MATH。

W42：优化实验合同、
Random Search、排名、
实验历史。
全部候选与实验
均为 SYNTHETIC_MATH。

W43-D2 本层：

不修改 W39/W40 求解器。
不修改 W41 评价器。
不修改 W42 优化流水线。

本层只提供
证据登记与隔离。

已有 SYNTHETIC_MATH 定义
未来可登记为：

- source_type = SYNTHETIC_MATH
- verification_level = MODEL_ONLY

工程资料接入后
登记为：

- source_type = ENGINEERING_REFERENCE
- verification_level = DATA_SUPPORTED
  或 ENGINEERING_VERIFIED

二者在数据结构层面隔离，
优化定义只能引用
已登记来源。


## 4. 当前限制

- 无 ENGINEERING_REFERENCE 实例
- 无 EXTERNAL_DATA 实例
- 参数与来源的跨对象一致性
  未强制校验
  （verified 标记
  不代表来源等级）
- 登记为内存结构，
  无持久化
- verification_level 升级
  需要人工流程，
  系统不提供任何
  升级方法
- EngineeringParameter
  尚未接入优化定义


## 5. 未来专业软件接入位置

接入点：

EngineeringReferenceRegistry.register

接入流程：

1. 专业软件输出
   转为 EngineeringParameter
2. 绑定 source_reference
3. 登记来源 EngineeringReference
4. source_type = EXTERNAL_DATA
5. verification_level =
   DATA_SUPPORTED
   或 ENGINEERING_VERIFIED
6. 人工确认后
   进入优化定义

禁止：

- 自动提升验证等级
- 无来源参数
- 虚构工程参数
