# W39-D3 Deterministic Numerical Four-Bar Closure Closeout

## 1. Scope

W39-D3 implements the first executable deterministic numerical four-bar
closure layer.

The implementation is:

app/services/linkage_closure.py

W39-D3 now supports:

- deterministic point-B calculation
- fixed-base A-D / DA consistency validation
- scale-aware numerical tolerance
- two-circle closure classification
- NO_SOLUTION
- TANGENT
- TWO_SOLUTIONS
- DEGENERATE
- deterministic C candidate coordinates
- POSITIVE / NEGATIVE / TANGENT branch classification
- deterministic candidate ordering
- W39-D2 typed ClosureResult output

W39-D3 does not perform engineering reference-branch selection.

## 2. Canonical mechanism

The canonical topology remains:

A = rear_link_base

B = rear_link_shield

C = front_link_shield

D = front_link_base

Rigid-link lengths remain:

AB = rear_link_length_mm

BC = shield_beam_effective_length_mm

CD = front_link_length_mm

DA = base_pivot_spacing_mm

The closed chain remains:

A -> B -> C -> D -> A

Top-beam geometry is outside W39-D3.

## 3. Deterministic point B

W39-D3 calculates B from:

A

AB

rear_link_angle_deg

using:

Bx = Ax + AB * cos(theta)

By = Ay + AB * sin(theta)

The degree input is explicitly converted to radians.

No presentation rounding is performed inside the numerical solver.

Calculated B coordinates use:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

## 4. Numerical tolerance

W39-D3 uses a scale-aware distance tolerance:

effective_tolerance_mm = max(
    absolute_mm,
    relative * scale_mm
)

The resulting tolerance has unit mm.

Raw squared-distance or cross-product quantities are not directly compared
against a tolerance expressed in mm.

NumericalTolerance remains computational infrastructure.

It is not a hydraulic-support engineering design parameter.

## 5. Fixed-base consistency

Before closure solving, W39-D3 compares:

distance(A, D)

with:

base_pivot_spacing_mm

using the effective distance tolerance.

A mismatch outside tolerance is treated as an explicit input-consistency
failure.

It is not returned as NO_SOLUTION.

NO_SOLUTION is reserved for a geometrically consistent mechanism whose moving
links cannot close at the requested rear-link angle.

The solver does not:

- move D
- rewrite base_pivot_spacing_mm
- average inconsistent values
- silently repair the input

## 6. Circle closure

After B is calculated:

q = distance(B, D)

r1 = BC

r2 = CD

W39-D3 deterministically classifies the two-circle relationship.

### NO_SOLUTION

NO_SOLUTION includes:

- separated circles
- contained non-intersecting circles
- coincident centers with unequal radii beyond tolerance

No C candidate is created.

### DEGENERATE

Numerically coincident centers with equal radii within tolerance produce:

DEGENERATE

This represents an infinite mathematical solution set.

No arbitrary finite C coordinate is created.

### TANGENT

Both external and internal tangency are supported.

TANGENT produces exactly one C candidate.

The candidate branch is:

TANGENT

Because the mathematical C point is unique, D3 returns:

selection_status = SELECTED

branch_resolution = TANGENT_UNIQUE

This is mathematical uniqueness.

It is not engineering reference-branch selection.

### TWO_SOLUTIONS

A proper two-circle intersection produces exactly two finite C candidates.

Their branch set is:

POSITIVE

NEGATIVE

W39-D3 does not choose one as the hydraulic-support engineering pose.

## 7. Circle-intersection construction

For a non-coincident intersection:

a = (
    r1^2
    - r2^2
    + q^2
) / (2*q)

The line-of-centers base point P is calculated first.

For TWO_SOLUTIONS:

h^2 = r1^2 - a^2

and the two C coordinates are generated using opposite perpendicular offsets
from the directed line B -> D.

For TANGENT:

h = 0

and the unique C point is P.

## 8. Candidate branch classification

Branch sign is defined relative to directed line:

B -> D

The raw 2D cross product has unit mm^2.

W39-D3 converts it to signed perpendicular distance:

signed_distance_mm = cross / distance(B, D)

The resulting branch metric has unit mm and can therefore be compared against
the distance-scale numerical tolerance.

For TWO_SOLUTIONS:

positive signed distance -> POSITIVE

negative signed distance -> NEGATIVE

For TANGENT:

branch = TANGENT

## 9. Deterministic candidate ordering

For reproducible serialization and testing, TWO_SOLUTIONS candidates are
returned in this order:

1. POSITIVE
2. NEGATIVE

This order is not an engineering preference.

Candidate index 0 is not automatically the physical hydraulic-support pose.

Future branch resolution must use branch semantics rather than list position.

## 10. Reference-branch boundary

ClosureSolverInput may contain:

reference_branch

but W39-D3 intentionally does not consume it for TWO_SOLUTIONS selection.

Even when reference_branch is POSITIVE or NEGATIVE, W39-D3 returns:

closure_state = TWO_SOLUTIONS

selection_status = BRANCH_AMBIGUOUS

selected_pose = null

branch_resolution = NONE

Reference-branch resolution belongs to W39-D4.

## 11. Provenance boundary

Every B or C coordinate generated by W39-D3 uses:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

source_text identifies the W39-D3 deterministic closure calculation.

W39-D3 introduces no Formula Registry ID.

W39-D3 creates no Calculation Record.

Input geometry provenance is not rewritten.

## 12. Determinism and immutability

For the same ClosureSolverInput, W39-D3 returns the same typed mathematical
result.

The service does not mutate the input object.

The solver creates new calculated result objects.

## 13. Synthetic benchmark status

The W39-D1 SYNTHETIC_MATH benchmark set is executable against the D3 solver.

The frozen results are:

SM-001 -> TWO_SOLUTIONS

SM-002 -> TANGENT

SM-003 -> NO_SOLUTION

SM-004 -> NO_SOLUTION

SM-005 -> DEGENERATE

SM-006 -> NO_SOLUTION

These cases validate mathematical implementation and software behavior.

They do not constitute hydraulic-support engineering validation.

## 14. Engineering-reference status

ER-001 remains:

ENGINEERING_REFERENCE

NOT_SOLVER_READY

No complete traceable real-support A/B/C/D geometry and reference branch has
yet been promoted into a solver-ready engineering benchmark.

W39-D3 does not fabricate that missing geometry.

Therefore W39-D3 is mathematically executable but not yet independently
validated against a complete real hydraulic-support mechanism.

## 15. Explicitly not implemented

At W39-D3 closeout, the following remain NOT IMPLEMENTED:

- reference-branch engineering selection
- OPEN/CROSSED semantics
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

## 16. D4 entry condition

W39-D4 may now implement engineering branch resolution.

D4 shall consume the mathematical candidates already produced by W39-D3.

For TWO_SOLUTIONS, D4 may use a valid non-degenerate reference branch to select
the candidate with the matching branch.

D4 shall not:

- recalculate the circle intersection merely to select a branch
- select candidate index 0 by convention
- select by larger or smaller X
- select by larger or smaller Y
- select by visual plausibility

If a non-degenerate reference branch is unavailable, the result shall remain
BRANCH_AMBIGUOUS.

## 17. Validation status

W39-D3 contract and service tests establish software-level deterministic
closure behavior.

They verify:

- point-B calculation
- input-consistency failure
- all six synthetic closure states
- external tangency
- internal tangency
- candidate coordinates
- candidate branch ordering
- reference_branch non-consumption
- provenance
- input immutability
- deterministic repeatability

Passing these tests does not establish physical validation of a manufactured
or field-used hydraulic support.
