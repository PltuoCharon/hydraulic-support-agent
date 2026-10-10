# W40-D5 Shield / Top-Beam Joint Trajectory Contract

## 1. Objective

W40-D5 implements the next deterministic kinematic layer after W40-D3 and
W40-D4:

four-bar B/C motion

plus:

explicit reference shield_top_beam_pivot E0

-> deterministic E trajectory.

W40-D5 shall use the rigid shield-frame semantics frozen in W40-D4.

Target typed model:

app/models/linkage_top_beam.py

Target service:

app/services/linkage_top_beam.py

Planned public operation:

propagate_shield_top_beam_joint(
    linkage: LinkageGeometry,
    motion: MotionSegmentResult,
    tolerance: NumericalTolerance,
) -> ShieldTopBeamJointTrajectoryResult

W40-D5 shall not calculate beam-tip motion.

## 2. Authoritative inputs

The authoritative reference mechanism geometry shall come from:

LinkageGeometry

The authoritative continuous mechanism motion shall come from:

MotionSegmentResult

The authoritative numerical comparison policy shall come from:

NumericalTolerance

W40-D5 shall not introduce a hidden tolerance.

## 3. Required reference geometry

D5 propagation requires explicit:

linkage.reference_pose.rear_link_shield = B0

linkage.reference_pose.front_link_shield = C0

linkage.top_beam_interface.shield_top_beam_pivot = E0

All three points shall be present.

If any required point is missing, propagation is not executable.

W40-D5 shall fail explicitly rather than fabricate geometry.

## 4. E0 must remain explicit

E0 shall not be derived from:

canopy_len

beam_length

roof_end_distance

center_dist

support_height_mm

beam_tip_reference_point

historical support examples

or generic support-part presence.

No zero coordinate or project-wide default shall replace missing E0.

## 5. Reference shield frame

For explicit reference geometry:

B0

C0

E0

define:

L0 = |C0 - B0|

u0 = (C0 - B0) / L0

v0 = (-u0_y, u0_x)

The reference frame origin is B0.

The frame is directed from:

B0 -> C0

L0 shall be finite and strictly positive.

A zero-length or numerically degenerate B0/C0 shield axis makes propagation
not executable.

## 6. Attachment local coordinates

The reference E attachment shall be converted to:

s_E = dot(E0 - B0, u0)

n_E = dot(E0 - B0, v0)

The pair:

(s_E, n_E)

is the frozen local shield-body coordinate of the shield/top-beam joint center.

These are calculated millimetre quantities.

## 7. Typed attachment model

The D5 typed model shall include a representation equivalent to:

ShieldTopBeamJointAttachment

containing at least:

version = 1

reference_rear_link_shield = B0

reference_front_link_shield = C0

reference_joint_center = E0

longitudinal_offset_mm = s_E

normal_offset_mm = n_E

provenance

The attachment model shall not contain beam-tip geometry.

## 8. Reference motion consistency

The first MotionSample in MotionSegmentResult represents the motion reference
pose.

Its selected pose shall contain:

rear_link_shield = B_motion0

front_link_shield = C_motion0

D5 shall verify that:

B_motion0

matches:

B0

and:

C_motion0

matches:

C0

within the explicit NumericalTolerance.

A reference mismatch is an explicit error.

D5 shall not derive an attachment from one mechanism and apply it to another
motion segment.

## 9. Numerical comparison

Reference consistency and round-trip checks shall use a scale-aware effective
millimetre tolerance derived from the supplied NumericalTolerance.

The comparison policy shall account for:

absolute_mm

and:

relative

without introducing another undocumented tolerance constant.

Exact implementation may reuse the established W39 scale-aware numerical
tolerance semantics.

## 10. Reference round trip

After calculating:

s_E

and:

n_E

D5 shall reconstruct the reference joint center:

E_roundtrip =
B0 + s_E * u0 + n_E * v0

The Euclidean distance between:

E_roundtrip

and:

E0

shall be within the explicit effective tolerance.

Failure is an explicit error.

The service shall not enlarge tolerance merely to force the round trip to pass.

## 11. Per-sample directed shield frame

For every MotionSample with a selected pose:

Bi = selected_pose.rear_link_shield

Ci = selected_pose.front_link_shield

Li = |Ci - Bi|

ui = (Ci - Bi) / Li

vi = (-ui_y, ui_x)

The frame remains directed:

Bi -> Ci

D5 shall not reverse the frame from coordinate magnitude or visual
orientation.

## 12. Per-sample E propagation

For every selected B/C pose:

Ei = Bi + s_E * ui + n_E * vi

Ei is the propagated shield/top-beam revolute-joint center.

This is a deterministic planar rigid-body transform.

The operation does not solve top-beam pitch.

## 13. Typed trajectory sample

The D5 typed model shall include a representation equivalent to:

ShieldTopBeamJointTrajectorySample

containing at least:

version = 1

sample_index

requested_angle_deg

closure_state

selected_pose_available

joint_center

For a selected pose:

selected_pose_available = true

joint_center = propagated Ei

For an unsolved pose:

selected_pose_available = false

joint_center = null

## 14. One-to-one sample alignment

The D5 trajectory result shall contain exactly one trajectory sample for every
MotionSample in the input MotionSegmentResult.

The output sample_index shall equal the corresponding motion sample_index.

The output requested_angle_deg shall equal the corresponding motion
requested_angle_deg.

D5 shall not:

skip input samples

insert intermediate samples

reorder samples

or renumber samples.

## 15. Normal TWO_SOLUTIONS sample

For:

TWO_SOLUTIONS + SELECTED

the sample contains a valid selected B/C pose.

D5 shall therefore calculate one propagated E coordinate.

The resulting joint_center shall not be null.

## 16. Terminal TANGENT sample

For:

TANGENT + SELECTED

the sample still contains a unique selected B/C pose.

D5 shall calculate one final propagated E coordinate.

The tangent E coordinate may therefore be the final available joint-center
point in the trajectory.

D5 shall not continue motion beyond the terminal tangent.

## 17. Terminal NO_SOLUTION sample

For:

NO_SOLUTION

there is no selected B/C pose.

The corresponding D5 trajectory sample shall remain present for alignment, but:

selected_pose_available = false

joint_center = null

D5 shall not fabricate an E coordinate.

## 18. Terminal DEGENERATE sample

For:

DEGENERATE

there is no selected B/C pose.

The corresponding D5 trajectory sample shall remain present for alignment, but:

selected_pose_available = false

joint_center = null

D5 shall not fabricate an E coordinate.

## 19. Motion termination preservation

The D5 trajectory result shall preserve the original:

MotionTermination

from MotionSegmentResult.

D5 does not create a second independent motion termination interpretation.

For example:

COMPLETED

TANGENT_BOUNDARY

NO_SOLUTION_BOUNDARY

DEGENERATE_BOUNDARY

shall remain unchanged.

## 20. Requested versus processed semantics

D5 receives an already processed MotionSegmentResult.

Therefore the D5 output sample count shall equal:

len(motion.samples)

not:

motion.requested_angle_count

when the original sweep terminated early.

The original requested_angle_count may be preserved as metadata.

D5 shall not fabricate trajectory entries for angles that W40-D3 never solved.

## 21. Typed trajectory result

The D5 typed model shall include a representation equivalent to:

ShieldTopBeamJointTrajectoryResult

containing at least:

version = 1

attachment

direction

reference_branch

reference_angle_deg

requested_angle_count

samples

termination

provenance

It shall not require:

support_height_mm

top_beam_angle_deg

beam_tip_trajectory

beam_tip_horizontal_displacement_mm

## 22. Provenance

The D5 attachment derivation and trajectory propagation are deterministic
calculated results.

D5 trajectory provenance shall use an engine identity equivalent to:

W40_SHIELD_TOP_BEAM_JOINT_RIGID_PROPAGATION

with:

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

W40-D5 introduces no Formula Registry ID.

W40-D5 creates no Calculation Record.

## 23. Propagated point provenance

Each propagated Ei coordinate shall use:

origin = CALCULATED

evidence_status = PARTIAL

The numerical E0 reference coordinate retains its original supplied provenance
inside the attachment/reference input.

The calculated Ei shall not be promoted to VERIFIED merely because the rigid
transform is deterministic.

## 24. Rigid attachment invariants

For every selected output sample, reconstructing the local coordinates of Ei in
the corresponding Bi -> Ci frame shall reproduce:

s_E

and:

n_E

within NumericalTolerance.

This verifies that E does not drift relative to the shield rigid body.

No arbitrary coordinate-jump threshold is introduced.

## 25. Input immutability

D5 shall not mutate:

LinkageGeometry

MotionSegmentResult

reference B0

reference C0

reference E0

MotionSample

or W39 ClosureResult objects contained inside the motion result.

All propagated points and typed trajectory objects shall be newly constructed.

## 26. Determinism

Repeated execution using identical:

LinkageGeometry

MotionSegmentResult

NumericalTolerance

shall produce equal:

ShieldTopBeamJointTrajectoryResult

values.

There shall be no random state or candidate-dependent heuristic.

## 27. No legacy-slot side effect

D5 shall not mutate:

LinkageGeometry.trajectory_results

or directly populate:

TrajectoryResults.shield_top_beam_joint_trajectory

as a side effect.

The D5 typed result is the authoritative propagation result.

Any later compatibility mapping into legacy trajectory slots shall require an
explicit integration step.

## 28. No beam-tip inference

D5 shall not calculate:

T

beam_tip_reference_point propagation

top_beam_pose

top_beam_angle_deg

beam_tip_trajectory

beam_tip_horizontal_displacement_mm

or:

80 mm compliance.

Known E motion does not remove the independent top-beam orientation degree of
freedom.

## 29. No support-height inference

D5 shall not calculate:

support_height_mm

from:

B.y

C.y

E.y

or any other joint coordinate.

The D5 trajectory remains parameterized by:

rear_link_angle_deg.

## 30. Error boundary

D5 shall fail explicitly for conditions including:

missing B0

missing C0

missing E0

degenerate B0/C0 axis

reference motion B mismatch

reference motion C mismatch

selected motion sample with degenerate Bi/Ci axis

or an internally inconsistent selected-pose state.

D5 shall not repair those inputs silently.

## 31. Software-validation boundary

D5 tests shall verify deterministic geometry and typed-state behavior.

Passing D5 tests does not prove:

model-specific E0 accuracy

real balance-jack geometry

top-beam physical orientation

beam-tip motion

operating-height coverage

or 80 mm compliance.

Those remain separate engineering validation tasks.

## 32. D6 entry condition

After D5 implementation, W40 will possess:

rear-link-angle trajectory

-> deterministic B/C trajectory

-> deterministic E trajectory

for all selected poses.

If no additional deterministic top-beam orientation relation becomes
available, W40-D6 shall close the stage with:

beam-tip trajectory = NOT EXECUTABLE

80 mm validation = NOT EXECUTABLE

while preserving the completed B/C/E trajectory capability.

Missing top-beam orientation geometry shall remain an explicit evidence gap.
