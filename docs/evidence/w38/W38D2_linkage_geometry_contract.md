# W38-D2 Linkage Geometry v1 Data Contract

## 1. Objective

W38-D2 defines the application data contract for hydraulic-support linkage
geometry.

Contract identifier:

hs.linkageGeometry.v1

D2 defines data semantics only.

D2 does not:

- implement four-bar closure equations
- solve linkage poses
- calculate trajectories
- perform interference analysis
- perform optimization
- create CAD geometry
- perform FEA
- create new Formula Registry IDs

## 2. Relationship with OverallSupportDesign

LinkageGeometry v1 is intended to become the engineering content carried by the
linkage section of OverallSupportDesign.

W38-D2 does not modify OverallSupportDesign yet.

The existing W37 linkage state therefore remains NOT_IMPLEMENTED until a later
integration step.

## 3. Core four-bar topology

The canonical four-bar mechanism contains four rigid members:

- base
- rear_link
- shield_beam
- front_link

The four canonical revolute joints are:

- rear_link_base
- rear_link_shield
- front_link_shield
- front_link_base

Connectivity is frozen as:

base:
rear_link_base -> front_link_base

rear_link:
rear_link_base -> rear_link_shield

shield_beam:
rear_link_shield -> front_link_shield

front_link:
front_link_shield -> front_link_base

The top-beam / shield-beam joint is not one of these four canonical joints.

It belongs to a separate top_beam_interface.


## 4. Coordinate-system convention

LinkageGeometry v1 uses a normalized 2D longitudinal side-view coordinate
system.

Units:

- linear coordinates: mm
- lengths: mm
- angles: degree

Coordinate convention:

- origin anchor: rear_link_base
- rear_link_base is normalized to (0, 0)
- +X points toward the front / coal-wall side of the support
- +Y points vertically upward

This coordinate convention is a project representation convention.

It is not a measured engineering dimension.

Imported drawing or CAD coordinates may later be translated into this
normalized coordinate system without changing the physical mechanism.

No model-specific link length is implied by this convention.

## 5. Parameter provenance

Engineering values in LinkageGeometry shall preserve the W37 parameter-origin
semantics:

- RETRIEVED
- CALCULATED
- USER_INPUT
- AI_PROPOSED

Evidence status shall remain independent:

- VERIFIED
- PARTIAL
- EVIDENCE_GAP
- NOT_APPLICABLE

An AI_PROPOSED coordinate or dimension is not VERIFIED merely because it
satisfies the data schema.

Missing engineering values shall be represented as missing/null values.

Missing values shall not be replaced with zero or arbitrary defaults.


## 6. Canonical geometry definition

LinkageGeometry v1 uses a coordinate-first canonical representation.

### 6.1 Fixed geometry

rear_link_base is the normalized coordinate origin:

x = 0 mm
y = 0 mm

The model-specific fixed input is:

front_link_base

with:

- x_mm
- y_mm
- origin
- evidence_status
- source_text
- note

This point defines the second fixed base pivot.

### 6.2 Reference pose

A reference pose shall contain:

- support_height_mm
- rear_link_shield
- front_link_shield

Each moving pivot contains:

- x_mm
- y_mm

Engineering coordinates shall preserve origin and evidence metadata.

The reference pose represents one physically meaningful mechanism
configuration.

It shall not be fabricated merely to initialize the model.

### 6.3 Derived link geometry

The following are derived geometry, not independent mandatory inputs in the
canonical representation:

- base_pivot_spacing_mm
- rear_link_length_mm
- front_link_length_mm
- shield_beam_effective_length_mm

These values will later be calculated from joint coordinates.

W38-D2 defines their semantics but does not implement those calculations.

Derived geometry shall use origin:

CALCULATED

after deterministic geometry calculation is implemented.


## 7. Top-beam interface

Top-beam geometry is outside the canonical four-bar closure but is required for
later top-beam pose and beam-tip trajectory analysis.

The optional top_beam_interface may contain:

- shield_top_beam_pivot
- beam_tip_reference_point

These coordinates are defined in the same normalized reference pose.

They shall not be derived from historical canopy_len.

Historical canopy_len remains support_length_parameter_m only.

canopy_len shall not become:

- top-beam length
- beam-tip offset
- shield_top_beam_pivot coordinate
- beam_tip_reference_point coordinate

## 8. Design boundaries

The design_boundaries section may contain:

- operating_height_min_mm
- operating_height_max_mm
- beam_tip_horizontal_displacement_limit_mm

Operating-height boundaries may be traced from existing model/project data when
their semantics and provenance are valid.

They are global mechanism validation boundaries.

They are not joint coordinates.

The project evidence contains the requirement that for a support with a
four-bar mechanism, beam-tip horizontal displacement over the operating-height
range shall not exceed 80 mm.

The 80 mm requirement is a validation constraint.

It is not a linkage dimension and shall not be used to fabricate geometry.

Its source/evidence metadata shall remain attached when populated.


## 9. Pose results

Future deterministic kinematic calculations may produce pose_results.

A pose result may contain:

- support_height_mm
- rear_link_shield
- front_link_shield
- rear_link_angle_deg
- front_link_angle_deg
- shield_beam_angle_deg
- top_beam_pose

W38-D2 defines only result slots.

It does not calculate them.

## 10. Trajectory results

Future trajectory_results may contain:

- beam_tip_trajectory
- beam_tip_horizontal_displacement_mm
- shield_top_beam_joint_trajectory
- instantaneous_center_trajectory

No trajectory result shall be populated before deterministic kinematic
calculation exists.

## 11. Validation results

Future validation_results may include:

- geometry_closure_ok
- operating_height_range_ok
- beam_tip_displacement_ok
- interference_status
- validation_notes

Software schema validation is not physical mechanism validation.

## 12. Missing-value behavior

Unknown engineering geometry remains null / absent.

The following are forbidden:

- zero as a substitute for unknown geometry
- historical example dimensions as automatic defaults
- canopy_len as top-beam geometry
- center_dist as linkage geometry
- support height as a pivot coordinate
- AI_PROPOSED geometry promoted automatically to VERIFIED


## 13. Contract structure

The intended logical structure is:

LinkageGeometry
├── version
├── status
├── coordinate_system
├── design_boundaries
├── fixed_geometry
├── reference_pose
├── derived_geometry
├── top_beam_interface
├── pose_results
├── trajectory_results
├── validation_results
└── provenance

## 14. D3 entry condition

W38-D3 may implement a pure Python/Pydantic data model matching this contract.

D3 shall still not implement:

- four-bar closure
- pose solving
- trajectory generation
- optimization
- CAD
- FEA

The D3 model shall primarily validate structure, units, provenance and explicit
missing values.

Geometry calculation belongs to a later step.
