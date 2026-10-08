# W38-D3 Linkage Geometry Pure Data Model

## 1. Scope

W38-D3 implements hs.linkageGeometry.v1 as a pure Pydantic model.

Implementation:

app/models/linkage_geometry.py

D3 is calculation-free.

It does not implement:

- four-bar closure
- derived-length calculation
- pose solving
- trajectory generation
- interference calculation
- optimization
- CAD
- FEA
- OverallSupportDesign integration

## 2. Reused W37 primitives

D3 reuses:

- StrictModel
- EngineeringParameter
- ModuleStatus
- DesignProvenance

It does not create a second provenance system.

Engineering parameter origin remains:

- RETRIEVED
- CALCULATED
- USER_INPUT
- AI_PROPOSED

Evidence status remains independent.

## 3. Normalized origin

rear_link_base = (0, 0) is represented by NormalizedOriginPoint.

This is a project coordinate-system convention.

It is not represented as USER_INPUT, RETRIEVED or VERIFIED engineering
geometry.

## 4. Engineering coordinates

Model-specific coordinates use EngineeringPoint2D.

Both x_mm and y_mm are EngineeringParameter values.

Therefore model-specific points preserve:

- value
- unit
- origin
- evidence status
- source trace
- formula trace
- calculation-record trace

Coordinates must use unit "mm".

## 5. Unit validation

D3 validates contract units only.

Length and coordinate fields require:

mm

Angle result fields require:

degree

This is schema validation.

It is not geometry calculation or physical validation.

## 6. Coordinate-first representation

The canonical input representation remains coordinate-first.

The model does not require duplicate user-supplied values for both coordinates
and derived link lengths.

Derived geometry remains optional until deterministic geometry calculation is
implemented.

## 7. Top-beam boundary

top_beam_interface remains outside the canonical four-bar closure.

Historical canopy_len is not consumed by this model.

The model does not contain a canopy_len field.

## 8. Integration status

OverallSupportDesign is not modified in D3.

Its existing linkage placeholder remains separate until a later integration
step.

## 9. D4 entry condition

W38-D4 may implement deterministic pure geometry calculations based on this
model.

Potential D4 outputs include:

- base pivot spacing
- rear-link length
- front-link length
- shield-beam effective linkage length

D4 must not fabricate missing coordinates.

D4 calculation outputs must use origin CALCULATED and preserve input
provenance separately.
