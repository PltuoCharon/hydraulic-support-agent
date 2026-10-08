# W38-D4 Deterministic Linkage Geometry Derivation

## 1. Scope

W38-D4 implements the first deterministic geometry calculations for
hs.linkageGeometry.v1.

Implementation:

app/services/linkage_geometry.py

D4 derives only direct 2D Euclidean distances from explicit canonical joint
coordinates.

D4 is not a kinematic solver.

It does not implement:

- four-bar closure solving
- pose solving from support height
- trajectory generation
- instantaneous-center calculation
- interference analysis
- optimization
- CAD
- FEA

## 2. Implemented outputs

The D4 service may derive:

- base_pivot_spacing_mm
- rear_link_length_mm
- front_link_length_mm
- shield_beam_effective_length_mm

The geometry mapping is:

rear_link_base -> front_link_base
= base_pivot_spacing_mm

rear_link_base -> rear_link_shield
= rear_link_length_mm

front_link_base -> front_link_shield
= front_link_length_mm

rear_link_shield -> front_link_shield
= shield_beam_effective_length_mm

shield_beam_effective_length_mm is the distance between the two four-bar
shield-beam pivots.

It is not the full physical structural length of the shield beam.

## 3. Partial derivation

derive_geometry() evaluates each available derived quantity independently.

Missing unrelated geometry does not block valid calculations.

For example, if front_link_base is absent but a complete reference pose is
present:

- base_pivot_spacing_mm remains missing
- front_link_length_mm remains missing
- rear_link_length_mm can be calculated
- shield_beam_effective_length_mm can be calculated

No missing coordinate is replaced by zero or by an engineering default.

## 4. Provenance

Every D4-generated length uses:

origin = CALCULATED

evidence_status = PARTIAL

The PARTIAL evidence state is intentional.

A deterministic distance calculation does not independently prove that its
input coordinates represent verified physical geometry.

D4 does not modify the provenance of input coordinates.

AI_PROPOSED input remains AI_PROPOSED.

EVIDENCE_GAP input remains EVIDENCE_GAP.

D4 creates no Formula Registry ID and no Calculation Record.

Therefore generated parameters currently contain:

formula_ids = []

calculation_record_ids = []

## 5. Numeric behavior

The geometry core uses ordinary 2D Euclidean distance.

No rounding is performed inside the geometry service.

Negative coordinates are valid.

NaN and positive/negative infinity are rejected.

This preserves coordinate-system meaning while preventing non-finite derived
geometry.

## 6. Mutation boundary

derive_geometry() returns a new DerivedGeometry object.

It does not mutate:

- fixed_geometry
- reference_pose
- existing derived_geometry
- top_beam_interface
- provenance

This behavior keeps source geometry separate from deterministic derived
geometry.

## 7. Historical-field boundary

D4 does not consume:

- canopy_len
- center_dist
- historical beam_length
- historical example geometry

No historical ambiguous parameter is promoted into four-bar geometry.

## 8. Top-beam boundary

top_beam_interface remains outside the D4 distance derivation core.

D4 does not calculate:

- top-beam length
- top-beam pose
- beam-tip location
- beam-tip trajectory

Those require later explicit geometry and kinematic semantics.

## 9. Validation status

W38-D4 tests cover:

- empty geometry
- partial geometry
- complete reference geometry
- 3-4-5 Euclidean distance
- all four derived quantities
- provenance of calculated outputs
- preservation of AI input provenance
- non-mutation
- negative coordinates
- NaN / positive infinity / negative infinity rejection
- no internal rounding

Passing software tests demonstrates implementation consistency with the D4
contract.

It does not constitute physical validation of a hydraulic-support mechanism.

## 10. D5 entry condition

W38-D5 may build basic pose and kinematic preparation on top of this
deterministic geometry core.

D5 must continue to preserve:

- explicit coordinate-system semantics
- explicit configuration assumptions
- source provenance
- missing geometry
- separation between deterministic calculation and engineering verification

Historical ambiguous geometry shall not be used to close an otherwise
under-defined mechanism.
