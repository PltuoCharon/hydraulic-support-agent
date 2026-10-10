# W40-D3 Branch-Preserving Angle Sweep Closeout

## 1. Scope

W40-D3 implements deterministic one-direction continuous four-bar motion.

Implementation:

app/services/linkage_motion.py

Public operation:

sweep_rear_link_angles(
    sweep: MotionSweepInput
) -> MotionSegmentResult

W40-D3 executes the motion semantics frozen in W40-D1 and the strongly typed
models implemented in W40-D2.

W40-D3 does not implement support-height solving or top-beam propagation.

## 2. Execution chain

The implemented chain is:

MotionSweepInput

-> validated per-angle ClosureSolverInput

-> existing W39 solve_closure(...)

-> complete ClosureResult

-> MotionSample

-> boundary-aware processing

-> MotionSegmentResult

W39 remains authoritative for every individual four-bar pose.

## 3. Per-angle task reconstruction

For every requested angle, D3 constructs a new ClosureSolverInput.

The frozen reference task supplies:

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

changes between samples.

Per-angle task construction passes through:

ClosureSolverInput.model_validate(...)

D3 intentionally does not use unchecked:

model_copy(update=...)

for the angle replacement.

## 4. Existing W39 solver reuse

Each processed requested angle calls:

solve_closure(...)

exactly once.

D3 does not separately execute:

solve_closure_candidates(...)

D3 does not implement another circle-intersection algorithm.

D3 does not implement another branch-selection algorithm.

## 5. Reference sample

The first requested angle is solved normally through W39.

A valid D3 reference sample shall be:

TWO_SOLUTIONS

SELECTED

selected_pose != null

selected_pose.branch = frozen reference branch

branch_resolution = REFERENCE_POSE

D3 rejects a motion segment whose first solved sample is tangent, unreachable,
degenerate, or ambiguous.

## 6. Normal motion sample

Every normal interior sample remains:

TWO_SOLUTIONS

SELECTED

selected on the frozen engineering reference branch.

The complete ClosureResult is preserved inside MotionSample.

The unselected mathematical candidate is not discarded.

## 7. POSITIVE branch continuity

For a POSITIVE motion segment, every non-boundary TWO_SOLUTIONS sample shall
remain selected on:

POSITIVE

D3 explicitly rejects an opposite selected branch.

## 8. NEGATIVE branch continuity

For a NEGATIVE motion segment, every non-boundary TWO_SOLUTIONS sample shall
remain selected on:

NEGATIVE

D3 explicitly rejects an opposite selected branch.

## 9. Tangent boundary

When W39 returns:

TANGENT

D3 appends that result as the final processed MotionSample.

It returns:

termination = TANGENT_BOUNDARY

The tangent sample preserves:

selection_status = SELECTED

selected_pose.branch = TANGENT

branch_resolution = TANGENT_UNIQUE

No later requested angle is solved.

D3 does not automatically cross the tangent onto another branch.

## 10. No-solution boundary

When W39 returns:

NO_SOLUTION

D3 appends that result as the final attempted MotionSample.

It returns:

termination = NO_SOLUTION_BOUNDARY

The boundary sample has no selected pose.

No later requested angle is solved.

## 11. Degenerate boundary

When W39 returns:

DEGENERATE

D3 appends that result as the final attempted MotionSample.

It returns:

termination = DEGENERATE_BOUNDARY

The boundary sample has no selected pose.

No later requested angle is solved.

## 12. Ambiguous result handling

An interior:

TWO_SOLUTIONS + BRANCH_AMBIGUOUS

is treated as a service-layer error.

D3 does not convert ambiguity into a motion termination.

D3 does not select the first mathematical candidate.

D3 does not select by coordinate proximity or visual preference.

## 13. No gap and resume

After the first:

TANGENT

NO_SOLUTION

or:

DEGENERATE

the sweep immediately stops.

Later requested angles are not passed to solve_closure(...).

A mathematically solvable later angle is therefore not silently attached to the
same continuous motion segment.

## 14. Requested and processed counts

MotionSegmentResult.requested_angle_count always records:

len(sweep.angle_samples_deg)

The number of MotionSample entries records how many requested angles were
actually processed.

For:

COMPLETED

the counts are equal.

For boundary termination, the processed count may be smaller than the requested
count.

## 15. Input ordering

D3 preserves the validated input angle order.

It does not:

- sort angles
- reverse angles
- insert intermediate angles
- interpolate missing poses

The caller's validated order remains the intended sweep direction.

## 16. Motion metadata

The result preserves:

direction = sweep.direction

reference_branch = sweep.reference_task.reference_branch

reference_angle_deg = sweep.reference_task.rear_link_angle_deg

These values are not recalculated from later samples.

## 17. Motion provenance

The result uses:

engine = W40_BRANCH_PRESERVING_ANGLE_SWEEP

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

W40-D3 introduces no Formula Registry ID.

W40-D3 creates no Calculation Record.

## 18. Source immutability

Successful and boundary-terminated sweeps do not mutate MotionSweepInput.

They do not mutate:

- the reference ClosureSolverInput
- caller-supplied DegreeParameter objects
- W39 results returned by solve_closure(...)

## 19. Determinism

Repeated execution with identical MotionSweepInput produces equal
MotionSegmentResult values.

There is no random branch choice.

There is no candidate-index branch selection.

There is no timestamp-dependent motion result.

## 20. Continuous B/C trajectory capability

For every selected trajectory sample, the complete W39 selected pose contains:

rear_link_shield = B

front_link_shield = C

Therefore W40-D3 now provides deterministic ordered B and C trajectories
parameterized by rear_link_angle_deg.

The trajectory remains an angle-parameterized mechanism trajectory.

It is not yet an operating-height trajectory.

## 21. Support-height boundary

W40-D3 does not calculate:

support_height_mm

It does not infer height from B.y, C.y, or any other pivot coordinate.

It does not populate the W38 PoseResult type.

No operating-height coverage claim is made.

## 22. Top-beam boundary

W40-D3 does not calculate:

- shield_top_beam_pivot trajectory
- top_beam_pose
- beam_tip_trajectory
- beam_tip_horizontal_displacement
- 80 mm validation

Those require additional top-beam kinematic semantics.

## 23. No artificial continuity threshold

D3 does not introduce an arbitrary maximum B/C displacement between adjacent
angle samples.

Current continuity is defined through:

- strict ordered angle progression
- frozen rigid-link geometry
- frozen engineering branch
- deterministic W39 solving
- immediate mathematical-boundary termination

No unsupported engineering jump threshold is added.

## 24. Automated validation achieved

W40-D3 tests establish:

- completed INCREASING POSITIVE sweep
- completed DECREASING NEGATIVE sweep
- reference-pose solving
- only rear_link_angle_deg changes per task
- new validated task per angle
- exactly one W39 solve per processed angle
- preservation of requested DegreeParameter data
- tangent terminal behavior
- requested-count preservation after tangent
- no-solution terminal behavior
- degenerate terminal behavior
- no solver calls after a tangent
- explicit ambiguous-result rejection
- explicit opposite-branch rejection
- invalid tangent reference rejection
- complete W39 candidate preservation
- direction/reference metadata preservation
- frozen motion provenance
- source immutability
- deterministic repeated execution
- absence of support-height/top-beam output
- solving only explicitly requested angles

These are deterministic software-level guarantees.

They are not physical certification of a real support mechanism.

## 25. D4 entry condition

W40-D3 now supplies deterministic ordered B/C trajectories.

W40-D4 shall next audit and freeze the top-beam kinematic relationship needed
to propagate:

shield_top_beam_pivot

and eventually:

beam_tip_reference_point

from the reference pose to subsequent mechanism poses.

D4 shall determine whether the current project contains enough explicit
engineering geometry to define that rigid-body propagation.

If the required transform or attachment geometry is absent, D4 shall preserve
the missing information as an explicit engineering-geometry gap rather than
fabricate it.
