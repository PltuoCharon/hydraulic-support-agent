# W38-D5 Reference Pose and Kinematic Preparation Contract

## 1. Objective

W38-D5 introduces deterministic analysis of an explicitly supplied reference
pose for hs.linkageGeometry.v1.

D5 operates only when the canonical four-bar reference geometry is already
explicit.

D5 may calculate:

- rear-link direction angle
- front-link direction angle
- shield-beam direction angle
- relative side of moving pivots with respect to the fixed base line
- a neutral assembly-side signature
- basic degeneracy status

D5 does not implement:

- solving a pose from support height
- four-bar closure search
- trajectory generation
- instantaneous-center trajectory
- beam-tip trajectory
- interference analysis
- optimization
- CAD
- FEA

## 2. Required geometry

Reference-pose analysis requires:

- rear_link_base
- front_link_base
- reference_pose.rear_link_shield
- reference_pose.front_link_shield

rear_link_base remains the normalized origin.

If front_link_base is missing, reference-pose analysis cannot establish the
fixed base line and shall not fabricate one.

If reference_pose is missing, no reference-pose analysis is possible.


## 3. Direction-angle convention

All D5 direction angles use the normalized coordinate system from
hs.linkageGeometry.v1.

Angles are measured from the +X axis using the ordinary planar atan2
convention.

The intended ranges are represented by the deterministic atan2 result in
degrees.

Definitions:

rear_link_angle_deg:

rear_link_base -> rear_link_shield

front_link_angle_deg:

front_link_base -> front_link_shield

shield_beam_angle_deg:

rear_link_shield -> front_link_shield

These are geometric direction angles.

W38-D5 does not claim that they are identical to every historical literature
angle symbol.

No OCR-derived alpha/beta symbol is silently mapped onto these fields.

## 4. Fixed-base side test

The fixed base line is:

rear_link_base -> front_link_base

For any point P, D5 may calculate the signed 2D cross product between:

base vector

and

rear_link_base -> P

The sign determines only which side of the directed base line P occupies.

Classification:

POSITIVE
NEGATIVE
ON_BASE_LINE

This is a normalized computational convention.

It is not by itself a physical-validity judgement.


## 5. Assembly-side signature

D5 defines a neutral geometry signature using the side classifications of:

- rear_link_shield
- front_link_shield

If both moving pivots are strictly on the same side of the directed base line:

assembly_side_signature = SAME_SIDE

If the two moving pivots are strictly on opposite sides:

assembly_side_signature = OPPOSITE_SIDE

If either moving pivot lies on the base line, or the base line itself is
degenerate:

assembly_side_signature = DEGENERATE

W38-D5 does not rename these states to OPEN or CROSSED.

Those mechanism-specific labels require a separately frozen kinematic
definition.

## 6. Degenerate geometry

D5 shall treat a reference pose as geometrically degenerate if any required
canonical four-bar segment has zero or near-zero length.

The checked segments are:

- base pivot spacing
- rear-link length
- front-link length
- shield-beam effective linkage length

D5 shall also reject non-finite geometry.

A configurable numerical tolerance may be used internally for zero-length
detection.

The tolerance is numerical infrastructure.

It shall not be represented as a hydraulic-support engineering design
parameter.


## 7. Provenance

D5-calculated direction angles shall use:

origin = CALCULATED

evidence_status = PARTIAL

The calculated angle does not independently verify the physical source
geometry.

D5 creates no new Formula Registry ID.

D5 creates no Calculation Record.

Input point provenance shall not be rewritten.

## 8. Support-height boundary

reference_pose.support_height_mm is retained as explicit reference-pose
metadata.

W38-D5 does not infer support height from joint coordinates.

W38-D5 does not use support_height_mm to solve or move the mechanism.

The geometric relationship between support height and mechanism pose belongs
to later kinematic work.

## 9. Historical-field boundary

D5 shall not use:

- canopy_len
- center_dist
- historical beam_length
- historical example dimensions

to create or complete a reference pose.

## 10. D6 entry condition

After reference-pose analysis is deterministic and validated, W38-D6 may close
the week with regression, documentation and architecture freeze.

Full pose solving from arbitrary support height remains later work unless its
mathematical assumptions, configuration branch and validation evidence have
first been explicitly frozen.
