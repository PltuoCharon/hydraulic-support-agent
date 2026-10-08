# W38-D1 Linkage Geometry and Semantic Audit

## 1. Objective

W38-D1 audits the current hydraulic-support project before implementing any
linkage geometry or kinematics.

D1 does not:

- implement linkage formulas
- create default link lengths
- create default joint coordinates
- implement kinematics
- implement optimization algorithms
- create new Formula Registry IDs

The purpose is to establish which existing parameters may safely enter the
future linkage model and which parameters require new engineering evidence.

## 2. Current implementation status

OverallSupportDesign v1 currently contains only a reserved linkage state.

The current application does not contain:

- a linkage geometry model
- joint-coordinate definitions
- link-length calculations
- pose calculation
- trajectory calculation
- interference calculation

Therefore the current linkage implementation status remains:

NOT_IMPLEMENTED


## 3. Four-bar topology

The project engineering corpus describes the hydraulic-support four-bar
mechanism as being formed by:

- front link
- rear link
- shield beam
- base

This topology may be used as the conceptual four-bar mechanism boundary.

The top beam is not silently treated as one of the four-bar links.

The top-beam / shield-beam connection is a separate geometry relationship that
is required for top-beam pose and beam-tip trajectory analysis.

Because the source text contains OCR corruption, W38-D1 freezes engineering
semantics rather than copying corrupted source symbols or point labels.

## 4. Top-down geometry architecture

The engineering corpus describes a top-down parametric design architecture:

design requirements
→ layout/global parameters
→ skeleton model
→ component geometry
→ assembly/detail design

W38 adopts this architecture conceptually.

Future project layers shall therefore remain distinct:

1. OverallSupportDesign
2. Linkage geometry
3. Skeleton / assembly geometry
4. Detailed structural geometry
5. Analysis / FEA

The linkage model shall not contain detailed plate, rib or weld geometry.


## 5. Class A — existing semantics that may be reused

### 5.1 Working-height boundaries

Existing support-model fields:

- height_min
- height_max

have sufficiently clear overall-support semantics.

They may later provide the required operating-height interval for linkage
validation.

They are not joint coordinates and are not link lengths.

### 5.2 Support type

Existing support type/model information may be used to determine whether a
given linkage topology is applicable.

Applicability must still be checked at model/project level.

### 5.3 Center distance

center_dist has the meaning:

support center distance

It may remain an overall support parameter.

It shall not be interpreted as:

- front-link length
- rear-link length
- base pivot spacing
- any longitudinal linkage dimension

### 5.4 Four-bar component topology

The engineering corpus supports the conceptual existence of:

- front link
- rear link
- shield beam
- base

as the four-bar mechanism.

This establishes topology only.

It does not establish model-specific dimensions.


## 6. Class B — existing but restricted / historical information

### 6.1 canopy_len

Historical canopy_len remains:

support_length_parameter_m / 支护长度参数

It shall not become:

- top-beam length
- control width Bc
- roof-control distance
- beam-end distance
- any linkage length

The legacy database COMMENT that calls canopy_len "顶梁长度(m)" is metadata
debt and is not authoritative engineering semantics.

### 6.2 Historical beam_length

The historical param_dependencies value beam_length = 5.2 m is a legacy global
default.

It shall not become the top-beam geometry of a new linkage design.

### 6.3 Historical roof_end_distance

The historical global default roof_end_distance = 0.7 m is not a model-specific
linkage geometry input.

### 6.4 Historical center_distance default

The historical global default center_distance = 2.05 m shall not override
model-specific center_dist and shall not be used as linkage geometry.

### 6.5 support_parts

support_parts currently stores:

- model_id
- part_name
- part_type
- material
- quantity

It contains structural-composition knowledge but no linkage geometry.

The generic record "连杆" does not define front-link / rear-link geometry,
joint positions or link lengths.


## 7. Literature/reference information that shall not become defaults

The engineering corpus includes linkage design guidance and a specific
optimization example.

The example contains numerical values for:

- rear-link length
- front-link length
- shield-beam length
- pivot-related dimensions
- linkage angles

These values belong to that specific example.

They are reference/example results only.

They shall not be copied into the project as universal or default hydraulic-
support geometry.

The source also contains OCR corruption in several symbols and point labels.

Exact variable names, coordinates and equations shall therefore be rechecked
against a reliable source before implementation.

## 8. Class C — missing engineering geometry

The current project has no verified model-specific values for:

- base rear-link fixed pivot
- base front-link fixed pivot
- rear-link / shield-beam pivot
- front-link / shield-beam pivot
- top-beam / shield-beam pivot
- front-link effective length
- rear-link effective length
- shield-beam effective linkage length
- base fixed-pivot spacing
- top-beam / shield-beam joint offset relative to the top-beam reference plane
- linkage coordinate origin
- positive X direction
- positive Y direction
- beam-tip reference point
- maximum-height mechanism pose
- minimum-height mechanism pose

These values must not be fabricated.

They shall later come from one or more of:

- verified engineering drawings
- reliable literature
- standard-defined constraints
- manufacturer documentation
- explicit engineer/user input
- independently validated generated design candidates


## 9. Kinematic and design constraints

The project evidence already contains a standard-derived requirement that for
supports using a four-bar mechanism, beam-tip horizontal displacement over the
support operating-height range shall not exceed 80 mm.

This is a future validation constraint.

It is not sufficient to determine linkage geometry by itself.

The engineering corpus also describes:

- linkage trajectory constraints
- shield-beam angle constraints
- rear-link angle constraints
- trajectory deviation constraints

These literature ranges remain reference evidence until individually reviewed
and normalized.

## 10. Parameter-layer decision for W38-D2

W38-D2 shall separate linkage information into at least:

### design_boundaries

Examples:

- operating height minimum
- operating height maximum
- beam-tip horizontal-displacement limit

### geometry_inputs

Examples:

- fixed-pivot coordinates
- reference-plane offsets
- initial/reference pose definitions

### derived_geometry

Examples:

- front-link length
- rear-link length
- shield-beam effective linkage length
- moving-joint coordinates

Whether an item is input or derived shall be explicitly frozen by the D2
contract rather than inferred from its name.

### pose_results

Examples:

- support height
- joint coordinates
- link angles
- shield-beam angle
- top-beam pose

### trajectory_results

Examples:

- beam-tip trajectory
- beam-tip horizontal displacement
- instantaneous-center trajectory

### validation_results

Examples:

- height-range validity
- displacement-limit validity
- geometry closure
- interference status

## 11. W38-D1 frozen boundaries

The following interpretations are forbidden:

canopy_len = top-beam length

canopy_len = Bc

center_dist = linkage length

support height = pivot coordinate

historical example dimensions = default geometry

support_parts part existence = verified part geometry

No unverified geometry default shall be introduced merely to make the linkage
model run.

## 12. D2 entry condition

W38-D2 may define a pure linkage data contract after D1 is frozen.

D2 shall not yet implement:

- four-bar closure equations
- motion simulation
- optimization
- CAD
- FEA

D2 shall first define coordinate-system semantics, parameter roles, provenance
and missing-value behavior.
