# W37-D1 Overall Design System Audit

## 1. Purpose

W37 在组会后重新定义为“总体设计数据契约与项目路线迁移”。

D1 只审计当前系统能力及未来 OverallSupportDesign 的接口边界。
本阶段不新增工程算法、不修改数据库、不新增 Formula ID、不实现四连杆或 Valve。

## 2. Frozen baseline

W36.5 已完成并冻结。

当前主线已有：
- 支架型号与工况数据库
- 智能选型
- q_need 计算
- 立柱参数设计
- 立柱强度/稳定性校核
- HydraulicCylinder 基础原语
- 推移千斤顶参数设计
- Formula Registry
- Calculation Record

## 3. Capability matrix

| Capability | Current state | W37-D1 status |
|---|---|---|
| Working-condition data | DB/API available | COMPLETE |
| Historical support data | DB/API/selection available | COMPLETE |
| Intelligent support selection | Product runtime available | COMPLETE |
| p1/p2/p3 -> q_need | Core/API/UI available | COMPLETE |
| q_need -> required working resistance | Core/formulas/tests only | PARTIAL |
| Column parameter design | Core/API/UI/record | COMPLETE |
| Column strength/stability | Core/API/UI | PARTIAL |
| Push-jack parameter design | Core/API/UI/E2E | PARTIAL |
| Jack Formula IDs | None | INTENTIONALLY_DEFERRED |
| Jack Calculation Record | None | INTENTIONALLY_DEFERRED |
| Valve design | Placeholder only | NOT_IMPLEMENTED |
| Pipeline design | None | NOT_IMPLEMENTED |
| Pump-station design | None | NOT_IMPLEMENTED |
| Linkage/kinematics | None | NOT_IMPLEMENTED |
| Structural parameter model | None | NOT_IMPLEMENTED |
| FEA | None | NOT_IMPLEMENTED |
| Topology optimization | None | NOT_IMPLEMENTED |
| AI generative structural optimization | None | NOT_IMPLEMENTED |

## 4. q_need and resistance boundary

The active q_need path calculates p1, p2 and p3 and selects:

q_need = max(p1, p2, p3)

q_need is the project controlling required support intensity.
It shall not automatically be equated with a standard Ps definition.

F-QN-005 to F-QN-007 implement:

A_control = Sc * Bc

F_base = q_need * A_control * 1000

F_rated = F_base / Ks

Current runtime status is PARTIAL because this resistance chain has a pure
calculation core and tests but is not wired into the current router/UI path.

Bc must be explicit and verified.
Historical canopy_len shall not be silently mapped to Bc.
canopy_len keeps the current canonical meaning: 支护长度参数.

Ks is support efficiency and is not historical column eta.

## 5. Column boundary

Active column design returns:
- d_calc_mm
- d_std_mm
- p_actual_kn
- optional setting_ratio_pct
- optional setting_ok

p_actual_kn is the calculated support capacity after standard-bore selection
using column count and historical eta.

Historical eta remains an explicit input with an unresolved physical definition.
It shall not be renamed hydraulic efficiency or mechanical efficiency.

## 6. Push-jack boundary

Push-jack design already provides:
- push_required_kn
- pressure_mpa
- bore_calc_mm
- bore_candidate_mm
- push_actual_kn
- push_ok
- optional rod/pull/stroke fields

Current limitations:
- no F-JACK Formula ID
- no Calculation Record
- MT/T 94 candidate-bore compliance not independently verified
- no automatic rod diameter
- no automatic stroke
- no default pressure

## 7. Design context boundary

hs.designTransfer.v1 is a lightweight page-to-page design context.

Its current source types are:
- selected_support
- calculated_requirement

The audit found calculated_requirement is accepted/consumed but no active
producer path was found in web/src.

hs.designTransfer.v1 shall remain backward compatible.

A future hs.overallDesign.v1 will represent the complete engineering design
project. It shall be defined in W37-D2 rather than extending designTransfer
into a large lifecycle object.

## 8. OverallSupportDesign boundary

OverallSupportDesign will represent one engineering design project.

It is not:
- a support_models database row
- a Calculation Record
- an AI free-form answer

Future parameter origins shall distinguish at least:
- RETRIEVED
- CALCULATED
- USER_INPUT
- AI_PROPOSED

Engineering/evidence status shall remain independent from parameter origin.

## 9. Calculation Record boundary

Calculation Record records individual deterministic engineering calculations.

Current production scope remains column_design only.

Future OverallSupportDesign may reference multiple calculation records,
but shall not replace them.

## 10. Next step

W37-D2 will freeze OverallSupportDesign v1 data contract.

No production implementation is authorized by this D1 document.
