# W37-D3 OverallSupportDesign Model Implementation

## Scope

W37-D3 implements the frozen OverallSupportDesign v1 contract as pure
Pydantic application data models.

No database migration, API route, UI integration, engineering formula,
AI parameter generation, Valve calculation, linkage calculation or FEA
is introduced in D3.

## Implemented

- hs.overallDesign.v1 version validation
- EngineeringParameter
- Parameter origin validation
- Evidence-status validation
- WorkingCondition
- ReferenceSupport
- SupportRequirement
- OverallParameters
- ColumnDesign
- PushJackDesign
- reserved Valve / Pipeline / Pump modules
- reserved Linkage / Structure / Analyses modules
- DesignProvenance
- OverallSupportDesign
- validation helper
- serialization helper

## Frozen semantics

- RETRIEVED / CALCULATED / USER_INPUT / AI_PROPOSED remain distinct
- parameter origin and evidence status remain independent
- canopy_len maps only to support_length_parameter_m
- canopy_len is not Bc
- canopy_len is not top-beam length
- Ks is not eta
- AI_PROPOSED is not silently promoted to verified engineering data

## Boundary

The model is intentionally calculation-free.

Existing q_need, resistance, column and push-jack services remain independent
engineering cores.

W37-D4 may introduce adapters that map existing calculation results into
OverallSupportDesign without changing those engineering algorithms.
