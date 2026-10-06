# W37-D4 OverallSupportDesign Adapter Implementation

## Scope

W37-D4 implements pure mapping adapters from existing engineering result
dictionaries into OverallSupportDesign v1.

Implemented adapters:

- q_need
- required resistance
- column design
- push-jack design

The adapters do not call engineering calculation cores.

## Architecture

Existing deterministic calculation core
→ result dictionary
→ adapter
→ EngineeringParameter / OverallSupportDesign

The adapter layer:

- copies existing values
- attaches units
- attaches origin
- attaches evidence status
- attaches existing Formula IDs
- preserves existing Calculation Record IDs
- aggregates provenance

The adapter layer does not:

- recalculate engineering values
- invent defaults
- fabricate missing engineering data
- create Formula IDs
- create Calculation Records
- persist OverallSupportDesign

## q_need

Mapped formulas:

- p1 -> F-QN-001
- p2 -> F-QN-002
- p3 -> F-QN-003
- q_need -> F-QN-004

Calculated outputs use:

- origin = CALCULATED
- evidence_status = PARTIAL

This does not mean the formulas are unverified.
PARTIAL reflects that complete parameter-level provenance is not yet available
for every input in the OverallSupportDesign lifecycle.

## Required resistance

Mapped formulas:

- control area -> F-QN-005
- base resistance -> F-QN-006
- required working resistance -> F-QN-007

support_efficiency_ks remains:

- origin = USER_INPUT
- evidence_status = EVIDENCE_GAP

Ks is not eta.

Bc is not inferred from canopy_len.

## Column

Mapped existing outputs:

- d_calc_mm
- d_std_mm
- p_actual_kn
- optional setting_ratio_pct
- optional setting_ok

p_actual_kn retains the meaning:

candidate-standard-bore whole-support calculated capacity using column count n
and historical correction coefficient eta.

eta remains:

- USER_INPUT
- EVIDENCE_GAP

A successful calculation does not upgrade eta to VERIFIED.

Existing column calculation record_id may be preserved.

The adapter never creates a Calculation Record.

## Push jack

Mapped existing outputs include:

- push_required_kn
- pressure_mpa
- bore_calc_mm
- bore_candidate_mm
- push_actual_kn
- push_ok
- optional rod/pull/stroke fields
- mt_t94_verified

Current traceability remains intentionally limited:

- no F-JACK Formula ID
- no push-jack Calculation Record
- mt_t94_verified remains False when supplied as False

The adapter does not change these facts.

## Validation

W37-D4 validation includes:

- contract tests
- adapter mapping tests
- provenance de-duplication
- missing-value checks
- no engineering-core import in adapter module
- real q_need smoke test
- real column smoke test
- real push-jack smoke test

Passing software tests demonstrates implementation consistency.
It is not independent physical or manufacturing validation.

## Next step

W37-D5 may build an application-level overall-design workflow/report on top of
the frozen model and adapters.

Existing calculation cores remain unchanged.
