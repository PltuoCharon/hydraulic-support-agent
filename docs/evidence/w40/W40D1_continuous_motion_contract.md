# W40-D1 Continuous Four-Bar Motion Contract

## 1. Objective

W40 begins continuous deterministic kinematics on top of the frozen W39
single-pose four-bar solver.

W40-D1 freezes the semantics for a continuous single-branch angle sweep.

The W40-D1 driving variable remains:

rear_link_angle_deg

W40-D1 does not redefine support_height_mm as the four-bar driving variable.

The first W40 motion chain is:

explicit non-degenerate W39 reference branch

-> ordered rear-link-angle samples

-> one W39 closure solve per angle

-> branch-preserving selected poses

-> continuous B/C pivot trajectory

W40-D1 defines semantics only.

It does not yet implement the sweep service.

## 2. Why angle-driven motion comes first

W39 already establishes a deterministic map:

rear_link_angle_deg

-> mathematical closure

-> engineering branch selection

No deterministic project relation currently establishes:

support_height_mm

-> four-bar pose

Therefore W40 shall first construct continuous motion in the already frozen
rear-link-angle parameter space.

Support-height mapping may be introduced only after its geometric semantics are
explicitly defined and tested.

## 3. Reference motion branch

A continuous W40 sweep requires one non-degenerate engineering branch seed.

The reference branch shall be exactly one of:

POSITIVE

NEGATIVE

The reference branch shall originate from the explicit W39 reference-pose
workflow.

A null reference branch is not sufficient to seed a continuous branch-tracked
trajectory.

A TANGENT-only reference configuration may remain valid as a W39 single pose,
but it shall not by itself define the W40 continuous branch seed.

W40 shall not guess a branch.

## 4. Sweep input

A W40 angle sweep shall consume an explicit ordered sequence of rear-link
angles.

Each angle shall be finite and expressed in degrees.

The sequence shall be strictly monotonic.

It may be:

strictly increasing

or:

strictly decreasing

Duplicate consecutive angles are invalid.

An unordered collection is invalid.

The input order represents intended motion direction.

## 5. Reference angle anchoring

The reference rear-link angle shall be explicitly represented in the sweep
definition.

The reference sample anchors the engineering branch.

W40 shall not infer an unknown reference angle from support_height_mm.

W40 shall not choose an arbitrary sweep element as the reference merely
because it is first in the list.

## 6. Geometry frozen during one sweep

Within one W40 sweep, the following shall remain constant:

rear_link_base A

front_link_base D

AB rear-link length

BC shield-beam effective linkage length

CD front-link length

DA base-pivot spacing

NumericalTolerance

reference branch

Only rear_link_angle_deg changes from sample to sample.

A motion sweep is not allowed to silently change rigid-link lengths between
samples.

## 7. Existing W39 solver remains authoritative

For each rear-link-angle sample, W40 shall construct a ClosureSolverInput that
preserves the frozen mechanism geometry and engineering reference branch.

W40 shall call the existing W39:

solve_closure(...)

for that sample.

W40 shall not implement a second circle-intersection solver.

W40 shall not implement a second branch-resolution algorithm.

W39 D3 and D4 remain authoritative for single-pose closure.

## 8. Normal continuous sample

The normal interior sample of a continuous branch-tracked trajectory is:

closure_state = TWO_SOLUTIONS

selection_status = SELECTED

selected_pose != null

selected_pose.branch = reference branch

branch_resolution = REFERENCE_POSE

The unselected mathematical candidate remains present in the underlying W39
ClosureResult.

W40 trajectory continuity shall not destroy mathematical solution information.

## 9. Branch continuity rule

For every non-tangent selected TWO_SOLUTIONS sample:

selected_pose.branch

shall equal the frozen sweep reference branch.

A POSITIVE sweep shall not silently select NEGATIVE.

A NEGATIVE sweep shall not silently select POSITIVE.

W40 shall never select by:

- candidate list index
- larger X
- smaller X
- larger Y
- smaller Y
- visual appearance
- nearest candidate without branch semantics

## 10. Tangent behavior

A TANGENT sample is mathematically unique.

It may be retained as a terminal boundary sample of a continuous sweep.

Its semantics remain:

closure_state = TANGENT

selection_status = SELECTED

selected_pose.branch = TANGENT

branch_resolution = TANGENT_UNIQUE

TANGENT does not authorize automatic switching from POSITIVE to NEGATIVE or
from NEGATIVE to POSITIVE.

After reaching a tangent boundary, W40-D1 continuity semantics shall stop that
sweep direction rather than silently crossing into another assembly branch.

## 11. Unreachable behavior

If a requested angle produces:

NO_SOLUTION

that sample marks an unreachable mathematical boundary.

W40 shall not fabricate a pose.

W40 shall not skip the failed sample and resume the same trajectory at a later
angle.

The continuous selected-pose sequence terminates in that sweep direction.

The unreachable sample may be recorded as a boundary/status result, but it is
not a valid trajectory pose.

## 12. Degenerate behavior

If a requested angle produces:

DEGENERATE

the continuous selected-pose sequence terminates in that sweep direction.

W40 shall not manufacture a finite C point from an infinite solution set.

W40 shall not continue the trajectory by choosing an arbitrary geometry.

## 13. Unexpected ambiguity

Because a W40 branch-tracked sweep requires a non-null reference branch, an
interior result of:

TWO_SOLUTIONS + BRANCH_AMBIGUOUS

is inconsistent with the W40 trajectory layer.

W40 shall fail explicitly rather than continue with an arbitrary candidate.

## 14. No gap-and-resume behavior

A single continuous trajectory shall contain one contiguous run of valid
selected poses.

After termination by:

NO_SOLUTION

DEGENERATE

or:

TANGENT boundary

the same sweep direction shall not resume later merely because another sampled
angle becomes mathematically solvable.

Any restarted segment must be represented as a new explicit motion segment with
its own validated reference semantics.

## 15. Coordinate continuity

The trajectory shall preserve the ordered solved coordinates:

B_i = rear_link_shield at sample i

C_i = front_link_shield at sample i

Successive coordinate differences may be calculated for diagnostics.

W40-D1 does not introduce an arbitrary maximum allowed B or C displacement per
sample.

No unverified engineering jump threshold shall be invented.

Mathematical continuity is established through:

- ordered angle progression
- fixed rigid-link geometry
- fixed non-degenerate engineering branch
- W39 deterministic solving
- no gap-and-resume behavior

## 16. Provenance

Every solved B/C point continues to use the provenance already frozen by W39:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

Sequence construction does not promote geometry to VERIFIED.

W40-D1 introduces no Formula Registry ID.

W40-D1 creates no Calculation Record.

## 17. Input immutability

A W40 sweep shall not mutate the source:

LinkageGeometry

ClosureSolverInput reference task

W39 reference result

or caller-supplied angle sequence.

Each sample shall be represented by newly constructed calculation objects.

## 18. Existing PoseResult boundary

The current W38 PoseResult model requires:

support_height_mm

W40-D1 does not yet possess a deterministic support-height-to-pose mapping.

Therefore W40 shall not populate PoseResult by inventing support_height_mm for
an angle-driven sample.

A dedicated W40 motion model shall be introduced before implementing the
continuous sweep.

## 19. Existing TrajectoryResults boundary

The current W38 TrajectoryResults model contains future slots such as:

beam_tip_trajectory

beam_tip_horizontal_displacement_mm

shield_top_beam_joint_trajectory

instantaneous_center_trajectory

It does not currently represent the full W40 angle-driven B/C trajectory
semantics.

W40-D1 shall not populate those future slots merely because the container
exists.

W40-D2 shall introduce explicit typed motion/sweep models.

## 20. Top-beam semantic gap

The current top_beam_interface stores reference-pose coordinates for:

shield_top_beam_pivot

beam_tip_reference_point

Those reference coordinates alone do not yet freeze:

- a top-beam local coordinate frame
- top-beam rigid-body pose semantics
- the attachment transform from the shield beam to the top beam
- the top-beam / shield-beam joint offset relative to a top-beam reference
  frame
- a deterministic rule for propagating the beam tip to a new four-bar pose

Therefore W40-D1 does not propagate top-beam or beam-tip coordinates.

Historical canopy_len shall not be used to fill this gap.

## 21. 80 mm validation boundary

The project retains the standard-derived requirement that the beam-tip
horizontal displacement of a support using a four-bar mechanism over its
operating-height range shall not exceed 80 mm.

The 80 mm value is a validation boundary.

It is not geometry.

W40-D1 cannot yet execute this standard validation because the project does not
yet have both:

1. a frozen deterministic top-beam / beam-tip propagation model
2. a frozen mapping between the generated continuous poses and the complete
   operating-height range

W40 shall not claim 80 mm compliance from an arbitrary rear-link-angle sweep.

## 22. Support-height boundary

W40-D1 does not calculate:

support_height_mm

for angle-driven samples.

It does not infer support height from:

- B.y
- C.y
- shield_top_beam_pivot.y
- beam_tip_reference_point.y
- maximum of pivot coordinates
- historical support height examples

Such mappings require explicit engineering semantics.

## 23. Operating-height boundaries

Existing:

operating_height_min_mm

and:

operating_height_max_mm

remain design/validation boundaries.

They shall not be converted into rear-link-angle limits without a verified
height-to-pose relation.

W40-D1 therefore does not claim that an arbitrary angle interval covers the
support's complete operating-height range.

## 24. W40-D2 entry condition

After W40-D1 contract freeze, W40-D2 may introduce a strongly typed motion
model, expected to represent at least:

- frozen sweep reference branch
- ordered angle samples
- motion direction
- per-sample closure state
- per-sample B/C coordinates when selected
- per-sample selected branch
- termination state
- termination reason
- explicit NumericalTolerance
- provenance boundary

The model shall not require support_height_mm until support-height semantics
exist.

## 25. Later W40 direction

After the typed motion model exists, later W40 work may implement:

W40-D3:
branch-preserving rear-link-angle sweep and B/C trajectories

W40-D4:
top-beam kinematic semantic/evidence contract

W40-D5:
top-beam and beam-tip propagation only if the required geometry and rigid-body
semantics are explicitly available

W40-D6:
trajectory closeout and executable validation only for constraints whose
required geometry and motion-domain semantics are actually available

If the prerequisites for MT/T 556 beam-tip validation remain incomplete,
W40-D6 shall preserve that item as an explicit evidence/geometry gap rather
than manufacture a result.

Continuous four-bar motion comes before optimization.
