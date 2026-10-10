# W40-D3 Branch-Preserving Rear-Link-Angle Sweep Contract

## 1. Objective

W40-D3 implements deterministic one-direction continuous four-bar motion on
top of:

W39 solve_closure(...)

and:

W40-D2 strongly typed motion models.

Target implementation:

app/services/linkage_motion.py

Primary public operation:

sweep_rear_link_angles(
    sweep: MotionSweepInput
) -> MotionSegmentResult

W40-D3 does not change W39 closure mathematics.

W40-D3 does not redefine support_height_mm as a motion variable.

## 2. Input authority

The service shall consume exactly one:

MotionSweepInput

The authoritative frozen mechanism is:

sweep.reference_task

The authoritative requested angle order is:

sweep.angle_samples_deg

The authoritative motion direction is:

sweep.direction

The authoritative engineering branch is:

sweep.reference_task.reference_branch

W40-D3 shall not infer a different branch from later coordinates.

## 3. One W39 solve per processed angle

For every processed requested angle, W40-D3 shall call the existing:

solve_closure(...)

exactly once.

The service shall not independently call:

solve_closure_candidates(...)

and then separately resolve the branch.

The existing integrated W39 single-pose solver remains authoritative.

## 4. Per-angle task construction

For every requested angle, W40-D3 shall construct a newly validated:

ClosureSolverInput

from the frozen reference task.

The per-angle task shall preserve:

- rear_link_base
- front_link_base
- rear_link_length_mm
- shield_beam_effective_length_mm
- front_link_length_mm
- base_pivot_spacing_mm
- reference_branch
- NumericalTolerance

Only:

rear_link_angle_deg

shall change.

The new rear_link_angle_deg shall be the corresponding requested
DegreeParameter.

W40-D3 shall not mutate the original reference_task.

## 5. Validated reconstruction requirement

Per-angle ClosureSolverInput construction shall pass through normal Pydantic
validation.

W40-D3 shall not use an unchecked update mechanism to bypass
ClosureSolverInput validation.

The service may serialize/copy the reference task and then call:

ClosureSolverInput.model_validate(...)

or use an equivalent fully validating construction path.

## 6. Reference sample

The first requested angle is already guaranteed by MotionSweepInput to equal
the reference task rear-link angle.

W40-D3 shall solve that first angle normally through W39.

The first result shall be:

TWO_SOLUTIONS

SELECTED

selected_pose != null

selected_pose.branch = frozen reference branch

branch_resolution = REFERENCE_POSE

If the first solved sample is not a valid non-degenerate selected reference
pose, W40-D3 shall fail explicitly.

It shall not return a successful motion segment beginning at a tangent,
no-solution, degenerate, or ambiguous state.

## 7. Normal interior sample

For every normal processed sample after the reference:

closure_state = TWO_SOLUTIONS

selection_status = SELECTED

selected_pose != null

selected_pose.branch = frozen reference branch

branch_resolution = REFERENCE_POSE

The resulting MotionSample shall preserve the complete ClosureResult.

## 8. MotionSample construction

Each processed requested angle shall create exactly one MotionSample.

Its:

sample_index

shall equal its zero-based processed sequence position.

Its:

requested_angle_deg

shall preserve the corresponding input DegreeParameter.

Its:

closure_result

shall be the complete result returned by W39 solve_closure(...).

W40-D3 shall not discard the unselected mathematical candidate.

## 9. COMPLETED termination

If every requested angle is processed and every result is a normal selected
TWO_SOLUTIONS pose on the frozen reference branch, the service shall return:

termination = COMPLETED

requested_angle_count shall equal the number of requested angles.

len(samples) shall equal requested_angle_count.

## 10. TANGENT termination

If a processed angle returns:

closure_state = TANGENT

then that tangent result shall be appended as the final MotionSample.

The service shall immediately terminate with:

termination = TANGENT_BOUNDARY

No later requested angle shall be solved.

The tangent sample remains:

SELECTED

TANGENT

TANGENT_UNIQUE

W40-D3 shall not automatically continue onto the opposite branch.

## 11. NO_SOLUTION termination

If a processed angle returns:

closure_state = NO_SOLUTION

that result shall be appended as the final attempted MotionSample.

The service shall immediately terminate with:

termination = NO_SOLUTION_BOUNDARY

No later requested angle shall be solved.

The boundary sample has no selected pose.

## 12. DEGENERATE termination

If a processed angle returns:

closure_state = DEGENERATE

that result shall be appended as the final attempted MotionSample.

The service shall immediately terminate with:

termination = DEGENERATE_BOUNDARY

No later requested angle shall be solved.

The boundary sample has no selected pose.

## 13. Unexpected branch ambiguity

If W39 returns:

TWO_SOLUTIONS

with:

selection_status = BRANCH_AMBIGUOUS

W40-D3 shall raise an explicit error.

It shall not convert ambiguity into a normal MotionTermination.

It shall not select the first candidate.

It shall not select by coordinate proximity alone.

## 14. Unexpected opposite branch

If a TWO_SOLUTIONS result contains a selected pose whose branch does not equal
the frozen reference branch, W40-D3 shall fail explicitly.

It shall not rewrite the result.

It shall not silently accept the opposite branch.

The W40-D2 model remains the final structural guard, but D3 shall also detect
the inconsistency at the service boundary.

## 15. No gap and resume

After the first:

TANGENT

NO_SOLUTION

or:

DEGENERATE

W40-D3 shall stop processing the requested angle list.

It shall not call solve_closure(...) for later angles.

A later mathematically solvable angle does not belong to the same continuous
motion segment.

## 16. Requested count semantics

MotionSegmentResult.requested_angle_count shall always equal:

len(sweep.angle_samples_deg)

even when boundary termination occurs early.

Therefore:

requested_angle_count

records requested work,

while:

len(samples)

records processed work.

## 17. Direction preservation

W40-D3 shall preserve:

sweep.direction

unchanged in MotionSegmentResult.

The service shall not reverse, sort, or normalize the requested angle list.

The validated input order is already the intended physical sweep direction.

## 18. Reference branch preservation

MotionSegmentResult.reference_branch shall equal:

sweep.reference_task.reference_branch

MotionSegmentResult.reference_angle_deg shall equal:

sweep.reference_task.rear_link_angle_deg

The service shall not recalculate either value from later samples.

## 19. Provenance

The returned MotionSegmentResult shall use:

MotionSweepProvenance

with:

engine = W40_BRANCH_PRESERVING_ANGLE_SWEEP

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

W40-D3 introduces no Formula Registry ID.

W40-D3 creates no Calculation Record.

## 20. Source immutability

W40-D3 shall not mutate:

MotionSweepInput

ClosureSolverInput reference_task

input DegreeParameter angle objects

or any W39 ClosureResult returned by solve_closure(...).

The input serialization shall remain unchanged after successful or
boundary-terminated execution.

## 21. Determinism

For identical validated MotionSweepInput values, repeated execution shall
produce equal MotionSegmentResult values.

There shall be no:

- random branch choice
- timestamp-dependent result field
- candidate-order-dependent branch decision
- hidden mutable solver state

## 22. No support-height solving

W40-D3 shall not calculate:

support_height_mm

It shall not populate the legacy W38 PoseResult container.

It shall not infer height from:

- B.y
- C.y
- maximum pivot elevation
- reference support_height_mm
- operating-height limits

The D3 output remains angle-parameterized motion.

## 23. No top-beam propagation

W40-D3 shall not calculate:

shield_top_beam_pivot trajectory

top_beam_pose

beam_tip_trajectory

beam_tip_horizontal_displacement

or:

80 mm validation

Those remain later W40 work after the required geometry semantics are frozen.

## 24. No interpolation

W40-D3 solves only the explicitly requested angle samples.

It shall not automatically insert intermediate angles.

It shall not interpolate missing B/C coordinates.

Adaptive subdivision may be considered later only under a separate frozen
contract.

## 25. No artificial continuity threshold

W40-D3 shall not reject a mathematically valid adjacent pose merely because B
or C displacement exceeds an invented threshold.

Current continuity semantics remain:

- ordered monotonic angle sequence
- fixed rigid-link geometry
- frozen engineering branch
- deterministic W39 closure
- immediate stop at mathematical boundary

No unsupported maximum step-distance rule is introduced.

## 26. D3 validation target

W40-D3 tests shall cover at least:

- completed increasing sweep
- completed decreasing sweep
- POSITIVE branch preservation
- NEGATIVE branch preservation
- reference sample solving
- one W39 solve per processed sample
- tangent boundary termination
- no-solution boundary termination
- degenerate boundary termination
- no solver calls after a boundary
- explicit rejection of ambiguous TWO_SOLUTIONS
- explicit rejection of opposite selected branch
- preservation of complete W39 candidates
- requested versus processed counts
- source immutability
- deterministic repeated execution
- absence of support-height and top-beam calculations

## 27. D4 entry boundary

After W40-D3 is complete, the project will possess deterministic continuous:

B trajectory

and:

C trajectory

parameterized by rear_link_angle_deg.

W40-D4 shall then audit and freeze the missing top-beam kinematic semantics
before any beam-tip propagation is implemented.

W40-D4 shall not assume that two stored reference-pose top-beam points are
sufficient to define the complete rigid-body propagation model.
