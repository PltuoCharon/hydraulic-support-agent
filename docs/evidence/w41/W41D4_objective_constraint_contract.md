# W41-D4 Objective and Constraint Contract V1

Baseline: b38a40c1b6eb1eda45bae76dc5f71401d2b03371.
Domain: synthetic mathematical candidate evaluation. W41 supplies the common
evaluator; mature search algorithms belong to W42. This supersedes the phase
allocation wording in W40D6 closeout, without changing that historical file.

## Feasibility modes

`SINGLE_POSE_SELECTED` calls W39 at the candidate configuration angle.
TANGENT with its unique selected pose and TWO_SOLUTIONS with its explicitly
selected branch are FEASIBLE. NO_SOLUTION and DEGENERATE are INFEASIBLE but
remain distinct in the embedded result. An unresolved double solution is
BRANCH_UNRESOLVED. Never guess a branch.

`FULL_SAMPLED_REGULAR_MOTION` requires at least two explicit finite degree
samples, strictly monotonic in declared INCREASING/DECREASING direction, with
the first value exactly equal to the candidate reference angle and a non-null
W39 reference branch. All angle parameters require source_text. FEASIBLE means
W40 returned COMPLETED: every requested sample has a selected non-singular
double solution on the configured branch.

W39 preflight preserves the actual first closure result. If that first pose is
not a selected double solution, the evaluator does not call W40, reports failure
at index 0 and leaves motion_result null. No W40 segment is fabricated.

Once entered, W40 preserves its first terminal TANGENT, NO_SOLUTION or
DEGENERATE sample and requested count. Each terminal state is INFEASIBLE for
this regular full-sampling mode. Even a tangent at the final requested angle
fails; processing every requested angle alone is not sufficient.
The evaluator does not skip samples, resume, interpolate, cross tangencies or
infer the unsampled continuous interval.

## Objective

The request explicitly supplies `objective=None` for no objective.
objective_status=OBJECTIVE_NOT_CONFIGURED, objective_value=null; mathematical
feasibility is still evaluated. No default fitness or residual objective exists.

The only optional objective is SAMPLED_C_X_RANGE, direction MINIMIZE, unit mm:

f = max(C_i.x_mm.value) - min(C_i.x_mm.value)

It is compatible only with FULL_SAMPLED_REGULAR_MOTION. It is computed from all
requested, uniquely selected C points only when motion termination is COMPLETED.
Otherwise objective_status=NOT_EVALUABLE, objective_value=null, metrics=[].
Successful computation produces one metric named SAMPLED_C_X_RANGE, unit mm,
scope FULL_REQUESTED_ANGLE_SAMPLES. No prefix substitute, weights, penalties,
normalization or objective priorities are introduced.

Hand-check fixture: A=(0,0), D=(3,0), AB=1, BC=CD=3 mm; angles [0,90] degree;
POSITIVE synthetic branch rule. Cx(0)=2, Cx(90)=1.5+sqrt(0.65).
f=sqrt(0.65)-0.5=approximately 0.306225774829855 mm. This is artificial geometry.

The C point is a four-bar moving pivot, not the top-beam tip T. This objective
is not support-height error, engineering stability, mass, stress or compliance.

## Categories and state rules

- Invalid candidate, units, origins, bounds, AD consistency, mismatched outer
  case or invalid plan: validation exception; never NO_SOLUTION.
- ENGINEERING_REFERENCE and other unready records: no execution, no result or
  calculated metric. ER-001 remains NOT_SOLVER_READY. No geometry is required
  for an unready record, and no missing geometry is filled.
- Mathematical closure infeasibility/degeneracy: structured constraint failure
  preserving actual W39/W40 states.
- Unresolved branch in single-pose mode: distinct BRANCH_UNRESOLVED.
- Numerical or service exceptions: propagate; no fabricated closure or penalty.

Exactly one constraint outcome is returned: SELECTED_POSE or
FULL_REGULAR_SAMPLES, with PASS/FAIL/NOT_EVALUATED, reason and applicable failure
sample index. Index is null on success or unexecuted requests, 0 on failed
sweep preflight, or the actual terminal index for a returned failed motion.

FEASIBLE denotes this configured mathematical constraint only. It is never
ENGINEERING_VERIFIED. Existing W39 REFERENCE_POSE provenance labels do not
independently authenticate a synthetic branch rule.

## Numerical and engineering limitations

Preserve D3 lengths, bounds, coordinate-derived AD, type/coercion rules, domain
gates, arithmetic-capacity guard and explicit NumericalTolerance. Preserve W39
scale-dependent distance comparisons and all W40 stopping behavior. Do not add
angle tolerances, arbitrary near-zero thresholds or inter-sample jump tests.
The historical near-zero contract/code difference remains unresolved; very
small scales and conditioning are not universally validated.

No engineering READY promotion exists. Parameter source_text is a declaration,
not external source verification. Domain labels cannot turn ER-* into SM-*.
No E/T substitution, height mapping, T trajectory, 80 mm compliance, interference,
load, mass, optimization search or physical engineering bounds are implemented.
