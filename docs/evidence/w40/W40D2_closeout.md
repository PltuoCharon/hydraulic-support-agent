# W40-D2 Strongly Typed Continuous Motion Model Closeout

## 1. Scope

W40-D2 introduces the strongly typed data model for one-direction continuous
four-bar motion.

Implementation:

app/models/linkage_motion.py

The implemented model layer contains:

- MotionDirection
- MotionTermination
- MotionSweepInput
- MotionSample
- MotionSweepProvenance
- MotionSegmentResult

W40-D2 implements data validation only.

It does not execute an angle sweep.

## 2. One-direction segment semantics

One MotionSweepInput represents motion from one explicit engineering reference
pose in exactly one direction.

The allowed directions are:

INCREASING

DECREASING

There is no AUTO direction.

If motion on both sides of the reference pose is required, two separate motion
segments shall be constructed.

## 3. Reference branch requirement

A continuous motion segment requires:

reference_task.reference_branch = POSITIVE

or:

reference_task.reference_branch = NEGATIVE

A null reference branch is rejected.

A tangent-only W39 pose does not independently provide a non-degenerate
continuous-motion branch seed.

W40-D2 does not guess the engineering branch.

## 4. Reference-angle anchoring

The first requested angle shall equal:

reference_task.rear_link_angle_deg

The motion therefore starts from its explicit engineering reference pose.

MotionSweepInput requires at least two angle samples.

One isolated reference pose remains a W39 single-pose problem.

## 5. Angle validation

All requested angle values shall be finite.

For:

INCREASING

the values shall be strictly increasing.

For:

DECREASING

the values shall be strictly decreasing.

Duplicate adjacent angles are rejected.

A direction/order contradiction is rejected by model validation.

## 6. Frozen mechanism representation

MotionSweepInput reuses the complete:

ClosureSolverInput

as reference_task.

It does not independently duplicate:

- A
- D
- AB
- BC
- CD
- DA
- NumericalTolerance
- reference branch

Later sweep execution shall vary only rear_link_angle_deg when constructing
each W39 closure task.

## 7. MotionSample

Each MotionSample records:

sample_index

requested_angle_deg

complete ClosureResult

The complete W39 ClosureResult remains authoritative for:

- closure multiplicity
- mathematical candidates
- selected pose
- B/C coordinates
- selected branch
- branch-resolution provenance

W40-D2 does not create separate duplicate B/C fields.

## 8. Mathematical candidate preservation

Because MotionSample stores the complete W39 ClosureResult, TWO_SOLUTIONS
samples retain both:

POSITIVE

and:

NEGATIVE

mathematical candidates.

Engineering branch tracking does not delete the unselected mathematical
solution.

## 9. Normal trajectory sample

A normal trajectory sample is:

closure_state = TWO_SOLUTIONS

selection_status = SELECTED

selected_pose != null

selected_pose.branch = segment reference branch

branch_resolution = REFERENCE_POSE

Every non-boundary TWO_SOLUTIONS sample shall satisfy this invariant.

## 10. Branch-continuity model invariant

A POSITIVE MotionSegmentResult cannot contain a selected NEGATIVE
TWO_SOLUTIONS sample.

A NEGATIVE MotionSegmentResult cannot contain a selected POSITIVE
TWO_SOLUTIONS sample.

TWO_SOLUTIONS + BRANCH_AMBIGUOUS is invalid inside a successful typed motion
segment.

The model therefore prevents silent branch jumping independently of the future
sweep service.

## 11. Tangent boundary

TANGENT may appear only as the terminal boundary sample.

Its W39 semantics remain:

selection_status = SELECTED

selected_pose.branch = TANGENT

branch_resolution = TANGENT_UNIQUE

The corresponding MotionTermination is:

TANGENT_BOUNDARY

No later sample may exist in the same segment.

## 12. NO_SOLUTION boundary

NO_SOLUTION may be retained as the final attempted sample.

It has no selected pose.

The corresponding MotionTermination is:

NO_SOLUTION_BOUNDARY

The boundary sample is not a valid trajectory pose.

No later sample may exist in the same segment.

## 13. DEGENERATE boundary

DEGENERATE may be retained as the final attempted sample.

It has no selected pose.

The corresponding MotionTermination is:

DEGENERATE_BOUNDARY

The boundary sample is not a valid trajectory pose.

No later sample may exist in the same segment.

## 14. Gap-and-resume prevention

MotionSample indexes shall be contiguous:

0, 1, 2, ..., n - 1

Requested angles shall preserve the processed motion order.

After a typed tangent, no-solution, or degenerate boundary, the same
MotionSegmentResult cannot contain later samples.

Gap-and-resume is therefore invalid at the model layer.

## 15. Completion semantics

For:

termination = COMPLETED

the number of processed samples shall equal:

requested_angle_count

Every sample shall be a valid selected TWO_SOLUTIONS pose on the frozen
reference branch.

A COMPLETED result cannot contain:

- TANGENT
- NO_SOLUTION
- DEGENERATE
- BRANCH_AMBIGUOUS

## 16. Requested versus processed samples

requested_angle_count records the total requested angle count.

len(samples) records the processed count.

The model requires:

len(samples) <= requested_angle_count

Boundary termination may therefore occur before every requested angle has been
processed.

COMPLETED requires equality.

## 17. Provenance

MotionSweepProvenance is frozen as:

engine = W40_BRANCH_PRESERVING_ANGLE_SWEEP

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

The model rejects fabricated Formula Registry IDs.

The model rejects fabricated Calculation Record IDs.

W40 sequence construction does not create an independent engineering formula.

## 18. Strict-model behavior

The W40 motion models reuse the project StrictModel behavior.

Unknown extra fields are rejected.

For example, support_height_mm cannot be silently inserted into
MotionSweepInput.

The model layer remains explicit rather than permissive.

## 19. Immutability

Model construction does not mutate the source:

- ClosureSolverInput
- ClosureResult
- DegreeParameter
- caller-provided angle objects

The tests verify source serialization remains unchanged.

## 20. Support-height boundary

The W40-D2 models do not require:

support_height_mm

They do not infer support height from B/C coordinates.

The existing W38 PoseResult is therefore not used as the authoritative W40
MotionSample model.

## 21. Top-beam boundary

MotionSegmentResult does not contain:

top_beam_pose

beam_tip_trajectory

beam_tip_horizontal_displacement

or:

80 mm compliance

Those outputs require later top-beam and operating-height semantics.

No placeholder geometry is fabricated in W40-D2.

## 22. Validation achieved

W40-D2 automated tests verify:

- increasing input
- decreasing input
- non-null reference branch
- minimum sample count
- finite angles
- reference-angle anchoring
- strict monotonicity
- extra-field rejection
- source immutability
- sample-index validation
- provenance defaults
- rejection of fake formula/calculation traces
- POSITIVE completed segment
- NEGATIVE completed segment
- requested/processed count consistency
- opposite-branch rejection
- contiguous sample indexes
- result angle ordering
- tangent terminal boundary
- no-solution terminal boundary
- degenerate terminal boundary
- no post-boundary samples
- ambiguous TWO_SOLUTIONS rejection
- preservation of W39 mathematical candidates
- absence of support-height/top-beam result fields
- JSON serialization round trip
- W39 result immutability

These are software and semantic validation checks.

They are not physical mechanism validation.

## 23. D3 entry condition

W40-D3 may now implement:

sweep_rear_link_angles(...)

The service shall:

1. consume MotionSweepInput
2. copy the reference ClosureSolverInput per requested angle
3. change only rear_link_angle_deg
4. call the existing W39 solve_closure(...)
5. preserve the frozen reference branch
6. append one MotionSample per processed angle
7. stop at the first TANGENT, NO_SOLUTION, or DEGENERATE boundary
8. never gap and resume
9. return one validated MotionSegmentResult

The W40-D2 model shall remain the final structural guard around D3 service
output.

W40-D3 shall not implement support-height solving.

W40-D3 shall not implement top-beam propagation.
