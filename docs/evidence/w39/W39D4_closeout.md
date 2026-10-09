# W39-D4 Reference-Branch Resolution Closeout

## 1. Scope

W39-D4 implements engineering branch resolution on top of the deterministic
mathematical closure produced by W39-D3.

The implementation extends:

app/services/linkage_closure.py

W39-D4 now supports:

- explicit reference-branch classification from B/C/D geometry
- POSITIVE reference branch
- NEGATIVE reference branch
- unavailable / degenerate reference branch
- TWO_SOLUTIONS reference-branch resolution
- preservation of mathematical candidate sets
- integrated D3 -> D4 closure orchestration

W39-D4 does not modify the D3 circle-intersection mathematics.

## 2. Layer separation

W39-D3 answers:

What mathematical closure solutions exist?

W39-D4 answers:

Which mathematical candidate matches the explicitly established engineering
reference branch?

These responsibilities remain separate.

D4 does not recalculate circle intersection merely to choose a branch.

## 3. Reference branch geometry

The W39 reference branch is derived from explicit reference geometry:

reference B

reference C

fixed D

The branch is classified relative to directed line:

reference B -> D

using signed perpendicular distance.

Positive signed distance means:

POSITIVE

Negative signed distance means:

NEGATIVE

A value numerically indistinguishable from zero does not establish a
non-degenerate reference branch.

## 4. Relationship to W38

W38 explicit reference geometry may provide:

reference_pose.rear_link_shield

reference_pose.front_link_shield

and:

fixed_geometry.front_link_base

These coordinates can establish the W39 reference branch.

W38 assembly-side values:

SAME_SIDE

OPPOSITE_SIDE

DEGENERATE

are not W39 reference-branch values.

W39-D4 does not translate:

SAME_SIDE -> POSITIVE

or:

OPPOSITE_SIDE -> NEGATIVE

No such mapping is frozen.

## 5. Degenerate or unavailable reference branch

A reference branch is unavailable when:

- reference B and D are numerically coincident
- reference C is numerically indistinguishable from the B-D line

In those cases the reference branch is:

null

The system does not guess POSITIVE or NEGATIVE.

For TWO_SOLUTIONS, the engineering result therefore remains:

selection_status = BRANCH_AMBIGUOUS

selected_pose = null

branch_resolution = NONE

## 6. Numerical tolerance

Reference-branch classification reuses W39 NumericalTolerance semantics.

The distance tolerance remains:

effective_tolerance_mm = max(
    absolute_mm,
    relative * scale_mm
)

The branch metric is:

signed_distance_mm = cross / distance(B, D)

The resulting quantity has unit mm.

D4 does not introduce a second incompatible tolerance policy.

## 7. Reference derivation

W39-D4 provides:

derive_reference_branch(...)

This operation classifies explicit B/C/D reference geometry.

It does not solve the four-bar mechanism.

It does not modify W38 reference geometry.

It returns:

POSITIVE

NEGATIVE

or:

null

when a non-degenerate branch cannot be established.

## 8. Reference resolution

W39-D4 provides:

resolve_reference_branch(...)

This operation consumes an already calculated ClosureResult.

For non-TWO_SOLUTIONS states, D3 mathematical semantics are preserved.

For TWO_SOLUTIONS, the expected unresolved D3 state is:

selection_status = BRANCH_AMBIGUOUS

selected_pose = null

branch_resolution = NONE

D4 rejects a TWO_SOLUTIONS result that has already been selected before the
reference-resolution layer.

This prevents double branch resolution.

## 9. TWO_SOLUTIONS without reference branch

When:

task.reference_branch = null

D4 preserves the unresolved mathematical result.

It does not select:

- the first candidate
- POSITIVE by preference
- NEGATIVE by preference
- larger X
- smaller X
- larger Y
- smaller Y

The result remains BRANCH_AMBIGUOUS.

## 10. TWO_SOLUTIONS with reference branch

When:

task.reference_branch = POSITIVE

D4 selects the candidate explicitly labelled:

POSITIVE

When:

task.reference_branch = NEGATIVE

D4 selects the candidate explicitly labelled:

NEGATIVE

Candidate lookup is based on branch semantics.

Candidate list position is not an engineering selection rule.

## 11. Selected pose construction

After successful reference resolution:

closure_state remains:

TWO_SOLUTIONS

selection_status becomes:

SELECTED

branch_resolution becomes:

REFERENCE_POSE

selected_pose uses:

rear_link_shield = D3 result rear_link_shield

front_link_shield = selected D3 candidate point_c

rear_link_angle_deg = original solver input angle

branch = selected candidate branch

D4 does not recompute B.

D4 does not recompute C.

## 12. Mathematical candidate preservation

Successful engineering branch selection does not destroy the mathematical
solution set.

Both original D3 candidates remain in:

ClosureResult.candidates

The selected candidate remains present.

The unselected candidate also remains present.

This preserves the distinction between:

mathematical solutions

and:

engineering branch selection.

## 13. Tangent preservation

TANGENT already has one mathematically unique C point.

D3 therefore produces:

selection_status = SELECTED

branch_resolution = TANGENT_UNIQUE

D4 preserves this result.

D4 does not relabel tangent mathematical uniqueness as:

REFERENCE_POSE

## 14. Candidate integrity

D4 locates the requested candidate by explicit branch value.

If the requested branch cannot be found, D4 fails explicitly.

It does not:

- substitute another candidate
- select candidate index 0
- manufacture a candidate
- recalculate point C

The D2 model normally prevents inconsistent TWO_SOLUTIONS candidate sets, but
D4 preserves this boundary independently.

## 15. Immutability

resolve_reference_branch does not mutate:

ClosureSolverInput

or:

the supplied D3 ClosureResult

A new ClosureResult is returned.

Non-TWO_SOLUTIONS results are returned as distinct deep copies while preserving
their engineering semantics.

## 16. Integrated closure operation

W39-D4 provides:

solve_closure(...)

The operation performs:

ClosureSolverInput

-> W39-D3 solve_closure_candidates()

-> W39-D4 resolve_reference_branch()

-> ClosureResult

The D3 mathematical solver is invoked exactly once.

The orchestration does not contain a second circle-intersection implementation.

## 17. Provenance boundary

D4 creates no new geometric coordinates.

Selected-pose coordinates retain D3 provenance:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

Successful branch resolution changes only branch-selection provenance:

branch_resolution = REFERENCE_POSE

It does not promote the underlying geometry to VERIFIED.

W39-D4 introduces no Formula Registry ID.

W39-D4 creates no Calculation Record.

## 18. Explicitly not implemented

At W39-D4 closeout, the following remain NOT IMPLEMENTED:

- automatic derivation from a complete W38 LinkageGeometry object
- support-height-to-pose mapping
- operating-height sweep
- previous-pose continuity
- automatic branch switching
- OPEN/CROSSED semantics
- top-beam pose
- beam-tip trajectory
- 80 mm beam-tip validation
- interference checking
- linkage optimization
- GA
- PSO
- NSGA-II

## 19. D5 entry condition

W39-D5 may integrate the W38 canonical geometry and explicit reference pose
with the W39 closure solver.

The D5 workflow may:

1. consume one LinkageGeometry object
2. verify required fixed and derived geometry exists
3. derive the W39 reference branch from explicit W38 B/C/D coordinates
4. construct a typed ClosureSolverInput
5. execute the W39 D3 + D4 solver chain
6. compare the solved reference configuration with the supplied reference pose
7. preserve all provenance and missing-data boundaries

D5 shall be an integration and regression layer.

It shall not modify D3 circle-intersection mathematics merely to make an
engineering case pass.

## 20. Validation status

W39-D4 tests verify:

- POSITIVE reference classification
- NEGATIVE reference classification
- degenerate reference handling
- tolerance-aware reference classification
- positive candidate selection
- negative candidate selection
- ambiguous behavior without reference branch
- selected-coordinate reuse
- preservation of both mathematical candidates
- tangent preservation
- rejection of double resolution
- candidate-integrity failure
- input/result immutability
- deterministic resolution
- single D3 invocation in integrated solving

These are software and engineering-semantics checks.

They do not constitute physical validation of a real hydraulic support.
