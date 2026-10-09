# W40-D1 Continuous Four-Bar Motion Semantics Closeout

## 1. Scope

W40-D1 freezes the semantic boundary for continuous deterministic four-bar
motion on top of the W39 single-pose solver.

The motion parameter remains:

rear_link_angle_deg

W40-D1 does not implement the sweep service.

W40-D1 does not redefine support_height_mm as the four-bar driving variable.

## 2. Motion-chain boundary

The first W40 continuous-motion chain is:

explicit non-degenerate engineering reference branch

-> ordered rear-link-angle samples

-> one existing W39 solve_closure(...) call per angle

-> branch-preserving selected poses

-> continuous B/C pivot trajectory

W39 remains authoritative for every individual closure calculation.

## 3. Branch seed

A continuous W40 motion segment requires a non-degenerate reference branch:

POSITIVE

or:

NEGATIVE

A null reference branch does not seed a continuous branch-tracked trajectory.

A single TANGENT pose may remain valid in W39, but does not independently
define which non-degenerate branch shall continue beyond that tangent.

W40 does not guess the branch.

## 4. Sweep ordering

The future sweep input shall be:

- finite
- ordered
- strictly monotonic
- explicitly increasing or decreasing

Duplicate consecutive angles are invalid.

Input order represents motion direction.

The reference angle shall be explicitly represented.

## 5. Frozen mechanism during one sweep

One continuous sweep keeps fixed:

- A rear-link base
- D front-link base
- AB rear-link length
- BC shield-beam effective linkage length
- CD front-link length
- DA base-pivot spacing
- NumericalTolerance
- engineering reference branch

Only rear_link_angle_deg changes between samples.

Rigid-link geometry does not silently change during the motion segment.

## 6. Branch continuity

For normal TWO_SOLUTIONS samples:

selection_status = SELECTED

selected_pose != null

selected_pose.branch = frozen reference branch

branch_resolution = REFERENCE_POSE

A POSITIVE trajectory shall not silently become NEGATIVE.

A NEGATIVE trajectory shall not silently become POSITIVE.

Candidate list position is not a continuity rule.

Coordinate preference is not a continuity rule.

Visual appearance is not a continuity rule.

## 7. Tangent boundary

TANGENT remains mathematically unique:

selection_status = SELECTED

selected_pose.branch = TANGENT

branch_resolution = TANGENT_UNIQUE

A tangent may be retained as a terminal boundary pose.

It does not authorize automatic branch switching.

W40-D1 therefore freezes tangent crossing as a stop boundary rather than an
implicit POSITIVE/NEGATIVE transition.

## 8. Unreachable and degenerate boundaries

NO_SOLUTION terminates the current sweep direction.

DEGENERATE terminates the current sweep direction.

Neither state creates a trajectory pose.

W40 does not skip an invalid sample and resume the same continuous segment at
a later angle.

A later restart would require a separately defined motion segment.

## 9. Continuity meaning

W40-D1 does not invent a maximum allowed coordinate jump between adjacent
samples.

Current continuity is established by:

- ordered angle progression
- fixed rigid-link geometry
- frozen engineering branch
- deterministic W39 solving
- no invalid gap-and-resume behavior

No unsupported engineering displacement threshold is introduced.

## 10. Provenance boundary

Solved W40 B/C points continue to inherit the W39 deterministic provenance:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

Sequence construction does not promote values to VERIFIED.

W40-D1 introduces no Formula Registry ID.

W40-D1 creates no Calculation Record.

## 11. Existing W38 result containers

The current W38 PoseResult requires support_height_mm.

W40-D1 does not yet have a deterministic support-height-to-pose relation.

Therefore support_height_mm shall not be fabricated merely to populate
PoseResult.

The current TrajectoryResults model primarily reserves later outputs such as
beam-tip and top-beam-joint trajectories.

It is not yet the strongly typed W40 angle-sweep model.

## 12. Top-beam gap

The current top_beam_interface contains reference-pose coordinates for:

shield_top_beam_pivot

beam_tip_reference_point

Those points alone do not freeze a complete rigid-body propagation model.

The project still lacks frozen semantics for:

- top-beam local coordinate frame
- shield-to-top-beam attachment transform
- top-beam / shield-beam joint offset in the top-beam frame
- deterministic beam-tip propagation to a new mechanism pose

W40-D1 therefore does not calculate a beam-tip trajectory.

Historical canopy_len is not used to fill the missing geometry.

## 13. 80 mm boundary

The project retains the standard-derived requirement that beam-tip horizontal
displacement over the support operating-height range shall not exceed 80 mm.

W40-D1 keeps this as a validation boundary.

It does not claim compliance.

An arbitrary rear-link-angle sweep is not equivalent to the complete
operating-height range.

Executable 80 mm validation requires both:

- deterministic top-beam / beam-tip propagation
- explicit operating-height-to-pose semantics

## 14. Support-height boundary

W40-D1 does not infer support_height_mm from:

- B.y
- C.y
- top-beam joint y
- beam-tip y
- maximum pivot elevation
- historical example heights

Existing operating_height_min_mm and operating_height_max_mm remain
engineering boundaries, not rear-link-angle bounds.

## 15. D2 entry condition

W40-D2 may introduce a dedicated strongly typed motion model.

The model should represent:

- reference branch
- ordered rear-link-angle samples
- sweep direction
- per-sample closure state
- selected B/C coordinates when available
- selected branch
- termination state
- termination reason
- NumericalTolerance
- provenance boundary

The W40 motion model shall not require fabricated support_height_mm.

## 16. Validation status

W40-D1 tests validate the semantic contract only.

They do not validate:

- a real hydraulic-support motion range
- top-beam rigid-body behavior
- support-height mapping
- beam-tip trajectory
- 80 mm compliance

Those capabilities require later deterministic geometry and engineering
evidence.
