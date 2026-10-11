# W41-D4 Unified Evaluator Contract V1

Baseline: b38a40c1b6eb1eda45bae76dc5f71401d2b03371.

## Public interface

`evaluate_design(request: DesignEvaluationRequest) -> DesignEvaluationResult`

Modules: app/models/linkage_evaluation.py and app/services/linkage_evaluation.py.
Reuse W41-D3 CandidateContract, CandidateDesignInput and DesignCase;
W39 ClosureResult; W40 MotionSweepInput and MotionSegmentResult.
No previous models, algorithms or frozen contracts are modified.

Request fields:
- case: existing DesignCase.
- candidate: CandidateDesignInput or null.
- plan: discriminated SinglePosePlan/AngleSweepPlan or null.
- objective: explicit ObjectiveSpec or null (field required).

Ready synthetic cases require candidate and plan. Supplied candidate.case must
exactly equal outer case, including provenance. Angle plans require an explicit
branch and matching first angle. Plans require nonblank source_text. ObjectiveSpec
allows only SAMPLED_C_X_RANGE/MINIMIZE/mm and requires an angle plan.
Unready cases may omit candidate and plan. Engineering pseudo-READY, claimed
verification, ER relabelling and mismatched case/domain fail existing validation.
Raw payloads retain D3 explicit units and numeric coercion protections; JSON
entrypoints reject duplicate keys. Earlier coercion performed by a caller before
providing an existing typed object cannot be reconstructed.

## Call chain and independence

1. Revalidate a serialized request snapshot, protecting against mutable models
   and model_construct/update bypasses without mutating input.
2. Gate any engineering/unready case before adaptation or solving.
3. Call existing build_closure_task_from_design(candidate).
4. Call existing W39 solve_closure(task).
5. For an eligible angle plan, call existing W40 sweep_rear_link_angles with
   that task and the explicit plan; otherwise leave motion_result null.
6. Derive hard-constraint outcome and optional objective from actual outputs.

Successful sweep calls W39 once for preflight and W40 once; W40 itself calls
W39 once per processed sample. Thus the first angle is solved twice. This is an
explicit compatibility tradeoff, not a copied loop or a changed solver API.
No exception-catching layer is introduced. Original validation, numerical and
service exceptions propagate, including exceptions during an entered sweep.
W40 does not expose a partial segment on exception; the evaluator fabricates
neither a segment nor a prefix. Batch exception packaging is future work.

## Return fields and invariants

- request: independent validated snapshot containing domain, case_id, candidate
  values, bounds, fixed geometry, branch source, tolerance and complete plan.
- execution_status: NOT_RUN or COMPLETED. COMPLETED means evaluation returned,
  not that all requested motion samples succeeded.
- case_readiness: READY or NOT_SOLVER_READY, equal to request.case.readiness.
- feasibility_status: NOT_EVALUATED, FEASIBLE, INFEASIBLE or BRANCH_UNRESOLVED.
- objective_status: OBJECTIVE_NOT_CONFIGURED, COMPUTED or NOT_EVALUABLE.
- constraints: exactly one ConstraintOutcome for the selected mode.
- closure_result: actual single-pose result or first-pose preflight result.
- motion_result: original typed W40 result, or null if W40 was not entered.
- objective_value: finite computed range, or null.
- metrics: exactly one named/unit/scoped metric for a computed objective,
  otherwise empty; unavailable values are not represented as zero.

Model validators enforce these relationships:
- Unready means NOT_RUN/NOT_EVALUATED, no closure/motion/metric/value and a
  NOT_EVALUATED constraint. A supplied objective is NOT_EVALUABLE.
- Ready evaluations require actual closure data and COMPLETED execution.
- Selected closure angle/branch agree with configuration.
- Returned motion agrees with preflight, requested count, direction, reference
  branch/angle and the processed prefix of the requested angle parameters.
- FEASIBLE/INFEASIBLE/BRANCH_UNRESOLVED agrees with embedded raw states and
  constraint PASS/FAIL; regular first pose cannot omit the sweep result.
- Constraint index identifies the actual failure boundary.
- COMPUTED requires full successful motion, matching metric and exact range
  from all returned C samples; uncomputed values remain null.

Snapshots and dedicated W39/W40 outputs retain provenance. No engineering
verification or invented Formula/Calculation IDs are introduced. See
W41D4_objective_constraint_contract.md for the mathematics and exclusions.

## Verification

Final verification using existing venv:

- `venv/bin/python -m pytest -q tests/test_w41d4_evaluation_models.py tests/test_w41d4_evaluation_service.py`:
  74 passed, 0 failed, no warnings, 0.19s, exit code 0.
- `venv/bin/python -m pytest -q`: 1233 passed, 0 failed, 1 warning,
  14.52s, exit code 0. Baseline 1159 + 74 new cases = 1233.
- `venv/bin/python -m pip check`: No broken requirements found, exit code 0.
- Existing warning: StarletteDeprecationWarning regarding httpx in
  fastapi/testclient.py. No dependencies installed or upgraded.

First targeted run: 56 passed, 12 failed due to missing explicit metric unit
in the new service. Fixed the service to supply mm, then 68 passed. After
additional actual arithmetic-capacity, decreasing-sweep and state-index tests,
the final targeted run above passed 74 cases.

Tests include SM-001 through SM-006, real W40 completed/tangent/no-solution/
degenerate results, failed first-pose gate without W40 calls, unready ER-001
without any adapter/solver calls, hand-calculated objective, exception identity,
actual D3 capacity rejection, snapshot independence and serialization roundtrip.
Historical tests, W38/W39/W40 algorithms and W41-D3 contracts are unchanged.
HEAD remains b38a40c1b6eb1eda45bae76dc5f71401d2b03371. No commit or push.
