# W39-D3 Deterministic Numerical Four-Bar Closure Contract

## 1. Objective

W39-D3 implements the first deterministic numerical four-bar closure layer.

The target service module is:

app/services/linkage_closure.py

W39-D3 answers:

What mathematical closure solutions exist for one explicit solver input?

W39-D3 does not answer:

Which non-degenerate solution is the hydraulic-support engineering branch?

Reference-branch engineering selection remains outside D3.

## 2. Frozen public service boundary

W39-D3 shall provide:

calculate_rear_link_shield(
    task: ClosureSolverInput
) -> EngineeringPoint2D

and:

solve_closure_candidates(
    task: ClosureSolverInput
) -> ClosureResult

The service shall consume the W39-D2 strongly typed models.

It shall not return an unstructured solver dictionary.


## 3. Canonical geometry

W39-D3 retains the frozen topology:

A = rear_link_base

B = rear_link_shield

C = front_link_shield

D = front_link_base

Rigid-link lengths are:

AB = rear_link_length_mm

BC = shield_beam_effective_length_mm

CD = front_link_length_mm

DA = base_pivot_spacing_mm

The closed chain remains:

A -> B -> C -> D -> A

No top-beam geometry participates in D3 closure solving.

## 4. Deterministic point B

Given:

A = (Ax, Ay)

AB = rear_link_length_mm

theta = rear_link_angle_deg

D3 shall calculate:

Bx = Ax + AB * cos(theta)

By = Ay + AB * sin(theta)

theta shall be converted explicitly from degree to radian for numerical
trigonometric evaluation.

No presentation rounding shall occur inside the numerical service.

The resulting B coordinate shall use:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []


## 5. Effective distance tolerance

W39-D3 shall convert NumericalTolerance into a scale-aware distance tolerance.

For distance quantities:

effective_tolerance_mm = max(
    absolute_mm,
    relative * scale_mm
)

scale_mm shall be derived from the distance magnitudes involved in the current
comparison.

The effective tolerance therefore has unit mm.

The service shall not compare a raw squared-distance quantity directly against
a tolerance expressed in mm.

NumericalTolerance remains computational infrastructure.

It is not a hydraulic-support engineering parameter.

## 6. Fixed-base consistency validation

Before circle closure is solved, D3 shall compare:

geometric_AD = distance(A, D)

with:

base_pivot_spacing_mm

using the effective distance tolerance.

If:

abs(geometric_AD - base_pivot_spacing_mm) > effective_tolerance_mm

the solver input is inconsistent.

This is an input-consistency failure.

It is not:

NO_SOLUTION

because NO_SOLUTION describes a valid geometric input whose moving links cannot
close at the requested pose.

D3 shall fail explicitly.

D3 shall not:

- move D
- rewrite base_pivot_spacing_mm
- average the two values
- silently accept a mismatch outside tolerance


## 7. Circle closure quantities

After B is calculated:

q = distance(B, D)

r1 = BC

r2 = CD

The circle-state tolerance shall be based on distance-scale quantities
including:

q

r1

r2

r1 + r2

abs(r1 - r2)

using the frozen effective-distance-tolerance policy.

## 8. Coincident centers

If:

q <= effective_tolerance_mm

the circle centers are numerically coincident.

If the centers are coincident and:

abs(r1 - r2) <= effective_tolerance_mm

the closure state is:

DEGENERATE

because infinitely many mathematical C points exist.

If the centers are coincident and the radii differ beyond tolerance, the
closure state is:

NO_SOLUTION

No candidate C point shall be invented in either case.


## 9. Separated and contained circles

For non-coincident centers:

outer_gap = q - (r1 + r2)

inner_gap = abs(r1 - r2) - q

If:

outer_gap > effective_tolerance_mm

the closure state is:

NO_SOLUTION

If:

inner_gap > effective_tolerance_mm

the closure state is:

NO_SOLUTION

These represent separated and contained non-intersecting circles,
respectively.

## 10. Tangency

For non-coincident centers, D3 shall classify TANGENT when either:

abs(q - (r1 + r2)) <= effective_tolerance_mm

or:

abs(q - abs(r1 - r2)) <= effective_tolerance_mm

after the NO_SOLUTION conditions have been evaluated.

Both external and internal tangency are included.

A tangent closure produces exactly one C candidate.

Its branch is:

TANGENT


## 11. Two-solution state

If the circles are:

- not coincident
- not separated
- not contained without intersection
- not tangent within tolerance

then the closure state is:

TWO_SOLUTIONS

Exactly two finite C candidates shall be generated.

Their branch set shall be exactly:

POSITIVE

NEGATIVE

D3 shall not select one of them as the engineering pose.


## 12. Circle-intersection construction

For a non-coincident intersection problem:

dx = Dx - Bx

dy = Dy - By

q = hypot(dx, dy)

a = (
    r1^2
    - r2^2
    + q^2
) / (2*q)

The base point P is:

Px = Bx + a * dx / q

Py = By + a * dy / q

For TWO_SOLUTIONS:

h^2 = r1^2 - a^2

h must be real and strictly positive for a valid two-solution construction.

The positive perpendicular direction relative to B -> D is:

(-dy / q, dx / q)

Therefore:

C_positive = (
    Px - h * dy / q,
    Py + h * dx / q
)

C_negative = (
    Px + h * dy / q,
    Py - h * dx / q
)

For TANGENT:

h = 0

and:

C = P

The service shall not use candidate list position as engineering branch
selection.


## 13. Candidate branch sign

Candidate branch sign is defined relative to directed line:

B -> D

For candidate C:

cross = (
    (Dx - Bx) * (Cy - By)
    - (Dy - By) * (Cx - Bx)
)

The signed perpendicular distance is:

signed_distance_mm = cross / distance(B, D)

This quantity has unit mm.

For TWO_SOLUTIONS:

signed_distance_mm > 0

means:

POSITIVE

and:

signed_distance_mm < 0

means:

NEGATIVE

The branch classifier shall use distance-scale tolerance rather than comparing
the raw mm^2 cross product directly against an mm tolerance.

A candidate numerically indistinguishable from the B-D line shall not be
silently presented as a valid POSITIVE or NEGATIVE two-solution branch.

For TANGENT the branch is explicitly:

TANGENT


## 14. Deterministic candidate ordering

For TWO_SOLUTIONS, D3 shall serialize candidates in deterministic order:

1. POSITIVE
2. NEGATIVE

This ordering exists only for reproducibility and stable testing.

It does not mean that POSITIVE is preferred.

It does not mean that the first candidate is the engineering solution.

D4 branch resolution shall use branch semantics, not list position.


## 15. TWO_SOLUTIONS result boundary

For TWO_SOLUTIONS, W39-D3 shall return:

selection_status = BRANCH_AMBIGUOUS

selected_pose = null

branch_resolution = NONE

This remains true even if:

ClosureSolverInput.reference_branch

is non-null.

D3 shall not consume reference_branch to select a candidate.

That behavior belongs to D4.

## 16. TANGENT result boundary

TANGENT has only one mathematical C point.

Therefore D3 may return:

selection_status = SELECTED

selected_pose = non-null

branch_resolution = TANGENT_UNIQUE

This is mathematical uniqueness.

It is not reference-branch engineering selection.

The selected pose shall reuse the exact solved B and sole candidate C data.


## 17. NO_SOLUTION and DEGENERATE result boundary

For NO_SOLUTION:

candidates = []

selection_status = NOT_APPLICABLE

selected_pose = null

branch_resolution = NONE

For DEGENERATE:

candidates = []

selection_status = NOT_APPLICABLE

selected_pose = null

branch_resolution = NONE

The D2 ClosureResult invariants remain authoritative.

## 18. Provenance

Every B or C coordinate calculated by D3 shall use:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

source_text shall identify the W39-D3 deterministic closure calculation.

D3 introduces no new Formula Registry ID.

D3 creates no Calculation Record.

The solver shall not change the provenance of input geometry.


## 19. Synthetic benchmark requirement

The W39-D1 SYNTHETIC_MATH benchmark registry shall be used to verify D3.

The solver shall correctly classify:

SM-001 = TWO_SOLUTIONS

SM-002 = TANGENT

SM-003 = NO_SOLUTION

SM-004 = NO_SOLUTION

SM-005 = DEGENERATE

SM-006 = NO_SOLUTION

Synthetic benchmark geometry validates deterministic mathematics and software
behavior only.

It does not constitute hydraulic-support engineering validation.

## 20. Engineering-reference boundary

ER-001 remains:

ENGINEERING_REFERENCE
NOT_SOLVER_READY

W39-D3 shall not fill the missing engineering geometry.

No real-support validation claim may be made from the synthetic benchmark
suite.

## 21. Explicitly outside W39-D3

W39-D3 does not implement:

- reference-branch engineering selection
- OPEN/CROSSED terminology
- previous-pose continuity
- support-height-to-pose mapping
- operating-height sweep
- top-beam pose
- beam-tip trajectory
- 80 mm beam-tip validation
- interference checking
- linkage optimization
- GA
- PSO
- NSGA-II

## 22. D4 entry condition

After D3 deterministic mathematical closure is independently tested, W39-D4
may implement reference-branch resolution.

D4 shall consume D3 TWO_SOLUTIONS candidates and select by explicit branch
semantics.

D4 shall not recalculate circle intersection merely to choose a branch.

D4 shall not select by candidate list position.
