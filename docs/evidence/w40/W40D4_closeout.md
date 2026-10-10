# W40-D4 Top-Beam Kinematic Semantics Closeout

## 1. Scope

W40-D4 audits and freezes the kinematic boundary between the solved four-bar
shield-beam motion and the later top-beam / beam-tip problem.

W40-D4 is a semantics and engineering-boundary stage.

It does not implement a propagation service.

The relevant points are:

B = rear_link_shield

C = front_link_shield

E = shield_top_beam_pivot

T = beam_tip_reference_point

## 2. Four-bar boundary

The canonical four-bar remains:

- base
- rear link
- shield beam
- front link

The top-beam / shield-beam joint is outside the canonical four-bar.

W40-D3 already provides deterministic ordered B/C trajectories.

Those trajectories determine the planar pose of the shield beam.

## 3. Shield rigid-body semantics

The directed segment:

B -> C

is frozen as the shield-beam rigid-body reference axis.

For each selected mechanism pose, B and C determine:

- shield-beam position
- shield-beam orientation

The direction is always:

B -> C

It is not selected by coordinate magnitude or visual appearance.

## 4. E semantics

An explicitly supplied:

shield_top_beam_pivot = E0

is interpreted as the physical revolute-joint center between the shield beam
and the top beam.

For W40 kinematics, E is treated as a material point fixed in the shield-beam
rigid body.

This is a project kinematic modeling convention based on the explicit
joint-center semantics.

It is not an independently verified new engineering dimension.

The numerical reference E0 retains its supplied provenance.

## 5. Missing E behavior

E propagation is permitted only when an explicit E0 is available.

Missing E0 shall remain missing.

W40 shall not derive E from:

- canopy_len
- beam_length
- roof_end_distance
- center_dist
- support_height_mm
- beam_tip_reference_point
- historical example geometry

No zero or historical default shall replace missing E.

## 6. Reference shield frame

For reference points:

B0

C0

define:

L0 = |C0 - B0|

u0 = (C0 - B0) / L0

v0 = (-u0_y, u0_x)

The frame origin is B0.

The frame orientation is explicitly derived from directed:

B0 -> C0

L0 must be finite and strictly positive.

## 7. E local coordinates

The explicit reference joint center E0 is represented in the shield frame by:

s_E = dot(E0 - B0, u0)

n_E = dot(E0 - B0, v0)

These local coordinates remain constant under rigid-body motion of the shield
beam.

## 8. Deterministic E propagation

For one later selected B/C pose:

Bi

Ci

define:

Li = |Ci - Bi|

ui = (Ci - Bi) / Li

vi = (-ui_y, ui_x)

Then:

Ei = Bi + s_E * ui + n_E * vi

This gives the deterministic propagated shield/top-beam joint center.

It is a planar rigid-body transformation.

## 9. Reference round trip

Using reference:

B0

C0

E0

the frozen local coordinates:

s_E

n_E

shall reproduce E0 within the explicit numerical tolerance.

A failed round trip indicates inconsistent geometry or implementation.

Tolerance shall not be widened merely to make the check pass.

## 10. Reference-mechanism consistency

The B/C reference pose used to derive the E attachment shall correspond to the
same mechanism as the W40 motion segment.

A future propagation service shall verify reference B/C consistency within the
explicit NumericalTolerance.

An E attachment derived from one mechanism shall not be silently reused on a
different reference mechanism.

## 11. Valid E trajectory samples

E may be propagated whenever a MotionSample contains a selected B/C pose.

Normal:

TWO_SOLUTIONS + SELECTED

samples therefore support E propagation.

Terminal:

TANGENT + SELECTED

also provides a unique B/C pose and may support one final E coordinate.

## 12. Unsolved motion boundaries

Terminal:

NO_SOLUTION

has no selected B/C pose and therefore no propagated E.

Terminal:

DEGENERATE

has no selected B/C pose and therefore no propagated E.

W40 shall not fabricate an E point for an unsolved sample.

## 13. E does not determine T

A known:

B

C

E

pose does not uniquely determine:

T

because the top beam is not frozen as rigidly locked to the shield beam.

W40 shall not rotate the reference beam-tip point with the shield beam and call
the result a physical beam-tip trajectory.

The transformation:

reference T -> shield rigid transform -> Ti

is currently forbidden as an engineering assumption.

## 14. Independent top-beam degree of freedom

The stored MT/T 556 evidence requires the top beam to support different pitch
attitudes at different support heights.

The same evidence associates the balance jack with achieving those attitude
requirements.

Therefore top-beam pitch relative to the shield beam is an independently
constrained kinematic quantity.

W40-D4 does not define that missing relation.

## 15. Balance-jack gap

The project currently records the existence of a balance jack but does not
contain enough model-specific kinematic geometry to solve top-beam orientation.

Missing items include, as applicable:

- shield-side balance-jack pivot
- top-beam-side balance-jack pivot
- effective jack length
- stroke boundary
- installation offsets
- relation between jack length and top-beam angle

Component existence alone is insufficient.

## 16. Other future top-beam constraints

A deterministic future top-beam model may instead use explicit engineering
information such as:

- top-beam angle per mechanism pose
- balance-jack installation geometry and length
- a second top-beam geometry constraint
- verified pose law
- model-specific assembly drawing
- independently validated generated assembly

No such constraint may be invented merely to unlock beam-tip calculation.

## 17. Reference T semantics

beam_tip_reference_point = T0

may remain stored as one explicit reference-pose coordinate.

One T0 coordinate does not define the top-beam rotational law.

Therefore T0 alone does not permit deterministic beam-tip trajectory
generation.

## 18. 80 mm validation status

The project retains the MT/T 556 requirement:

beam-tip horizontal displacement <= 80 mm

over the support operating-height range.

W40-D4 does not execute this validation.

The validation still requires:

1. deterministic beam-tip trajectory
2. deterministic mapping to the complete operating-height range

E propagation alone satisfies neither requirement.

## 19. Support-height boundary

W40-D4 does not infer:

support_height_mm

from B, C, E or T coordinates.

The W40 trajectory remains parameterized by:

rear_link_angle_deg

Operating-height mapping remains unresolved.

## 20. Provenance boundary

Reference E0 retains its supplied provenance.

Future propagated Ei coordinates shall be:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

Rigid-body propagation does not promote input geometry to VERIFIED.

No Formula Registry ID is introduced in W40-D4.

No Calculation Record is introduced in W40-D4.

## 21. Legacy trajectory container boundary

The existing:

TrajectoryResults.shield_top_beam_joint_trajectory

is only a reserved future-result slot.

Its existence does not prove that E propagation is already implemented.

A W40-D5 typed result shall preserve explicit per-sample semantics rather than
blindly populating the legacy list.

## 22. Engineering capability split

After W40-D4, the project capability boundary is:

B/C trajectory
-> shield rigid-body pose
-> E trajectory

DETERMINISTICALLY MODELABLE

while:

B/C/E trajectory
-> top-beam orientation
-> T trajectory

NOT YET UNIQUELY SOLVABLE

These capability levels shall remain separate.

## 23. Software versus physical validation

W40-D4 freezes model semantics and evidence boundaries.

It does not prove:

- model-specific E geometry
- model-specific balance-jack installation
- physical top-beam motion
- physical beam-tip trajectory
- 80 mm compliance

Those require further engineering inputs and validation.

## 24. D5 entry condition

W40-D5 may now implement a typed deterministic:

B/C motion + explicit E0
-> E trajectory

service.

D5 shall preserve:

- motion sample index
- requested angle
- selected-pose availability
- tangent terminal semantics
- no E for NO_SOLUTION
- no E for DEGENERATE
- calculated/partial provenance
- source immutability

D5 shall not implement a beam-tip trajectory.

## 25. W40 final closeout direction

If no additional top-beam orientation geometry becomes available during W40,
the W40 closeout shall explicitly state:

beam-tip trajectory = NOT EXECUTABLE

80 mm validation = NOT EXECUTABLE

The reason shall be:

required top-beam orientation and operating-height mapping are not yet
deterministically available.

That is an engineering evidence result, not a software failure.

Missing geometry shall remain explicit rather than fabricated.
