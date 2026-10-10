# W40-D2 Strongly Typed Continuous Motion Model Contract

## 1. Objective

W40-D2 defines strongly typed models for one-direction continuous four-bar
motion on top of the frozen W39 ClosureSolverInput and ClosureResult models.

Target implementation:

app/models/linkage_motion.py

W40-D2 defines data semantics only.

It does not implement the angle-sweep service.

The primary model types shall be equivalent to:

MotionDirection

MotionTermination

MotionSweepInput

MotionSample

MotionSweepProvenance

MotionSegmentResult

## 2. One-direction motion segment

One MotionSweepInput represents one continuous motion direction starting from
the explicit W39 reference pose.

A single segment is either:

INCREASING

or:

DECREASING

in rear_link_angle_deg.

If motion is required on both sides of the reference pose, the caller shall
construct two explicit motion segments:

reference -> increasing angles

and:

reference -> decreasing angles

W40-D2 shall not hide two physical sweep directions inside one unordered
sequence.

## 3. MotionDirection

MotionDirection shall contain exactly:

INCREASING

DECREASING

No AUTO direction is allowed.

No UNKNOWN direction is allowed.

The caller shall state the intended sweep direction explicitly.

## 4. MotionTermination

MotionTermination shall contain exactly:

COMPLETED

TANGENT_BOUNDARY

NO_SOLUTION_BOUNDARY

DEGENERATE_BOUNDARY

BRANCH_AMBIGUOUS is not a normal termination value.

An unexpected ambiguous TWO_SOLUTIONS state is a layer error and shall not be
encoded as a successful MotionSegmentResult.

## 5. MotionSweepInput

MotionSweepInput shall contain at least:

version = 1

reference_task: ClosureSolverInput

direction: MotionDirection

angle_samples_deg: list[DegreeParameter]

The explicit NumericalTolerance remains inside reference_task.

W40-D2 shall not introduce a second tolerance field with different semantics.

## 6. Reference task branch requirement

MotionSweepInput.reference_task.reference_branch shall be non-null.

It shall be exactly:

POSITIVE

or:

NEGATIVE

A reference task without a non-degenerate branch is invalid for a W40
continuous motion segment.

A TANGENT-only W39 reference configuration is not sufficient to construct
MotionSweepInput.

## 7. Reference angle anchoring

The first angle sample shall be exactly the reference task driving angle:

angle_samples_deg[0].value
=
reference_task.rear_link_angle_deg.value

The first sample is therefore not merely assumed to be the reference because
of list position.

Its numerical equality to the explicit W39 reference angle is validated.

A W40 motion segment starts at its engineering reference pose and proceeds in
one direction away from that reference.

## 8. Minimum sample count

MotionSweepInput shall contain at least two angle samples.

One isolated reference angle is a W39 single-pose problem, not a W40 continuous
motion segment.

## 9. Finite angle values

Every angle_samples_deg value shall be finite.

NaN is invalid.

Positive infinity is invalid.

Negative infinity is invalid.

## 10. Strict monotonicity

For direction:

INCREASING

the model shall require:

angle[i + 1] > angle[i]

for every adjacent pair.

For direction:

DECREASING

the model shall require:

angle[i + 1] < angle[i]

for every adjacent pair.

Equal adjacent values are invalid.

A sequence whose numerical ordering contradicts MotionDirection is invalid.

## 11. Frozen geometry source

The reference_task contains the frozen mechanism geometry:

A

D

AB

BC

CD

DA

reference branch

NumericalTolerance

W40-D2 shall not duplicate those authoritative mechanism fields at the
MotionSweepInput top level.

Later sweep execution shall create each per-angle ClosureSolverInput from the
reference task while changing only:

rear_link_angle_deg

## 12. MotionSample

MotionSample shall contain at least:

version = 1

sample_index: non-negative integer

requested_angle_deg: DegreeParameter

closure_result: ClosureResult

The complete W39 ClosureResult remains authoritative for:

- closure_state
- mathematical candidates
- selected pose
- selected branch
- B coordinate
- C coordinate
- branch-resolution provenance

MotionSample shall not duplicate authoritative B/C coordinates into separate
independent fields.

## 13. Normal selected sample

A normal non-boundary trajectory sample shall contain:

closure_state = TWO_SOLUTIONS

selection_status = SELECTED

selected_pose != null

selected_pose.branch = frozen segment reference branch

branch_resolution = REFERENCE_POSE

Such a sample is a valid selected trajectory pose.

## 14. Tangent sample

A TANGENT sample may appear only as the final sample in a terminated motion
segment.

It shall retain the W39 semantics:

closure_state = TANGENT

selection_status = SELECTED

selected_pose != null

selected_pose.branch = TANGENT

branch_resolution = TANGENT_UNIQUE

Its segment termination shall be:

TANGENT_BOUNDARY

No later MotionSample may follow it in the same MotionSegmentResult.

## 15. NO_SOLUTION sample

A NO_SOLUTION sample may be retained as the final attempted boundary sample.

Its W39 result shall contain no selected pose.

Its segment termination shall be:

NO_SOLUTION_BOUNDARY

It is not a trajectory pose.

No later MotionSample may follow it in the same MotionSegmentResult.

## 16. DEGENERATE sample

A DEGENERATE sample may be retained as the final attempted boundary sample.

Its W39 result shall contain no selected pose.

Its segment termination shall be:

DEGENERATE_BOUNDARY

It is not a trajectory pose.

No later MotionSample may follow it in the same MotionSegmentResult.

## 17. Ambiguous TWO_SOLUTIONS is invalid

A MotionSample containing:

closure_state = TWO_SOLUTIONS

with:

selection_status = BRANCH_AMBIGUOUS

is invalid inside MotionSegmentResult.

The W40 continuous-motion layer requires a frozen non-null reference branch.

The sweep service shall fail explicitly before constructing a successful
segment result containing such ambiguity.

## 18. Branch continuity invariant

For every TWO_SOLUTIONS sample in one MotionSegmentResult:

selected_pose.branch

shall equal:

MotionSegmentResult.reference_branch

A POSITIVE segment cannot contain a selected NEGATIVE sample.

A NEGATIVE segment cannot contain a selected POSITIVE sample.

TANGENT is allowed only under the terminal tangent semantics already defined.

## 19. Sample indexes

MotionSegmentResult samples shall have contiguous indexes:

0, 1, 2, ..., n - 1

The first MotionSample shall have:

sample_index = 0

Missing indexes are invalid.

Duplicate indexes are invalid.

Reordered indexes are invalid.

## 20. Result angle order

The requested_angle_deg values stored in MotionSample shall preserve the
processed input order.

For an INCREASING result they shall remain strictly increasing.

For a DECREASING result they shall remain strictly decreasing.

The result model shall not reorder samples by coordinate values or closure
state.

## 21. MotionSweepProvenance

MotionSweepProvenance shall contain:

engine = W40_BRANCH_PRESERVING_ANGLE_SWEEP

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

The empty Formula Registry and Calculation Record lists are intentional.

W40 continuous sequence construction is deterministic computational
infrastructure and does not create a new engineering formula identity.

## 22. MotionSegmentResult

MotionSegmentResult shall contain at least:

version = 1

direction: MotionDirection

reference_branch: ReferenceBranch

reference_angle_deg: DegreeParameter

requested_angle_count: positive integer

samples: list[MotionSample]

termination: MotionTermination

provenance: MotionSweepProvenance

The result does not require support_height_mm.

The result does not require top-beam geometry.

## 23. Reference result anchoring

MotionSegmentResult.samples[0] shall represent the reference angle.

Its requested_angle_deg value shall equal:

MotionSegmentResult.reference_angle_deg.value

The first sample shall be a valid TWO_SOLUTIONS selected pose on the frozen
reference branch.

W40-D2 does not allow a tangent-only first sample to masquerade as a
non-degenerate branch seed.

## 24. Requested versus processed samples

requested_angle_count records how many angles were requested by the sweep
input.

The actual number of samples records how many angles were processed before
completion or boundary termination.

The model shall require:

len(samples) <= requested_angle_count

For:

termination = COMPLETED

the model shall require:

len(samples) = requested_angle_count

For any boundary termination:

len(samples) <= requested_angle_count

and the boundary sample shall be the final processed sample.

## 25. COMPLETED result

A COMPLETED MotionSegmentResult means every requested angle was processed.

Every sample shall be:

TWO_SOLUTIONS

SELECTED

on the frozen reference branch.

A COMPLETED result shall not contain:

TANGENT

NO_SOLUTION

DEGENERATE

or:

BRANCH_AMBIGUOUS

## 26. TANGENT_BOUNDARY result

For:

termination = TANGENT_BOUNDARY

the final sample shall be exactly:

TANGENT

SELECTED

TANGENT_UNIQUE

All preceding samples shall be valid TWO_SOLUTIONS selected on the frozen
reference branch.

## 27. NO_SOLUTION_BOUNDARY result

For:

termination = NO_SOLUTION_BOUNDARY

the final sample shall be exactly:

NO_SOLUTION

with no selected pose.

All preceding samples shall be valid TWO_SOLUTIONS selected on the frozen
reference branch.

## 28. DEGENERATE_BOUNDARY result

For:

termination = DEGENERATE_BOUNDARY

the final sample shall be exactly:

DEGENERATE

with no selected pose.

All preceding samples shall be valid TWO_SOLUTIONS selected on the frozen
reference branch.

## 29. No post-boundary samples

No MotionSegmentResult may contain samples after:

TANGENT

NO_SOLUTION

or:

DEGENERATE

A boundary is therefore structurally terminal in the typed result.

This makes gap-and-resume invalid at the data-model layer.

## 30. W39 result preservation

MotionSample stores the complete W39 ClosureResult.

Therefore mathematical candidates remain available for auditing.

The W40 model shall not discard the unselected mathematical candidate from a
TWO_SOLUTIONS result.

W40 branch continuity is an engineering selection layer over the preserved
W39 mathematical solution set.

## 31. Input and result immutability

W40 model construction shall not mutate:

ClosureSolverInput

ClosureResult

DegreeParameter

or caller-supplied Python angle lists.

Strongly typed models shall own their validated representations without
silently editing the source objects.

## 32. Provenance boundary

W39 solved B/C coordinates retain:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

W40 MotionSweepProvenance also remains:

evidence_status = PARTIAL

Model validation does not promote geometry to VERIFIED.

## 33. Support-height boundary

No W40-D2 model shall require:

support_height_mm

No model validator shall infer support height from pivot coordinates.

The W38 PoseResult type is therefore not used as the authoritative W40
MotionSample model.

## 34. Top-beam and 80 mm boundary

W40-D2 does not model:

top-beam pose propagation

beam-tip trajectory

beam-tip horizontal displacement

or:

80 mm compliance

Those require later top-beam and operating-height semantics.

The W40 motion model shall not contain fake placeholder values for those
quantities.

## 35. D3 entry condition

After W40-D2 is implemented and validated, W40-D3 may implement:

sweep_rear_link_angles(...)

The D3 service shall:

1. consume MotionSweepInput
2. construct one new ClosureSolverInput per angle
3. call existing W39 solve_closure(...)
4. preserve the frozen reference branch
5. stop at the first tangent, no-solution, or degenerate boundary
6. never gap and resume
7. return one validated MotionSegmentResult

W40-D3 shall not modify W39 circle-intersection mathematics.

W40-D3 shall not introduce support-height solving.
