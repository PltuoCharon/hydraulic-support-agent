# W38-D5 Reference Pose Analysis

## 1. Scope

W38-D5 implements deterministic analysis of one explicitly supplied canonical
four-bar reference pose.

Implementation:

app/services/linkage_pose.py

Result model:

ReferencePoseAnalysis

W38-D5 is not a four-bar pose solver.

It does not:

- solve a mechanism pose from support height
- search four-bar closure solutions
- generate trajectories
- calculate beam-tip trajectories
- calculate instantaneous-center trajectories
- perform interference analysis
- perform optimization
- generate CAD
- run FEA

## 2. Required geometry

Reference-pose analysis requires:

- rear_link_base
- front_link_base
- reference_pose.rear_link_shield
- reference_pose.front_link_shield

rear_link_base remains the normalized coordinate origin.

front_link_base and reference_pose must be explicitly available.

Missing geometry is rejected.

No missing coordinate is synthesized from:

- canopy_len
- center_dist
- historical beam_length
- historical example dimensions

## 3. Direction angles

D5 calculates three geometric direction angles:

rear_link_angle_deg:

rear_link_base -> rear_link_shield

front_link_angle_deg:

front_link_base -> front_link_shield

shield_beam_angle_deg:

rear_link_shield -> front_link_shield

Angles use the normalized longitudinal side-view coordinate system.

They are measured from +X using the ordinary planar atan2 convention and
reported in degrees.

These values are project geometric direction angles.

They are not automatically mapped to historical OCR-derived alpha/beta angle
symbols.

## 4. Side classification

D5 evaluates moving pivots relative to the directed fixed-base line:

rear_link_base -> front_link_base

Each moving pivot is classified as:

- POSITIVE
- NEGATIVE
- ON_BASE_LINE

The side test is based on the signed 2D cross product.

This classification describes geometry only.

It is not independently a physical-validity judgement.

## 5. Assembly-side signature

The two moving-pivot side classifications produce a neutral signature:

SAME_SIDE

Both moving pivots are strictly on the same side of the fixed-base line.

OPPOSITE_SIDE

The moving pivots are strictly on opposite sides.

DEGENERATE

The base geometry is degenerate, a required segment has near-zero length, or
a moving pivot lies on the base line.

W38-D5 intentionally does not rename these states OPEN or CROSSED.

Those mechanism-specific labels require separately frozen kinematic semantics.

## 6. Degeneracy

D5 checks the canonical four-bar segments:

- base pivot spacing
- rear-link length
- front-link length
- shield-beam effective linkage length

Zero or near-zero segments are treated as degenerate.

A zero-length segment has no valid direction angle, so the corresponding angle
result remains null.

Non-finite coordinates are rejected.

Negative coordinates remain valid.

The internal numerical tolerance is computational infrastructure, not a
hydraulic-support design parameter.

## 7. Provenance

Every calculated direction angle uses:

origin = CALCULATED

evidence_status = PARTIAL

The calculated angle does not independently verify its source geometry.

D5 creates:

formula_ids = []

calculation_record_ids = []

No new Formula Registry ID is introduced.

No Calculation Record is created.

Input coordinate provenance remains unchanged.

AI_PROPOSED input is not promoted to VERIFIED.

EVIDENCE_GAP input is not promoted to VERIFIED.

## 8. Support-height boundary

reference_pose.support_height_mm remains metadata describing the supplied
reference pose.

D5 does not infer support height from linkage coordinates.

D5 does not move or solve the mechanism when support_height_mm changes.

Two otherwise identical geometries with different support_height_mm values
therefore produce the same geometric pose analysis.

The relationship between support height and mechanism configuration belongs to
later kinematic solving.

## 9. Top-beam boundary

top_beam_interface does not participate in D5 core four-bar reference-pose
analysis.

Changing:

- shield_top_beam_pivot
- beam_tip_reference_point

does not change the D5 core result.

Top-beam pose and beam-tip trajectory remain later work.

## 10. Validation status

W38-D5 tests cover:

- missing fixed-base geometry
- missing reference pose
- three atan2 direction angles
- SAME_SIDE classification
- OPPOSITE_SIDE classification
- ON_BASE_LINE degeneracy
- zero base spacing
- zero rear-link length
- calculated-angle provenance
- preservation of input provenance
- independence from support_height_mm
- independence from top_beam_interface
- NaN rejection
- positive infinity rejection
- negative infinity rejection

Passing these tests demonstrates software consistency with the W38-D5
contract.

It does not constitute physical validation of a hydraulic-support four-bar
mechanism.

## 11. W38-D6 entry condition

W38-D6 may now perform final W38 regression, evidence review and architecture
freeze.

W38-D6 shall not introduce new kinematic algorithms.

Full four-bar pose solving and trajectory analysis remain subsequent work.
