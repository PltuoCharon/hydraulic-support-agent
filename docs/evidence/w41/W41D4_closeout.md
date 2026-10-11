# W41-D4 Closeout

## 1. Task Identity

Project: Hydraulic Support Intelligent Auxiliary Design
Phase: V3.0 W41-D4
Baseline: b38a40c1b6eb1eda45bae76dc5f71401d2b03371

Task: Unified Mathematical Design Evaluator V1

## 2. Implemented Capability

The evaluator reuses:

- W41-D3 CandidateDesignInput and adapter
- W39 deterministic solve_closure()
- W40 sweep_rear_link_angles()

Evaluation modes:

- SINGLE_POSE_SELECTED
- FULL_SAMPLED_REGULAR_MOTION

No historical kinematic solver was modified.

## 3. Objective Contract

The request requires an explicit objective field.

When objective=None:

- objective_status=OBJECTIVE_NOT_CONFIGURED
- objective_value=null
- mathematical feasibility is still evaluated

Optional synthetic mathematical objective:

SAMPLED_C_X_RANGE

Definition:
max(C_i.x) - min(C_i.x)

Direction: MINIMIZE
Unit: mm

The objective is computed only after the complete
requested regular motion sample sequence succeeds.

No partial-prefix objective is allowed.

## 4. Feasibility and Execution Semantics

Evaluation distinguishes:

- NOT_EVALUATED
- FEASIBLE
- INFEASIBLE
- BRANCH_UNRESOLVED

Execution status is independent of feasibility.

Original W39/W40 closure and motion states are preserved.

Numerical and service exceptions propagate.

No fabricated penalty, closure result, motion segment
or engineering verification status is generated.

## 5. Engineering Boundary

SYNTHETIC_MATH supports mathematical testing only.

ER-001 remains:

ENGINEERING_REFERENCE / NOT_SOLVER_READY

Unready engineering cases do not invoke W39/W40.

Not implemented:

- Engineering optimization bounds
- Support-height mapping
- Candidate E-point attachment geometry
- Independently constrained top-beam pose
- Physical T-point trajectory
- 80 mm beam-tip compliance verification
- GA, PSO or NSGA-II

## 6. Implemented Files

- app/models/linkage_evaluation.py
- app/services/linkage_evaluation.py
- tests/test_w41d4_evaluation_models.py
- tests/test_w41d4_evaluation_service.py
- docs/evidence/w41/W41D4_objective_constraint_contract.md
- docs/evidence/w41/W41D4_evaluator_contract.md

## 7. Independent Verification

Targeted tests:
74 passed, exit code 0, 0.16s.

Full regression:
1233 passed, 1 warning, 13.46s, exit code 0.

Historical W41-D3 baseline:
1159 passed, 1 warning.

Net new tests: 74.

The warning remains StarletteDeprecationWarning.

Dependency verification:
pip check PASS, exit code 0.

## 8. Remaining Risks

- Historical near-zero length contract discrepancy
- Extreme-scale numerical conditioning
- Synthetic provenance is not independent engineering evidence
- Discrete sampling does not prove continuous feasibility
- Engineering geometry and operating-height mapping remain incomplete
- Successful W40 sweep performs a repeated first-angle W39 solve

## 9. Acceptance Decision

Status: PASS_SOFTWARE_CONTRACT

The evaluator implementation, objective contract,
feasibility classification and regression tests pass.

Status does not imply engineering verification.

## 10. Next Phase

Continue the W41 closeout and evaluator integration
according to the approved V3.0 roadmap.

W42 may use this shared evaluator as a foundation
for mature optimization algorithm baselines.

Engineering objectives remain blocked until the
required geometry and evidence are available.
