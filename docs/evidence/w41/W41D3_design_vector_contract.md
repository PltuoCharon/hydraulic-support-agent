# W41-D3 Four-Bar Candidate Design Contract V1

Baseline: 999d7b48962f361b67520627bdfdc04a98113cde.

## Representation and interface

W41 candidates use `FourBarDesignVector` with fixed exported order:
`[rear_link_length_mm, shield_beam_effective_length_mm, front_link_length_mm]`
(AB, BC, CD). `as_vector()` returns a tuple of values in this order.
These are independent candidate inputs subject to closure constraints, not
independently guaranteed feasible mechanisms.

W38 remains coordinate-first. Its reference B/C coordinates determine its
lengths. Do not overwrite W38 `derived_geometry` to pass candidate dimensions:
W39-D5 freshly derives baseline lengths and checks reference-pose round trips.
Candidate adaptation is a separate entrypoint:
`build_closure_task_from_design(candidate: CandidateDesignInput) -> ClosureSolverInput`.
It never calls or duplicates the closure algorithm. Call existing W39
`solve_closure(task)` separately. W40 can consume this task as its reference
configuration subject to its existing selected-double-solution entry rules.

## Models and validation

- `LengthBounds`: positive finite mm lower/upper parameters, lower < upper.
- `DesignVariableBounds`: named intervals plus explicit domain.
- `DesignCase`: domain, case_id, readiness, source_text; engineering_verified
  is always literal false in this V1.
- `FixedEvaluationConfig`: normalized A, explicit D x/y, explicit degree angle,
  explicit nullable W39 branch, tolerance, optional declared AD, branch source.
- `CandidateDesignInput`: case, design, bounds, configuration; checks matching
  domains and inclusive bounds before adaptation.

Reuse existing StrictModel, MillimetreParameter, DegreeParameter,
EngineeringPoint2D, NumericalTolerance and provenance fields. Raw numeric
inputs accept Python int/float only; reject booleans, strings, null, NaN and
infinities. Units must be explicit in payloads. Missing/extra fields fail.
Parameters require valid existing origin/evidence enums and nonblank
source_text. Declared provenance is preserved but is not independent evidence
verification. Existing typed objects are inspected too; information already
lost through an earlier coercing model cannot be recovered.

Use `model_validate_json()` or `from_json()` for JSON: duplicate keys at any
nesting depth fail. Python mappings inherently cannot retain duplicate keys;
callers must not preparse JSON with a duplicate-discarding parser.

## Fixed geometry and numerical policy

A is (0,0); D is explicitly provided and may have nonzero y. AD is hypot(Dx,Dy),
finite and positive. Optional external AD is checked against coordinates using
existing W39 `max(absolute_mm, relative * comparison_scale)` tolerance. The task
always receives the coordinate-derived AD, CALCULATED/PARTIAL with no invented
Formula/Calculation IDs. Angle, branch and tolerance are configuration, not
optimization variables. Non-null branches require a source/rule description.
W38 SAME_SIDE/OPPOSITE_SIDE are not W39 POSITIVE/NEGATIVE.

Near-zero policy: accept finite lengths > 0 within explicit bounds, matching
current W39-D2 code. W39-D1 contract calls for lengths beyond tolerance; that
historical discrepancy remains unresolved. V1 introduces no arbitrary minimum,
no automatic clamp, no engineering tolerance and no solver changes.

Adapter rejects scales for which `(4 * max(AD, AB, BC, CD)) ** 2` would be
nonfinite in float arithmetic, using ArithmeticError. This conservative
arithmetic-capacity guard prevents overflow in the unmodified W39 calculations;
it is not an engineering upper bound. Other solver numerical exceptions remain
exceptions and must never be converted to NO_SOLUTION.

Adapter revalidates serialized input, creates independent task data, and does
not mutate source candidate objects. It does not use reference-pose coordinates
or change W38/W39/W40 services.

## Domains and status boundaries

SYNTHETIC_MATH READY cases alone may adapt. SM-001 through SM-006 remain
artificial mathematical fixtures with engineering_verified=false. Bounds in
tests are explicitly synthetic fixtures, not inferred engineering limits.

ENGINEERING_REFERENCE records remain NOT_SOLVER_READY in V1, including ER-001.
READY declarations and engineering_verified=true are rejected, even if a caller
supplies complete-looking numbers. ER-* cannot be relabelled as synthetic;
SM-* cannot be relabelled as engineering. Domain-mismatched bounds fail.
The standalone case record requires no dimensions or bounds: missing ER-001
geometry is not filled automatically. No independent engineering evidence
review/promotion service exists in this scope.

Input validity is separate from closure feasibility and engineering readiness:
- Invalid values/configuration/bounds: validation exception, no fabricated result.
- Unready case: adapter rejection, no solver task/result.
- Valid task at requested angle: preserve existing W39 NO_SOLUTION, TANGENT,
  TWO_SOLUTIONS or DEGENERATE and selection/provenance semantics.
- Double solution without branch stays BRANCH_AMBIGUOUS; no branch guessing.
- Numerical failure remains an exception, separate from moving-link infeasibility.

A closure result is specific to its requested angle. It proves neither complete
motion-range feasibility nor engineering compliance. Synthetic branch selection
is a test rule; W39's existing REFERENCE_POSE label does not authenticate a real
engineering reference. Preserve the W41 wrapper for domain/branch-source audit:
ClosureSolverInput itself has no domain field.

## Remaining scope and evidence limits

No objectives, GA/PSO, support-height mapping, top-beam T trajectory, interference
analysis or 80 mm engineering compliance decision. Engineering dimensions,
bounds, manufacturing constraints and verified branch rules remain unavailable.
Source text authenticity requires independent review. Discrete W40 samples do
not establish unsampled continuous feasibility. Tiny-scale underflow and other
numerical conditioning remain subject to existing solver semantics/exceptions.

## Validation results

Final runs using the existing venv; no dependencies installed or upgraded:

- `venv/bin/python -m pytest -q tests/test_w41d3_design_vector_model.py tests/test_w41d3_design_adapter.py`:
  78 passed, 0 failed, no warnings, 0.14s.
- `venv/bin/python -m pytest -q`:
  1159 passed, 0 failed, 1 warning, 14.31s, exit code 0.
- Historical baseline: 1081 passed, 1 warning; increase = 78 new cases.
- Warning unchanged: StarletteDeprecationWarning concerning httpx in
  fastapi/testclient.py. Dependencies were not modified.

First targeted run found an overflow fixture returning a result instead of an
exception (74 passed, 1 failed). The adapter arithmetic-capacity guard was added,
and final targeted/full results above include the corrected implementation.
Original W41D3_source_audit.txt retained unchanged; SHA-256:
cb0decc8e72787ea55aa0acbe750221b1fe8864769eb7f31e8cebdfb0dfa5f2e.
No W38/W39/W40 algorithms or historical tests were edited. No commit or push.
