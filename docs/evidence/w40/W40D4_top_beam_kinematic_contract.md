# W40-D4 Top-Beam Kinematic Semantics Contract

## 1. Objective

W40-D4 freezes the engineering and kinematic boundary between:

the solved four-bar shield-beam motion

and:

the later top-beam / beam-tip motion problem.

W40-D4 distinguishes four important points:

B = rear_link_shield

C = front_link_shield

E = shield_top_beam_pivot

T = beam_tip_reference_point

W40-D3 already supplies ordered deterministic B/C trajectories.

W40-D4 determines what can and cannot be propagated from those trajectories.

W40-D4 freezes semantics only.

It does not yet implement a propagation service.

## 2. Existing project evidence

The canonical four-bar mechanism contains:

- rear link
- front link
- shield beam
- base

The top-beam / shield-beam connection is outside that canonical four-bar.

Existing W38 TopBeamInterface contains only:

shield_top_beam_pivot

beam_tip_reference_point

These are reference-pose coordinates.

The existing project does not contain a complete top-beam rigid-body
kinematic model.

## 3. Shield beam as a rigid body

For W40 kinematics, the segment defined by:

B -> C

represents the directed shield-beam rigid-body reference axis.

Because the W39/W40 mechanism preserves BC as a rigid-link length, every
selected B/C pose defines the planar position and orientation of the shield
beam.

This is deterministic computational kinematics.

It is not new external engineering evidence.

## 4. E joint-center modeling convention

When an explicit reference:

shield_top_beam_pivot = E0

is supplied, W40 shall interpret E0 as the physical revolute-joint center
connecting the shield beam and top beam.

For propagation purposes, E is treated as a material point fixed in the rigid
shield beam.

This is a project kinematic modeling convention derived from the explicit
joint-center semantics.

It shall not be presented as independently VERIFIED geometry.

The numerical reference coordinate E0 retains its own original provenance.

## 5. E is conditional on explicit geometry

W40 shall propagate E only when:

shield_top_beam_pivot

is explicitly available.

If E0 is missing, the project shall report the shield/top-beam joint geometry
as unavailable.

W40 shall not derive E0 from:

- canopy_len
- historical beam_length
- roof_end_distance
- center_dist
- support_height_mm
- beam_tip_reference_point
- historical support examples

No zero/default coordinate shall replace missing E0.

## 6. Reference shield coordinate frame

For one non-degenerate reference pose:

B0 = rear_link_shield

C0 = front_link_shield

define:

L0 = |C0 - B0|

u0 = (C0 - B0) / L0

v0 = (-u0_y, u0_x)

where:

u0

is the unit vector along directed B0 -> C0,

and:

v0

is the +90 degree planar normal.

The reference shield frame origin is B0.

L0 shall be finite and strictly positive.

## 7. Local E coordinates

The explicit reference joint center E0 shall be converted into shield-frame
local coordinates:

s_E = dot(E0 - B0, u0)

n_E = dot(E0 - B0, v0)

The pair:

(s_E, n_E)

is the frozen local coordinate of E on the rigid shield beam.

Units are millimetres.

No rounding is applied.

## 8. Propagation to one selected pose

For one later selected pose:

Bi = rear_link_shield

Ci = front_link_shield

define:

Li = |Ci - Bi|

ui = (Ci - Bi) / Li

vi = (-ui_y, ui_x)

The propagated shield/top-beam joint center is:

Ei = Bi + s_E * ui + n_E * vi

This is a planar rigid-body transform.

It does not determine top-beam orientation.

## 9. Directed-frame convention

The local frame is based on directed:

B -> C

not:

C -> B

The service shall not flip the axis based on coordinate magnitude.

It shall not choose orientation from:

- larger X
- larger Y
- visual appearance
- candidate ordering

Using a directed B -> C frame preserves a deterministic local-frame
orientation across the branch-preserving W40 trajectory.

## 10. Reference round-trip invariant

At the first motion sample, propagation using:

B0

C0

s_E

n_E

shall reproduce the explicit:

E0

within the explicit numerical tolerance.

Failure of this round trip indicates inconsistent input or implementation.

W40 shall not loosen tolerance merely to force the reference round trip to
pass.

## 11. Motion/reference consistency

The first selected B/C pose of the supplied W40 motion segment shall correspond
to the same reference geometry used to define E0.

The service shall verify that the motion reference B/C agrees with the
LinkageGeometry reference B/C within numerical tolerance.

W40 shall not derive an attachment from one reference mechanism and apply it
silently to another mechanism.

## 12. Rigid-body invariants

For every propagated selected pose, the local coordinates of E relative to the
directed shield frame shall remain:

s_E

n_E

Therefore rigid-body propagation preserves the geometric relation between:

B

C

and:

E

No independent drift of E relative to the shield beam is allowed.

## 13. Valid motion samples

E may be propagated for every MotionSample that contains a selected pose.

This includes normal:

TWO_SOLUTIONS + SELECTED

samples.

A terminal:

TANGENT + SELECTED

sample also has a unique B/C pose and may therefore receive a propagated E
point.

## 14. Unsolved boundary samples

A terminal:

NO_SOLUTION

sample has no selected B/C pose.

Therefore it has no propagated E coordinate.

A terminal:

DEGENERATE

sample has no selected B/C pose.

Therefore it has no propagated E coordinate.

W40 shall not fabricate E for unsolved boundary samples.

## 15. E propagation does not solve T

Knowing:

Bi

Ci

and:

Ei

does not uniquely determine:

Ti = beam_tip position.

The top beam is not frozen as rigidly locked to the shield beam.

W40 shall not propagate T using the shield-beam rotation alone.

In particular, W40 shall not use:

Ti = rigid_transform_of_reference_T_with_BC

unless an independent future contract explicitly proves that such a rigid lock
is appropriate for the target support configuration.

## 16. Independent top-beam orientation

Existing engineering evidence requires the top beam to support different
pitch attitudes over the support height range.

The project evidence also identifies the balance jack as participating in
meeting those top-beam attitude requirements.

Therefore the top-beam orientation relative to the shield beam shall be treated
as an independently constrained kinematic quantity until a deterministic
relation is supplied.

W40-D4 does not define that relation.

## 17. Balance-jack geometry gap

The current project does not contain the geometry required to solve top-beam
orientation from a balance jack.

The missing kinematic information includes, depending on the target
architecture, items such as:

- balance-jack shield-side pivot
- balance-jack top-beam-side pivot
- effective jack length for a pose
- stroke limits
- installation offsets
- explicit relation between jack length and top-beam angle

Merely knowing that a balance jack exists is insufficient.

## 18. Other acceptable future top-beam constraints

A future deterministic top-beam pose model may be supplied by one or more
explicit engineering inputs such as:

- top-beam angle for each mechanism pose
- balance-jack installation geometry plus jack length
- a second independent top-beam geometry point
- a verified top-beam pose law
- a complete model-specific assembly drawing
- an independently validated generated assembly

W40 shall not invent one of these constraints.

## 19. Beam-tip reference point boundary

beam_tip_reference_point = T0

may remain stored as an explicit reference-pose coordinate.

T0 alone defines only one point in one pose.

It does not define the future top-beam rotation law.

Therefore T0 alone is insufficient for a deterministic beam-tip trajectory.

## 20. Historical geometry remains forbidden

Historical:

canopy_len

beam_length

roof_end_distance

or generic support-part presence

shall not be converted into:

- top-beam length
- E local offset
- T local offset
- balance-jack installation geometry
- top-beam angle law

Missing top-beam geometry remains missing.

## 21. Support-height boundary

W40-D4 does not create:

support_height_mm

for the W40 angle-driven trajectory.

It does not infer support height from E.y or T.y.

The operating-height mapping remains a separate unresolved relationship.

## 22. 80 mm validation remains blocked

The project retains the MT/T 556 beam-tip horizontal-displacement limit:

80 mm

over the support operating-height range.

W40-D4 does not execute that validation.

Executable 80 mm validation requires at least:

1. a deterministic beam-tip trajectory
2. a deterministic mapping to the complete operating-height range

Neither requirement is completed by E propagation alone.

## 23. Numerical tolerance

All reference consistency and rigid-transform round-trip checks shall use an
explicit NumericalTolerance.

No hidden geometric tolerance is introduced.

Distance comparisons use millimetres.

## 24. Provenance

Reference E0 preserves its supplied engineering provenance.

Propagated Ei coordinates shall use:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

The rigid transform does not promote the original geometry to VERIFIED.

W40-D4 introduces no Formula Registry ID.

W40-D4 creates no Calculation Record.

## 25. Existing TrajectoryResults boundary

The legacy:

TrajectoryResults.shield_top_beam_joint_trajectory

is a future-result slot.

Its existence does not itself define the W40-D4 kinematic semantics.

W40 shall not populate that legacy slot until a typed propagation result
preserves:

- motion sample index
- requested angle
- selected-pose availability
- terminal boundary semantics
- provenance

A dedicated typed D5 result is preferred.

## 26. Input immutability

Future E propagation shall not mutate:

LinkageGeometry

MotionSegmentResult

reference B/C/E points

or existing W39/W40 motion samples.

Propagation outputs shall be newly constructed calculated objects.

## 27. What W40-D4 establishes

W40-D4 establishes that:

B/C trajectory
-> shield rigid-body pose
-> E trajectory

is deterministically modelable when explicit E0 is available.

W40-D4 also establishes that:

B/C/E trajectory
-> top-beam orientation
-> T trajectory

is not yet uniquely solvable from current project geometry.

These two capability levels shall not be conflated.

## 28. D5 entry condition

W40-D5 may implement typed shield/top-beam joint propagation based on the
frozen B/C/E rigid-body transform.

D5 shall not yet claim a deterministic beam-tip trajectory unless additional
top-beam orientation constraints become available.

If those constraints remain unavailable, D5 shall return only the deterministic
E trajectory and preserve the T/top-beam gap explicitly.

## 29. D6 direction

W40-D6 shall close the W40 trajectory stage.

If top-beam orientation and operating-height mapping remain unresolved, D6
shall explicitly report:

beam-tip trajectory = NOT EXECUTABLE

80 mm validation = NOT EXECUTABLE

because required engineering geometry is missing.

That is a valid engineering closeout result.

Missing evidence shall not be replaced with fabricated geometry.
