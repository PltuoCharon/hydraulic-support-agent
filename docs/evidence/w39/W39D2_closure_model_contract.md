# W39-D2 Four-Bar Closure Model Contract

## 1. Objective

W39-D2 defines the strongly typed data model for deterministic four-bar
closure solving.

The target model module is:

app/models/linkage_closure.py

W39-D2 defines representation and consistency rules only.

It does not implement:

- point-B numerical calculation
- circle intersection
- candidate generation
- branch selection algorithms
- trajectory solving
- optimization

Numerical closure implementation belongs to a later W39 step.

## 2. Relationship to W38

W39 shall reuse W38 engineering parameter and coordinate semantics.

It shall reuse types such as:

- EngineeringPoint2D
- NormalizedOriginPoint
- MillimetreParameter
- DegreeParameter
- StrictModel

W39 shall not create a second incompatible coordinate or engineering-parameter
system.

W39 closure models represent a solver task and solver result.

They do not replace hs.linkageGeometry.v1.


## 3. Frozen enums

ClosureMultiplicity shall contain exactly:

- NO_SOLUTION
- TANGENT
- TWO_SOLUTIONS
- DEGENERATE

CandidateBranch shall contain exactly:

- POSITIVE
- NEGATIVE
- TANGENT

ReferenceBranch shall contain exactly:

- POSITIVE
- NEGATIVE

SelectionStatus shall contain exactly:

- SELECTED
- BRANCH_AMBIGUOUS
- NOT_APPLICABLE

ReferenceBranch intentionally excludes TANGENT.

A tangent pose does not establish one of the two non-degenerate configuration
branches.

W39 candidate branch terminology remains separate from the W38
assembly_side_signature terminology.


## 4. NumericalTolerance

W39 shall define:

NumericalTolerance

with:

absolute_mm

relative

absolute_mm:

- unit semantics = mm
- must be finite
- must be strictly positive

relative:

- dimensionless
- must be finite
- must be strictly positive

No hydraulic-support engineering meaning shall be assigned to these values.

They are numerical-computation infrastructure.

ClosureSolverInput shall require an explicit NumericalTolerance object.

W39-D2 shall not silently inject an engineering tolerance through a hidden
default.

A later application layer may provide a centralized software default only
after that default is explicitly frozen and tested.


## 5. ClosureSolverInput

ClosureSolverInput shall use:

version = hs.linkageClosure.v1

and contain:

rear_link_base

front_link_base

rear_link_length_mm

shield_beam_effective_length_mm

front_link_length_mm

base_pivot_spacing_mm

rear_link_angle_deg

reference_branch

tolerance

The field names for canonical geometry shall retain their W38 meanings.

### rear_link_base

Type:

NormalizedOriginPoint

It retains the W38 normalized representation:

A = (0, 0)

This is a representation convention, not fabricated measured geometry.

### front_link_base

Type:

EngineeringPoint2D

This is fixed pivot D.

Its parameter provenance shall be preserved.


### rigid-link lengths

The solver input explicitly carries:

rear_link_length_mm

shield_beam_effective_length_mm

front_link_length_mm

base_pivot_spacing_mm

using W38 MillimetreParameter semantics.

The four values correspond to:

AB

BC

CD

DA

respectively.

base_pivot_spacing_mm is intentionally carried even though A and D coordinates
also geometrically define the fixed-base spacing.

This redundancy exists so a later solver can validate consistency.

A solver shall not move D to make the supplied base_pivot_spacing_mm agree.

A solver shall not rewrite base_pivot_spacing_mm to make it agree with D.

A disagreement shall be handled as an explicit input-consistency failure.

### rear_link_angle_deg

Type:

DegreeParameter

It is the W39 first independent motion variable.

### reference_branch

Type:

ReferenceBranch or null

A non-null value represents a non-degenerate branch established outside the
numerical circle-intersection routine, normally from the W38 reference pose.

W39-D2 does not calculate reference_branch.

### tolerance

Type:

NumericalTolerance

It is required explicitly.


## 6. ClosureCandidate

ClosureCandidate shall contain:

point_c

branch

note

point_c:

Type:

EngineeringPoint2D

It represents one mathematically valid C candidate.

branch:

Type:

CandidateBranch

For TWO_SOLUTIONS, candidate branches shall be:

POSITIVE

and:

NEGATIVE

For TANGENT, the candidate branch shall be:

TANGENT

A candidate is a mathematical closure solution.

It is not automatically the selected engineering pose.

## 7. ClosureSelectedPose

ClosureSelectedPose shall contain:

rear_link_shield

front_link_shield

rear_link_angle_deg

branch

rear_link_shield represents solved B.

front_link_shield represents selected C.

branch identifies the branch of the selected C point.

For a non-degenerate two-solution pose the selected branch is POSITIVE or
NEGATIVE.

For a tangent pose the selected branch is TANGENT.

A selected pose exists only after selection semantics are satisfied.


## 8. ClosureSolverProvenance

ClosureSolverProvenance shall make the current W39 evidence boundary explicit.

It shall contain:

engine

evidence_status

formula_ids

calculation_record_ids

branch_resolution

note

engine shall identify the deterministic W39 four-bar closure implementation.

evidence_status shall currently be:

PARTIAL

formula_ids shall currently remain empty.

calculation_record_ids shall currently remain empty.

branch_resolution shall distinguish:

REFERENCE_POSE

TANGENT_UNIQUE

NONE

REFERENCE_POSE means the selected TWO_SOLUTIONS candidate was resolved using a
non-degenerate reference branch.

TANGENT_UNIQUE means the mathematical closure itself produced one unique
tangent candidate.

NONE means no branch was selected through either of those mechanisms.

ClosureSolverProvenance shall not claim VERIFIED merely because deterministic
mathematics succeeded.


## 9. ClosureResult

ClosureResult shall use:

version = hs.linkageClosure.v1

and contain:

closure_state

selection_status

rear_link_shield

candidates

selected_pose

provenance

note

rear_link_shield is solved point B.

For a valid solver task, B exists even when no valid C closure exists.

Closure multiplicity and selection status are independent fields, but their
combinations must obey the following invariants.

## 10. NO_SOLUTION invariant

If:

closure_state = NO_SOLUTION

then:

candidates = []

selection_status = NOT_APPLICABLE

selected_pose = null

No invented C coordinate is allowed.

## 11. DEGENERATE invariant

If:

closure_state = DEGENERATE

then:

candidates = []

selection_status = NOT_APPLICABLE

selected_pose = null

Infinite-solution or otherwise degenerate geometry shall not be represented by
an arbitrary finite candidate.


## 12. TANGENT invariant

If:

closure_state = TANGENT

then exactly one ClosureCandidate shall exist.

Its branch shall be:

TANGENT

selection_status shall be:

SELECTED

selected_pose shall be non-null.

The selected pose branch shall also be:

TANGENT

The tangent case does not require reference-branch resolution.

Its branch_resolution shall be:

TANGENT_UNIQUE

## 13. TWO_SOLUTIONS invariant

If:

closure_state = TWO_SOLUTIONS

then exactly two ClosureCandidate objects shall exist.

Their branch set shall be exactly:

POSITIVE

NEGATIVE

Two POSITIVE candidates are invalid.

Two NEGATIVE candidates are invalid.

A TANGENT candidate is invalid in TWO_SOLUTIONS.

For TWO_SOLUTIONS, selection_status may be:

SELECTED

or:

BRANCH_AMBIGUOUS


If:

selection_status = SELECTED

then:

selected_pose shall be non-null

and branch_resolution shall be:

REFERENCE_POSE

The selected pose branch shall match exactly one candidate branch.

If:

selection_status = BRANCH_AMBIGUOUS

then:

selected_pose = null

and branch_resolution shall be:

NONE

The model shall not convert BRANCH_AMBIGUOUS into an arbitrary selected pose.

## 14. Invalid combinations

The following examples shall be rejected by model validation:

- NO_SOLUTION with a candidate
- NO_SOLUTION with SELECTED
- DEGENERATE with selected_pose
- TANGENT with zero candidates
- TANGENT with two candidates
- TANGENT candidate marked POSITIVE
- TWO_SOLUTIONS with one candidate
- TWO_SOLUTIONS with two POSITIVE candidates
- TWO_SOLUTIONS with a TANGENT candidate
- BRANCH_AMBIGUOUS with selected_pose
- SELECTED without selected_pose

Strong typing shall prevent semantically contradictory solver results from
being serialized as valid hs.linkageClosure.v1 data.


## 15. Solved-coordinate provenance

When D3 later creates B or C coordinates, each calculated coordinate component
shall preserve the W39-D1 boundary:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

W39-D2 itself does not calculate those coordinates.

## 16. Input immutability

A future closure solver shall not mutate ClosureSolverInput.

It shall not mutate source W38 LinkageGeometry data used to construct the
input.

Solver output shall be represented by a new ClosureResult object.

## 17. Missing and invalid geometry

W39-D2 shall not represent missing solver-required geometry using zero.

No field shall be populated from:

- canopy_len
- center_dist
- historical beam_length
- historical example dimensions

Required geometry is required.

Invalid geometry shall fail explicitly rather than being repaired by the data
model.

## 18. Support-height boundary

ClosureSolverInput does not use support_height_mm as a solver-driving field.

The current independent motion variable remains:

rear_link_angle_deg

Support-height-driven pose solving remains outside W39-D2.


## 19. D3 entry condition

After this model contract is validated, W39-D2 may implement:

app/models/linkage_closure.py

The implementation shall enforce the frozen result invariants through model
validation.

Only after the model implementation and tests are frozen may W39-D3 implement
the first deterministic numerical closure service.

W39-D3 shall use the D2 models rather than returning an unstructured dict.

## 20. Selected-pose identity invariants

A selected pose shall be internally identical to the solver result from which
it was selected.

Whenever selected_pose is non-null:

selected_pose.rear_link_shield

shall equal:

ClosureResult.rear_link_shield

The selected pose shall not carry a second contradictory solved B point.

For:

closure_state = TANGENT

selected_pose.front_link_shield

shall equal the sole candidate point_c.

For:

closure_state = TWO_SOLUTIONS
selection_status = SELECTED

selected_pose.front_link_shield

shall equal the point_c of the ClosureCandidate whose branch equals the
selected pose branch.

Matching the branch label alone is insufficient.

The model shall reject a selected pose whose coordinates do not correspond to
the candidate that was actually selected.

These are exact data-consistency invariants.

They do not replace numerical geometric comparison using tolerance inside the
future D3 solver.
