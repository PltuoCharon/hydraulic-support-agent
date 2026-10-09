# W39-D1 Push-Jack Traceability Audit

## 1. Purpose

This audit is the W39 system-completeness side line.

It determines whether push-jack traceability should be expanded during W39
while the main research line moves into four-bar closure solving.

No push-jack engineering algorithm is changed by this audit.

## 2. Current implementation

The push-jack core implementation is:

app/services/calc/push_jack.py

The API wrapper is:

app/routers/calc.py

The two modules contain functions with the same public name:

push_jack_design

but they have different interfaces.

The service function is the engineering calculation core.

The router function accepts PushJackDesignReq and delegates to the service
core.

## 3. Existing engineering capability

The current push-jack service supports explicit inputs for:

- push_required_kn
- pressure_mpa
- rod_mm
- pull_required_kn
- stroke_mm

It derives or evaluates:

- calculated bore
- rounded candidate bore
- candidate-bore push force
- push requirement satisfaction
- optional pull force
- optional pull requirement satisfaction

The implementation reuses HydraulicCylinder primitives.

It does not:

- create a default working pressure
- automatically create a rod diameter
- automatically create a stroke
- introduce eta
- assume which chamber corresponds to a real machine operating action

## 4. Standard verification boundary

The current candidate-bore sequence is not claimed as verified MT/T 94 data.

Runtime therefore preserves:

mt_t94_verified = false

This status shall remain unchanged until the candidate sequence is independently
verified against an authoritative source.

## 5. Formula Registry status

The authoritative Formula Registry currently contains:

F-COL-001
F-COL-002
F-COL-003

for column-related calculations.

It contains no active F-JACK Formula ID.

W39-D1 shall not create an F-JACK ID merely because push-jack calculations
exist in software.

A Formula Registry entry requires independently reviewed engineering semantics
and evidence.

## 6. Calculation Record status

The push-jack core currently creates no Calculation Record.

The W37 overall-design adapter therefore preserves:

formula_ids = []

calculation_record_ids = []

Push-jack engineering traceability remains PARTIAL.

## 7. Overall-design integration

Push-jack calculation results can already be mapped into:

hydraulic_components.push_jack

The adapter preserves the current traceability boundary rather than inventing
missing formula or record identifiers.

The adapter does not recalculate the push-jack design.

## 8. W39 decision

Decision:

KEEP CURRENT PUSH-JACK CALCULATION CAPABILITY.

DO NOT CREATE F-JACK DURING W39-D1.

DO NOT CREATE A PUSH-JACK CALCULATION RECORD DURING W39-D1.

The remaining work is evidence debt rather than a blocker for the W39
four-bar research main line.

The push-jack evidence gap may be revisited when an authoritative standard,
handbook, manufacturer source or equivalent traceable engineering source is
available.

## 9. Priority

Push-jack traceability is classified as:

P1 system-completeness debt

It is not a P0 blocker for:

- W39 four-bar closure
- W40 kinematic validation
- W41 mature linkage optimization

W39 shall therefore return its main effort to deterministic linkage solving.

## 10. Validation boundary

Existing push-jack software tests demonstrate implementation consistency.

They do not establish:

- MT/T 94 verification
- a formal F-JACK engineering evidence chain
- physical validation of a manufactured push jack

No fake traceability shall be added merely to remove PARTIAL status.
