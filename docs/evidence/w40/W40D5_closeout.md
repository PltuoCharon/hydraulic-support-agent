# W40-D5 Shield / Top-Beam Joint Trajectory Closeout

## 1. Scope

W40-D5 implements deterministic propagation of the shield/top-beam revolute
joint center E across one W40 motion segment.

Implemented model:

app/models/linkage_top_beam.py

Implemented service:

app/services/linkage_top_beam.py

Public operation:

propagate_shield_top_beam_joint(
    linkage: LinkageGeometry,
    motion: MotionSegmentResult,
    tolerance: NumericalTolerance,
) -> ShieldTopBeamJointTrajectoryResult

W40-D5 does not implement top-beam orientation or beam-tip motion.

## 2. Input authority

The service uses:

LinkageGeometry

for explicit reference geometry,

MotionSegmentResult

for deterministic W40 motion,

and:

NumericalTolerance

for numerical comparison.

No hidden tolerance is introduced.

## 3. Required explicit geometry

Propagation requires:

B0 = linkage.reference_pose.rear_link_shield

C0 = linkage.reference_pose.front_link_shield

E0 = linkage.top_beam_interface.shield_top_beam_pivot

Missing reference_pose or missing E0 is an explicit error.

No historical/default geometry is substituted.

## 4. Directed shield frame

The reference rigid-body frame is defined from:

B0 -> C0

with:

L0 = |C0 - B0|

u0 = (C0 - B0) / L0

v0 = (-u0_y, u0_x)

The frame direction is deterministic.

It is not selected from coordinate magnitude, visual orientation, or candidate
ordering.

## 5. Numerical degeneracy

The B/C axis must remain numerically non-degenerate.

W40-D5 reuses the W39 scale-aware distance tolerance policy:

max(
    tolerance.absolute_mm,
    tolerance.relative * scale_mm
)

A B/C axis whose length is at or below the effective tolerance is rejected.

## 6. Reference attachment derivation

The explicit E0 coordinate is transformed into fixed shield-body coordinates:

s_E = dot(E0 - B0, u0)

n_E = dot(E0 - B0, v0)

The resulting typed attachment preserves:

- reference B0
- reference C0
- reference E0
- longitudinal offset s_E
- normal offset n_E
- deterministic provenance

The input E0 provenance is retained.

## 7. Reference round trip

W40-D5 reconstructs:

E_roundtrip =
B0 + s_E * u0 + n_E * v0

and verifies that the Euclidean error relative to E0 is within the explicit
scale-aware NumericalTolerance.

Tolerance is not enlarged to force a pass.

## 8. Motion-reference consistency

Before propagation, the first selected W40 motion pose is compared against the
LinkageGeometry reference B0/C0.

Reference B mismatch is rejected.

Reference C mismatch is rejected.

A small mismatch inside the explicit numerical tolerance is accepted.

This prevents an attachment derived from one reference mechanism from being
silently applied to another motion segment.

## 9. Per-sample propagation

For each selected motion pose:

Bi = selected_pose.rear_link_shield

Ci = selected_pose.front_link_shield

define:

Li = |Ci - Bi|

ui = (Ci - Bi) / Li

vi = (-ui_y, ui_x)

Then:

Ei = Bi + s_E * ui + n_E * vi

Ei is a deterministic calculated shield/top-beam joint-center coordinate.

## 10. Rigid-body invariant

For every selected propagated Ei, W40-D5 rechecks the local shield-frame
coordinates.

Recovered longitudinal coordinate shall reproduce:

s_E

Recovered normal coordinate shall reproduce:

n_E

within NumericalTolerance.

No arbitrary inter-sample coordinate-jump threshold is introduced.

## 11. TWO_SOLUTIONS sample

For:

TWO_SOLUTIONS + SELECTED

the sample contains one selected B/C pose.

W40-D5 therefore emits:

selected_pose_available = true

joint_center = calculated Ei

## 12. TANGENT sample

For terminal:

TANGENT + SELECTED

the sample still contains one unique B/C pose.

W40-D5 emits one final calculated Ei.

The tangent sample remains the final motion sample.

W40-D5 does not traverse the tangent onto another branch.

## 13. NO_SOLUTION sample

For terminal:

NO_SOLUTION

there is no selected pose.

The D5 trajectory sample is preserved for one-to-one alignment with:

selected_pose_available = false

joint_center = null

No E coordinate is fabricated.

## 14. DEGENERATE sample

For terminal:

DEGENERATE

there is no selected pose.

The D5 trajectory sample is preserved for one-to-one alignment with:

selected_pose_available = false

joint_center = null

No E coordinate is fabricated.

## 15. One-to-one trajectory alignment

D5 output contains exactly one trajectory sample for every MotionSample that
W40-D3 actually processed.

For each sample it preserves:

- sample_index
- requested_angle_deg
- closure_state
- selected-pose availability

D5 does not insert, delete, reorder, or renumber processed motion samples.

## 16. Requested-count semantics

The D5 result preserves:

motion.requested_angle_count

and:

motion.termination

The actual D5 sample count equals:

len(motion.samples)

When W40-D3 terminates early, D5 does not fabricate entries for requested
angles that were never solved.

## 17. Motion termination preservation

The following termination values remain unchanged:

COMPLETED

TANGENT_BOUNDARY

NO_SOLUTION_BOUNDARY

DEGENERATE_BOUNDARY

D5 does not reinterpret the W40-D3 motion boundary.

## 18. Provenance

The propagation engine identity is:

W40_SHIELD_TOP_BEAM_JOINT_RIGID_PROPAGATION

with:

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

Each propagated Ei coordinate uses:

origin = CALCULATED

evidence_status = PARTIAL

No Formula Registry ID is introduced.

No Calculation Record is fabricated.

## 19. Input immutability

The service verifies that propagation does not mutate:

LinkageGeometry

MotionSegmentResult

NumericalTolerance

Reference B0/C0/E0 data remain unchanged.

Existing W39 closure results remain unchanged.

## 20. Determinism

Repeated execution using identical:

LinkageGeometry

MotionSegmentResult

NumericalTolerance

produces an equal:

ShieldTopBeamJointTrajectoryResult

There is no random state or candidate-choice heuristic.

## 21. Legacy trajectory slot boundary

W40-D5 does not mutate:

LinkageGeometry.trajectory_results

and does not directly populate:

TrajectoryResults.shield_top_beam_joint_trajectory

The strongly typed D5 result is authoritative for this stage.

Any compatibility mapping requires a separate explicit integration step.

## 22. Top-beam boundary

W40-D5 does not calculate:

top_beam_angle_deg

top_beam_pose

beam_tip_reference_point propagation

beam_tip_trajectory

beam_tip_horizontal_displacement_mm

or:

80 mm compliance.

E motion alone does not determine top-beam orientation.

## 23. Support-height boundary

W40-D5 does not calculate:

support_height_mm

from B.y, C.y, E.y, or any other joint coordinate.

The trajectory remains parameterized by:

rear_link_angle_deg

It is not yet an operating-height trajectory.

## 24. Automated validation achieved

W40-D5 automated tests establish:

- typed E attachment
- typed aligned E trajectory
- calculated/partial provenance
- completed increasing and decreasing trajectory states
- normal selected-pose propagation
- tangent final-point propagation
- null E for NO_SOLUTION
- null E for DEGENERATE
- one-to-one sample alignment
- requested-count preservation
- termination preservation
- reference round trip
- independent rigid-transform agreement
- reference B/C consistency
- absolute-tolerance acceptance
- relative scale-aware tolerance acceptance
- numerical-degeneracy rejection
- missing reference geometry rejection
- source immutability
- deterministic repeated execution
- no legacy trajectory mutation
- absence of beam-tip and support-height outputs

These are deterministic software-level guarantees.

They do not constitute physical certification of a hydraulic support.

## 25. W40 capability after D5

The completed deterministic chain is now:

rear_link_angle_deg samples

-> branch-preserving W39 closure poses

-> ordered B/C trajectory

-> shield rigid-body pose

-> deterministic E trajectory

This chain is executable for explicit reference E0 geometry.

## 26. Remaining engineering gap

The next unresolved relation is:

B/C/E trajectory

-> top-beam orientation

-> beam-tip T trajectory

Current project geometry does not uniquely determine that relation.

The balance-jack installation geometry / top-beam pose law remains incomplete.

This gap shall remain explicit.

## 27. W40-D6 entry condition

W40-D6 shall close the W40 continuous-kinematics stage.

Unless additional deterministic top-beam orientation geometry becomes
available, D6 shall record:

beam-tip trajectory = NOT EXECUTABLE

80 mm validation = NOT EXECUTABLE

The reason is missing top-beam orientation and operating-height mapping, not
failure of the completed B/C/E trajectory implementation.

Missing engineering geometry shall not be fabricated.
