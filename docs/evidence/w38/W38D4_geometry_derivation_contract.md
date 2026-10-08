# W38-D4 Deterministic Geometry Derivation Contract

## 1. Objective

W38-D4 introduces the first deterministic calculations for
hs.linkageGeometry.v1.

D4 is limited to direct 2D Euclidean geometry derived from explicit linkage
joint coordinates.

Allowed derived quantities are:

- base_pivot_spacing_mm
- rear_link_length_mm
- front_link_length_mm
- shield_beam_effective_length_mm

D4 does not implement:

- four-bar closure solving
- pose solving from support height
- trajectory generation
- instantaneous-center calculation
- interference analysis
- optimization
- CAD
- FEA

## 2. Coordinate source

D4 consumes only the canonical coordinates defined by
hs.linkageGeometry.v1.

No geometry may be inferred from:

- canopy_len
- center_dist
- historical beam_length
- historical example dimensions
- support height alone

Missing coordinates remain missing.

D4 shall not insert zero coordinates or engineering defaults merely to make a
calculation possible.

## 3. Distance semantics

All currently allowed D4 outputs are Euclidean distances in the normalized
longitudinal 2D coordinate system.

For two points P1(x1, y1) and P2(x2, y2), distance is the ordinary planar
distance between those two explicit points.

W38-D4 does not create a Formula Registry ID for this mathematical geometry
identity.

No numerical rounding shall be applied inside the geometry core.

Presentation-layer rounding may be added later if required.


## 4. Derived-parameter mapping

### base_pivot_spacing_mm

Inputs:

- rear_link_base
- front_link_base

rear_link_base is the normalized origin.

If front_link_base is missing, the result remains null.

### rear_link_length_mm

Inputs:

- rear_link_base
- reference_pose.rear_link_shield

If reference_pose is missing, the result remains null.

### front_link_length_mm

Inputs:

- front_link_base
- reference_pose.front_link_shield

Both inputs are required.

If either is missing, the result remains null.

### shield_beam_effective_length_mm

Inputs:

- reference_pose.rear_link_shield
- reference_pose.front_link_shield

A reference_pose is required.

This quantity represents the effective four-bar distance between the two
shield-beam linkage pivots.

It is not the complete physical shield-beam structural length.

## 5. Partial derivation

D4 supports partial geometry.

Available quantities shall be calculated when all of their own required inputs
exist.

A missing unrelated coordinate shall not prevent calculation of an otherwise
fully defined quantity.

Example:

If front_link_base is missing but reference_pose contains both shield-beam
pivots:

- base_pivot_spacing_mm remains null
- front_link_length_mm remains null
- rear_link_length_mm may be calculated
- shield_beam_effective_length_mm may be calculated


## 6. Provenance of calculated geometry

Every D4-generated engineering length shall use:

origin = CALCULATED

Current W38-D4 evidence status shall be:

evidence_status = PARTIAL

This means:

- the value was deterministically calculated
- the calculation itself does not independently verify the source geometry

Input coordinate origin/evidence remains attached to the original
LinkageGeometry input.

D4 shall not rewrite source coordinate provenance.

D4 shall not automatically promote:

AI_PROPOSED -> VERIFIED

or:

EVIDENCE_GAP -> VERIFIED

## 7. Trace identifiers

W38-D4 creates no new Formula Registry ID.

W38-D4 creates no Calculation Record.

Therefore D4-derived parameters currently retain:

- formula_ids = []
- calculation_record_ids = []

This is intentional.

## 8. Mutation boundary

The geometry derivation service shall return a new DerivedGeometry object.

It shall not mutate the supplied LinkageGeometry object.

Existing source coordinates and existing provenance shall remain unchanged.


## 9. Numeric validity

Geometry calculations require finite numeric coordinates.

NaN and positive/negative infinity are invalid calculation inputs.

The geometry service shall reject non-finite coordinates rather than producing
non-finite derived geometry.

Negative coordinate values are not rejected merely because they are negative.

Coordinate sign has geometric meaning in the normalized coordinate system.

## 10. Top-beam boundary

W38-D4 does not derive top-beam geometry.

The following remain outside the D4 core distance derivation:

- shield_top_beam_pivot
- beam_tip_reference_point
- top-beam pose
- beam-tip trajectory

The existence of top_beam_interface shall not change the four allowed D4
derived lengths.

## 11. D5 entry condition

After D4 deterministic geometry derivation is validated, W38-D5 may begin
basic pose/kinematic preparation.

D5 shall not reuse historical ambiguous geometry as linkage input.

Before full kinematic solving is introduced, coordinate conventions,
configuration assumptions and closure behavior must remain explicit.
