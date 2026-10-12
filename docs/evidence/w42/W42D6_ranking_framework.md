# W42-D6 Pareto Ranking Framework

## 目标

建立优化候选排序基础。

不实现：
- GA
- PSO
- NSGA-II


## 输入

来自：

W42-D4 Optimization Pipeline

以及：

W42-D5 Objective Framework


## 支配定义

当前统一：

所有目标默认 MINIMIZE。


A 支配 B：

- A所有目标 <= B
- 至少一个目标 < B


## 失败处理

不可行候选：

- 不进入正常Pareto竞争
- 保留失败证据


## 当前限制

未包含：

- 权重
- 工程约束
- 多层目标优先级
- 优化算法

本阶段仅建立排序能力。
