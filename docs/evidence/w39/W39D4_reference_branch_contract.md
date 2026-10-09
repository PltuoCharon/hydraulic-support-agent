# W39-D4 Reference-Branch Resolution Contract

## 1. Objective

W39-D4 implements engineering branch resolution on top of the deterministic
mathematical closure produced by W39-D3.

W39-D3 answers:

What mathematical closure solutions exist?

W39-D4 answers:

When TWO_SOLUTIONS exists, which candidate matches the explicitly established
reference configuration?

W39-D4 shall not change the circle-intersection mathematics.

## 2. Layer boundary

The D4 branch-resolution layer shall consume:

- W38 explicit reference geometry
- W39-D2 ClosureSolverInput
- W39-D3 ClosureResult

It shall not independently recalculate the two-circle intersection merely to
select a branch.

The D3 mathematical result remains authoritative for candidate coordinates.


## 3. Reference branch definition

The W39 reference branch is derived from an explicit reference configuration.

Use:

reference B = reference_pose.rear_link_shield

reference C = reference_pose.front_link_shield

fixed D = front_link_base

The reference branch is classified relative to directed line:

reference B -> D

For reference C:

cross = (
    (Dx - Bx) * (Cy - By)
    - (Dy - By) * (Cx - Bx)
)

reference_signed_distance_mm = (
    cross / distance(reference B, D)
)

If the signed distance is positively outside numerical tolerance:

reference_branch = POSITIVE

If the signed distance is negatively outside numerical tolerance:

reference_branch = NEGATIVE

W39-D4 shall not derive reference branch from:

- W38 assembly_side_signature
- A -> D side classification
- candidate list position
- visual appearance
- X coordinate preference
- Y coordinate preference


## 4. Unavailable reference branch

A non-degenerate reference branch cannot be established when:

distance(reference B, D)

is zero or numerically indistinguishable from zero.

A non-degenerate reference branch also cannot be established when reference C
is numerically indistinguishable from the directed reference B-D line.

In either case:

reference_branch = null

The system shall not guess POSITIVE or NEGATIVE.

An unavailable reference branch is not automatically a mathematical closure
failure.

It means only that the supplied reference configuration cannot distinguish the
two non-degenerate W39 branches.

For a TWO_SOLUTIONS result, branch selection must therefore remain:

BRANCH_AMBIGUOUS


## 5. Numerical tolerance

Reference-branch classification shall reuse the W39 NumericalTolerance
semantics.

For distance comparisons:

effective_tolerance_mm = max(
    absolute_mm,
    relative * scale_mm
)

The signed reference-branch metric has unit mm.

The raw cross product has unit mm^2 and shall not be compared directly against
an mm tolerance.

D4 shall not introduce a second incompatible tolerance policy.


## 6. Reference-branch derivation service

W39-D4 shall provide a pure reference classification operation equivalent to:

derive_reference_branch(
    *,
    reference_b: EngineeringPoint2D,
    reference_c: EngineeringPoint2D,
    front_link_base: EngineeringPoint2D,
    tolerance: NumericalTolerance
) -> ReferenceBranch | None

The operation shall classify only the supplied explicit reference geometry.

It shall not solve the four-bar mechanism.

It shall not modify the supplied W38 reference geometry.

## 7. Branch-resolution service

W39-D4 shall provide a branch-resolution operation equivalent to:

resolve_reference_branch(
    *,
    task: ClosureSolverInput,
    result: ClosureResult
) -> ClosureResult

This operation shall consume the already-computed D3 mathematical result.

It shall return a new ClosureResult.

It shall not mutate task.

It shall not mutate result.


## 8. Non-TWO_SOLUTIONS preservation

If closure_state is:

NO_SOLUTION

or:

DEGENERATE

or:

TANGENT

D4 shall preserve the D3 result unchanged in engineering semantics.

D4 shall not create a new branch decision for these states.

In particular, a TANGENT result remains:

selection_status = SELECTED

branch_resolution = TANGENT_UNIQUE

because its selection came from mathematical uniqueness in D3.

D4 shall not relabel tangent uniqueness as REFERENCE_POSE selection.


## 9. TWO_SOLUTIONS without reference branch

If:

closure_state = TWO_SOLUTIONS

and:

task.reference_branch = null

then D4 shall preserve:

selection_status = BRANCH_AMBIGUOUS

selected_pose = null

branch_resolution = NONE

D4 shall not choose the first candidate.

D4 shall not prefer POSITIVE.

D4 shall not prefer NEGATIVE.

D4 shall not infer a branch from candidate coordinates alone.


## 10. TWO_SOLUTIONS with explicit reference branch

If:

closure_state = TWO_SOLUTIONS

and:

task.reference_branch = POSITIVE

D4 shall select the candidate whose branch is exactly:

POSITIVE

If:

task.reference_branch = NEGATIVE

D4 shall select the candidate whose branch is exactly:

NEGATIVE

Candidate lookup shall be by branch semantics.

Candidate list position shall not be used for selection.

The selected pose shall use:

rear_link_shield = result.rear_link_shield

front_link_shield = selected candidate point_c

rear_link_angle_deg = task.rear_link_angle_deg

branch = selected candidate branch

The selected pose shall therefore reuse D3 coordinates exactly.

No B or C coordinate shall be recomputed in D4.


## 11. Successful reference resolution

After successful TWO_SOLUTIONS reference-branch resolution:

closure_state remains:

TWO_SOLUTIONS

The original two candidates remain present.

selection_status becomes:

SELECTED

selected_pose becomes non-null.

branch_resolution becomes:

REFERENCE_POSE

The selected candidate is not removed from the candidate list.

The unselected mathematical candidate is also retained.

Engineering selection shall not destroy the original mathematical solution
set.


## 12. Expected D3 TWO_SOLUTIONS input

D4 reference resolution expects a mathematical TWO_SOLUTIONS result from D3.

Before reference resolution, that result shall have:

selection_status = BRANCH_AMBIGUOUS

selected_pose = null

branch_resolution = NONE

If a TWO_SOLUTIONS result is already:

SELECTED

before D4 resolution, D4 shall reject it as an invalid layer input rather than
silently selecting again.

This prevents double resolution and hides no previous branch decision.


## 13. Candidate integrity

D4 shall locate a candidate by its explicit branch value.

If the requested reference branch cannot be found in the mathematical result,
D4 shall fail explicitly.

It shall not:

- substitute the other candidate
- select candidate index 0
- manufacture a new candidate
- recalculate C

The D2 model normally prevents this inconsistent state, but D4 shall preserve
the semantic boundary explicitly.


## 14. Integrated deterministic pose operation

W39-D4 may provide an orchestration operation equivalent to:

solve_closure(
    task: ClosureSolverInput
) -> ClosureResult

The orchestration shall:

1. call the W39-D3 mathematical closure solver exactly once
2. receive its typed ClosureResult
3. apply D4 reference-branch resolution
4. return the resolved typed ClosureResult

For TWO_SOLUTIONS without reference_branch, the final result remains
BRANCH_AMBIGUOUS.

For TWO_SOLUTIONS with reference_branch, the final result may become SELECTED.

The orchestration shall not contain a second circle-intersection
implementation.


## 15. Relationship to W38 reference pose

W38 ReferencePose supplies explicit engineering geometry:

rear_link_shield

front_link_shield

and the W38 fixed geometry supplies:

front_link_base

These explicit points are sufficient to classify the W39 reference branch when
the reference geometry is non-degenerate.

W38 ReferencePoseAnalysis may still report:

SAME_SIDE

OPPOSITE_SIDE

DEGENERATE

but those assembly-side values are not W39 branch labels.

D4 shall calculate the W39 reference branch from explicit B/C/D coordinates.

It shall not translate:

SAME_SIDE -> POSITIVE

or:

OPPOSITE_SIDE -> NEGATIVE

No such mapping is frozen.


## 16. Provenance boundary

D4 branch resolution does not create new geometric coordinates.

It reuses D3 calculated B and C coordinates.

Therefore selected_pose coordinate provenance remains:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

Successful reference resolution changes branch-selection provenance to:

branch_resolution = REFERENCE_POSE

It does not promote geometric evidence_status to VERIFIED.

D4 introduces no Formula Registry ID.

D4 creates no Calculation Record.


## 17. Explicitly outside W39-D4

W39-D4 does not implement:

- circle-intersection recalculation
- support-height-to-pose mapping
- operating-height sweep
- previous-pose continuity
- automatic branch switching
- OPEN/CROSSED terminology
- top-beam pose
- beam-tip trajectory
- 80 mm beam-tip validation
- interference checking
- linkage optimization
- GA
- PSO
- NSGA-II

## 18. D5 entry condition

After D4 reference-branch resolution is tested, W39-D5 may integrate:

W38 LinkageGeometry
+
W38 explicit ReferencePose
+
W39 closure solver

into a repeatable engineering reference-pose workflow.

D5 shall focus on integration and regression behavior.

It shall not change D3 circle-intersection mathematics merely to make an
engineering example pass.

