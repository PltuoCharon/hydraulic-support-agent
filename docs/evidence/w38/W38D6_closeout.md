# W38-D6 Linkage Geometry and Reference-Pose Closeout

## 1. W38 objective

W38 establishes a trustworthy semantic and software foundation for hydraulic-
support four-bar linkage work.

The completed chain is:

D1
linkage geometry semantic audit

D2
hs.linkageGeometry.v1 data contract

D3
strict Pydantic data model

D4
deterministic 2D geometry derivation

D5
explicit reference-pose analysis

D6
regression, capability freeze and next-stage entry conditions

W38 does not claim to implement a complete four-bar kinematic solver.

## 2. Frozen canonical topology

The canonical four-bar members are:

- base
- rear_link
- shield_beam
- front_link

The canonical revolute joints are:

- rear_link_base
- rear_link_shield
- front_link_shield
- front_link_base

The top-beam / shield-beam joint is not one of the four canonical four-bar
joints.

Top-beam geometry remains in top_beam_interface.


## 3. Frozen coordinate convention

hs.linkageGeometry.v1 uses a normalized longitudinal side-view 2D coordinate
system.

Frozen convention:

- rear_link_base = (0, 0)
- +X points toward the front / coal-wall side
- +Y points upward
- linear unit = mm
- angular unit = degree

The normalized origin is a representation convention.

It is not a fabricated measured engineering coordinate.

Model-specific coordinates preserve parameter origin and evidence metadata.

## 4. Provenance rules

W38 reuses the W37 provenance vocabulary:

ParameterOrigin:

- RETRIEVED
- CALCULATED
- USER_INPUT
- AI_PROPOSED

EvidenceStatus:

- VERIFIED
- PARTIAL
- EVIDENCE_GAP
- NOT_APPLICABLE

Origin and evidence status remain independent.

AI_PROPOSED is not automatically VERIFIED.

A deterministic calculation does not independently verify its source
engineering geometry.

D4 and D5 calculated outputs therefore currently use:

origin = CALCULATED

evidence_status = PARTIAL

No W38 Formula Registry ID was introduced.

No W38 Calculation Record was introduced.


## 5. Implemented capabilities

### 5.1 Data representation

The system can represent:

- fixed linkage pivots
- one explicit reference pose
- provenance-aware 2D engineering coordinates
- design-height boundaries
- derived linkage geometry
- optional top-beam interface
- future pose/result slots
- future trajectory/result slots
- future validation/result slots

Unknown geometry remains missing.

### 5.2 Deterministic geometry derivation

W38-D4 can derive:

- base_pivot_spacing_mm
- rear_link_length_mm
- front_link_length_mm
- shield_beam_effective_length_mm

Derivation uses explicit canonical coordinates only.

Partial geometry is supported.

The geometry service does not mutate the source LinkageGeometry object.

### 5.3 Reference-pose analysis

W38-D5 can calculate:

- rear_link_angle_deg
- front_link_angle_deg
- shield_beam_angle_deg

using the project atan2 direction-angle convention.

D5 can also classify moving pivots relative to the directed fixed-base line:

- POSITIVE
- NEGATIVE
- ON_BASE_LINE

and produce the neutral assembly-side signature:

- SAME_SIDE
- OPPOSITE_SIDE
- DEGENERATE

These labels describe geometry.

They are not yet renamed OPEN or CROSSED.


## 6. Explicitly not implemented

At W38 closeout, the following remain NOT IMPLEMENTED:

- solving moving pivot coordinates from support height
- four-bar closure solving
- selection between multiple mathematical pose solutions
- OPEN / CROSSED mechanism-specific branch semantics
- continuous pose tracking
- operating-height sweep
- beam-tip trajectory
- horizontal beam-tip displacement calculation
- instantaneous-center trajectory
- interference checking
- mechanism optimization
- GA integration
- PSO integration
- NSGA-II integration
- CAD generation
- FEA coupling

A populated reference_pose is therefore an explicit input configuration, not
the result of a complete mechanism solver.

## 7. Historical-data exclusions

W38 does not infer four-bar geometry from:

- canopy_len
- center_dist
- historical beam_length
- historical roof_end_distance
- historical example dimensions
- support height alone

Historical canopy_len remains support_length_parameter_m only.

center_dist remains an overall transverse support parameter and is not a
linkage length.

Historical literature examples may support research understanding but are not
project defaults.


## 8. Standard-derived constraint status

The project retains the MT/T 556-1996 section 4.6.4 requirement that, for a
support using a four-bar mechanism, beam-tip horizontal displacement over the
operating-height range shall not exceed 80 mm.

In hs.linkageGeometry.v1 this is represented as a validation boundary:

beam_tip_horizontal_displacement_limit_mm = 80 mm

It is not a linkage dimension.

W38 does not yet calculate the beam-tip trajectory or evaluate this limit.

That validation becomes executable only after the required top-beam geometry
and continuous mechanism poses are explicitly available.

## 9. Software-validation boundary

W38 tests validate:

- data-contract semantics
- strict model behavior
- provenance preservation
- deterministic Euclidean geometry
- finite-number handling
- non-mutation
- direction-angle convention
- side classification
- neutral assembly signature
- degenerate reference geometry behavior

Passing software tests does not constitute:

- physical mechanism validation
- manufacturing validation
- structural-strength validation
- regulatory certification


## 10. W39 entry conditions

The next linkage stage may introduce actual four-bar closure and pose solving.

Before implementation, W39 must explicitly freeze:

1. independent input variable(s) used to parameterize mechanism motion
2. mathematical closure formulation
3. circle-intersection or equivalent deterministic solution method
4. treatment of zero / one / two mathematical solutions
5. configuration-branch continuity rules
6. mechanism-specific OPEN / CROSSED semantics, if those labels are adopted
7. relationship between solved mechanism pose and support_height_mm
8. numerical tolerances
9. unreachable-configuration behavior
10. provenance of solved coordinates

W39 must not select a mathematical solution merely because it is the first
solution returned by an algorithm.

W39 must not fabricate geometry to make closure possible.

W39 must preserve the W38 coordinate convention and provenance rules.

## 11. Recommended continuation

The recommended next chain is:

W39
four-bar closure and deterministic pose solving

W40
operating-range kinematics and trajectory validation

W41
mature optimization algorithm integration

This ordering keeps mechanism physics ahead of optimization.

No optimizer should be connected before deterministic pose and trajectory
behavior are independently testable.
