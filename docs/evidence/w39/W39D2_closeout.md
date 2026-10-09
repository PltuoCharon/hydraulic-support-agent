# W39-D2 Strongly Typed Four-Bar Closure Model Closeout

## 1. Scope

W39-D2 implements the strongly typed data contract required before numerical
four-bar closure solving.

The implementation is:

app/models/linkage_closure.py

W39-D2 contains:

- explicit solver-input models
- explicit numerical-tolerance representation
- closure multiplicity types
- candidate branch types
- branch-selection status types
- closure candidate models
- selected-pose models
- solver provenance models
- closure-result invariants
- serialization and validation helpers

W39-D2 does not implement numerical four-bar closure.

## 2. Relationship to W38

W39 reuses the W38 geometry and provenance type system.

Reused types include:

- StrictModel
- NormalizedOriginPoint
- EngineeringPoint2D
- MillimetreParameter
- DegreeParameter

W39 therefore does not create a second incompatible coordinate system.

hs.linkageClosure.v1 represents a solver task and solver result.

It does not replace hs.linkageGeometry.v1.

## 3. Solver input

ClosureSolverInput uses:

version = 1

and contains:

- rear_link_base
- front_link_base
- rear_link_length_mm
- shield_beam_effective_length_mm
- front_link_length_mm
- base_pivot_spacing_mm
- rear_link_angle_deg
- reference_branch
- tolerance

The current independent motion variable is:

rear_link_angle_deg

support_height_mm is intentionally not a solver-driving field in W39-D2.

## 4. Numerical tolerance

NumericalTolerance contains:

absolute_mm

and:

relative

Both must be finite and strictly positive.

The tolerance is numerical-computation infrastructure.

It is not a hydraulic-support engineering design parameter.

ClosureSolverInput requires an explicit NumericalTolerance object.

W39-D2 does not freeze a hidden engineering tolerance default.

## 5. Input geometry validation

Canonical rigid-link lengths must be finite and strictly positive:

AB

BC

CD

DA

The input angle and fixed-pivot coordinates must also be finite.

Missing or invalid geometry is not repaired by the model.

The model does not populate geometry from:

- canopy_len
- center_dist
- historical beam_length
- historical example dimensions

base_pivot_spacing_mm is intentionally retained together with the A/D
coordinates.

This redundancy exists for later consistency validation.

W39-D2 does not silently move D or rewrite base_pivot_spacing_mm.

Tolerance-aware A-D/base-spacing consistency checking belongs to the future
numerical solver.

## 6. Closure multiplicity

ClosureMultiplicity contains exactly:

NO_SOLUTION

TANGENT

TWO_SOLUTIONS

DEGENERATE

Closure multiplicity describes the mathematical closure state.

It does not by itself describe whether an engineering pose has been selected.

## 7. Candidate branch semantics

CandidateBranch contains:

POSITIVE

NEGATIVE

TANGENT

ReferenceBranch contains only:

POSITIVE

NEGATIVE

A tangent pose does not establish one of the two non-degenerate reference
branches.

These W39 branch types remain separate from the W38 assembly-side
classification.

## 8. Selection semantics

SelectionStatus contains:

SELECTED

BRANCH_AMBIGUOUS

NOT_APPLICABLE

Closure multiplicity and selection status remain separate concepts.

In particular:

TWO_SOLUTIONS does not imply SELECTED.

A two-solution result may remain BRANCH_AMBIGUOUS.

The model does not guess a branch.

## 9. NO_SOLUTION invariant

For:

closure_state = NO_SOLUTION

the model requires:

candidates = []

selection_status = NOT_APPLICABLE

selected_pose = null

branch_resolution = NONE

No arbitrary C coordinate may be serialized.

## 10. DEGENERATE invariant

For:

closure_state = DEGENERATE

the model requires:

candidates = []

selection_status = NOT_APPLICABLE

selected_pose = null

branch_resolution = NONE

An infinite-solution or otherwise degenerate closure is not represented by an
arbitrary finite candidate.

## 11. TANGENT invariant

For:

closure_state = TANGENT

the model requires exactly one candidate.

That candidate must have:

branch = TANGENT

The result must have:

selection_status = SELECTED

selected_pose != null

branch_resolution = TANGENT_UNIQUE

The selected pose branch must also be TANGENT.

The selected pose C coordinate must equal the sole candidate C coordinate.

## 12. TWO_SOLUTIONS invariant

For:

closure_state = TWO_SOLUTIONS

the model requires exactly two candidates.

Their branch set must be exactly:

POSITIVE

NEGATIVE

Duplicate POSITIVE candidates are invalid.

Duplicate NEGATIVE candidates are invalid.

A TANGENT candidate is invalid in TWO_SOLUTIONS.

A TWO_SOLUTIONS result may be:

SELECTED

or:

BRANCH_AMBIGUOUS

## 13. Ambiguous two-solution result

For:

closure_state = TWO_SOLUTIONS

selection_status = BRANCH_AMBIGUOUS

the model requires:

selected_pose = null

branch_resolution = NONE

The model shall not convert branch ambiguity into an arbitrary engineering
pose.

## 14. Selected two-solution result

For:

closure_state = TWO_SOLUTIONS

selection_status = SELECTED

the model requires:

selected_pose != null

branch_resolution = REFERENCE_POSE

The selected branch must be POSITIVE or NEGATIVE.

The selected branch must correspond to one of the two candidates.

The selected C coordinate must equal the C coordinate of the candidate with
that branch.

Matching the branch label alone is insufficient.

## 15. Selected-pose identity

Whenever selected_pose exists:

selected_pose.rear_link_shield

must equal:

ClosureResult.rear_link_shield

The result therefore cannot contain two contradictory solved B points.

For both TANGENT and selected TWO_SOLUTIONS results, the selected C coordinate
must also correspond exactly to the selected closure candidate.

These are exact object-consistency checks.

They do not replace tolerance-aware geometric calculations in the future
numerical solver.

## 16. Solved-coordinate provenance

Calculated solver coordinates are constrained to:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

A deterministic mathematical result is not automatically VERIFIED.

The model rejects result coordinates that falsely present themselves as
USER_INPUT, RETRIEVED or AI_PROPOSED solver outputs.

## 17. Solver provenance

ClosureSolverProvenance currently uses:

engine = W39_DETERMINISTIC_FOUR_BAR_CLOSURE

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

BranchResolution contains:

REFERENCE_POSE

TANGENT_UNIQUE

NONE

No Formula Registry entry or Calculation Record is invented by W39-D2.

## 18. Strict serialization boundary

The W39 closure models inherit StrictModel.

Unknown fields are therefore rejected.

Validation helpers are provided for:

ClosureSolverInput

and:

ClosureResult

ClosureResult also provides JSON-compatible serialization.

The solver shall return structured hs.linkageClosure.v1 data rather than an
unstructured dictionary.

## 19. Explicitly not implemented

At W39-D2 closeout, the following remain NOT IMPLEMENTED:

- deterministic point-B calculation
- A/D base-spacing consistency calculation
- two-circle intersection
- numerical tangency classification
- NO_SOLUTION classification
- DEGENERATE classification
- closure candidate coordinate generation
- signed branch calculation
- reference-branch selection algorithm
- support-height-driven pose solving
- continuous motion tracking
- beam-tip trajectory
- 80 mm beam-tip validation
- linkage optimization

## 20. D3 entry condition

W39-D3 may now implement deterministic numerical closure primitives.

D3 shall use the frozen D2 models.

D3 shall not bypass ClosureSolverInput or ClosureResult with unstructured
dictionaries.

The first numerical implementation shall focus on:

1. deterministic point B from rear_link_angle_deg
2. A-D/base_pivot_spacing consistency validation
3. two-circle intersection for point C
4. closure-state classification
5. deterministic candidate coordinates
6. candidate branch sign

Reference-branch selection may remain a subsequent W39 step if it is kept
separate from the mathematical intersection primitive.

## 21. Validation status

W39-D2 tests verify data-model behavior and semantic consistency.

They demonstrate that contradictory hs.linkageClosure.v1 objects are rejected.

They do not establish physical validation of a hydraulic-support linkage.

Engineering validation still requires a solver-ready, traceable
ENGINEERING_REFERENCE case.
