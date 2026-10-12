# W42-D5 Objective Constraint Framework


## Purpose

建立优化目标与约束表达层。


本阶段不是工程优化。


## Objective

当前支持：

CX_RANGE_MM


来源：

W41 evaluator


单位：

mm



## Constraint

状态：

PASS

FAIL

UNKNOWN


UNKNOWN:

表示无法计算违反程度。


禁止：

未知状态转换为通过。


## Architecture


W41 Evaluator

↓

Optimization Pipeline

↓

Objective Constraint Framework

↓

Future GA / PSO



## Limitations

当前：

- 单目标
- 无Pareto
- 无权重优化
- 无GA
- 无PSO
- 无工程约束
