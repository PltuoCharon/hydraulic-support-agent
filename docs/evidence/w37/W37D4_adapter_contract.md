# W37-D4 OverallSupportDesign Adapter Contract

## 1. Purpose

W37-D4 defines the mapping boundary between existing engineering calculation
results and OverallSupportDesign v1.

The adapter layer converts already-computed engineering results into the
canonical design data model.

The adapter layer is not an engineering calculation layer.

## 2. Core rule

Adapter MAY:

- copy existing calculation outputs
- attach engineering units
- attach parameter origin
- attach evidence status
- attach Formula Registry IDs
- attach Calculation Record IDs
- preserve source text
- preserve explicit user inputs

Adapter MUST NOT:

- recalculate engineering values
- invent missing values
- introduce engineering defaults
- modify existing calculation algorithms
- reinterpret physical semantics
- silently promote AI_PROPOSED values
- map canopy_len to Bc
- map canopy_len to top-beam length
- map eta to Ks
- create nonexistent Formula IDs
- create nonexistent Calculation Record IDs


## 3. q_need adapter

Source:

app.services.calc.q_need.estimate()

Current result fields:

- p1_mpa
- p2_mpa
- p3_mpa
- q_need_mpa
- governing
- inputs
- rule
- source

Canonical mapping:

- p1_mpa -> support_requirement.p1_mpa
- p2_mpa -> support_requirement.p2_mpa
- p3_mpa -> support_requirement.p3_mpa
- q_need_mpa -> support_requirement.required_support_intensity_mpa
- governing -> support_requirement.governing_method

Formula mapping:

- p1_mpa -> F-QN-001
- p2_mpa -> F-QN-002
- p3_mpa -> F-QN-003
- required_support_intensity_mpa -> F-QN-004

All four numerical outputs have origin CALCULATED.

The adapter copies result values.
It shall not call p1_load(), p2_weighting_step(), p3_statistical() or estimate().

q_need keeps the project semantic:
project controlling required support intensity.

It shall not automatically be renamed standard Ps.


## 4. Required-resistance adapter

Source:

app.services.calc.resistance.required_resistance()

Current result fields:

- control_area_m2
- base_resistance_kn
- required_working_resistance_kn
- support_efficiency
- formula_ids
- source
- note

Canonical mapping:

- control_area_m2 -> support_requirement.control_area_m2
- base_resistance_kn -> support_requirement.base_resistance_kn
- required_working_resistance_kn
  -> support_requirement.required_working_resistance_kn
- support_efficiency
  -> support_requirement.support_efficiency_ks

Formula mapping:

- control_area_m2 -> F-QN-005
- base_resistance_kn -> F-QN-006
- required_working_resistance_kn -> F-QN-007

support_efficiency_ks preserves Ks semantics.

Ks shall not be mapped to historical column eta.

Bc remains an explicit verified control-width input to the calculation core.
The adapter shall not derive Bc from historical canopy_len.

The current resistance calculation core remains product-runtime PARTIAL.
Using its adapter does not silently upgrade its runtime implementation status.


## 5. Column adapter

Source:

app.services.calc.column.design()

Current calculation outputs:

- d_calc_mm
- d_std_mm
- p_actual_kn
- optional setting_ratio_pct
- optional setting_ok
- inputs
- source

Canonical target:

hydraulic_components.columns

Output mapping:

- d_calc_mm -> columns.d_calc_mm
- d_std_mm -> columns.d_std_mm
- p_actual_kn -> columns.p_actual_kn
- setting_ratio_pct -> columns.setting_ratio_pct
- setting_ok -> columns.setting_ok

Formula mapping:

- bore design -> F-COL-001
- calculated force/capacity relation -> F-COL-002
- optional setting ratio -> F-COL-003

p_actual_kn means candidate-standard-bore whole-support calculated capacity
after applying column count n and historical correction coefficient eta.

It shall not be labelled single-column theoretical thrust.

Column adapter shall preserve calculation_record_ids when an actual
column_design record_id exists.

The adapter shall not create a record itself.


## 6. Column input trace

The current ColumnDesign model stores calculation inputs under the inputs field.

W37-D4 shall preserve input trace using EngineeringParameter-shaped payloads.

For an engineering run:

- p_kn: preserve actual upstream origin when known
- n: USER_INPUT unless an independently traced upstream source exists
- p_mpa: USER_INPUT unless an independently traced upstream source exists
- eta: USER_INPUT + EVIDENCE_GAP
- p_set_kn: preserve actual origin when known

Historical eta means historical column correction coefficient.

eta shall not be described as:

- hydraulic efficiency
- mechanical efficiency
- cylinder efficiency
- support efficiency
- Ks

Successful column calculation does not upgrade eta to VERIFIED.


## 7. Push-jack adapter

Source:

app.services.calc.push_jack.push_jack_design()

Canonical target:

hydraulic_components.push_jack

Mapping may include:

- push_required_kn
- pressure_mpa
- bore_calc_mm
- bore_candidate_mm
- push_actual_kn
- push_ok
- rod_mm
- pull_required_kn
- pull_actual_kn
- pull_ok
- stroke_mm
- mt_t94_verified

Calculated outputs are marked CALCULATED.

Explicit user-provided engineering inputs remain USER_INPUT unless their
actual upstream provenance says otherwise.

mt_t94_verified shall be copied without reinterpretation.

Current value False shall remain False.

W37-D4 shall not create F-JACK Formula IDs.

W37-D4 shall not create a push-jack Calculation Record.

The candidate bore series shall not be represented as independently verified
MT/T 94 compliance.


## 8. Missing and optional values

Missing optional source fields remain absent or None.

The adapter shall not fabricate:

- rod diameter
- stroke
- pull requirement
- setting force
- linkage geometry
- Valve data
- Pipeline data
- Pump data
- structural geometry
- FEA results

## 9. Provenance aggregation

Adapters may append existing source text, Formula IDs and Calculation Record IDs
to OverallSupportDesign.provenance.

Duplicate provenance entries may be de-duplicated.

Provenance aggregation shall not alter the underlying engineering values.

## 10. Mutation boundary

The D4 implementation may update an OverallSupportDesign object with mapped
results.

It shall not persist the design to MySQL.

It shall not write sessionStorage.

Persistence and API lifecycle are outside the D4 adapter scope.

## 11. D4 implementation target

After this contract is frozen, W37-D4 implementation may add a pure adapter
module for:

- q_need
- required resistance
- column design
- push-jack design

The adapter implementation must consume result dictionaries.

It must not call the engineering calculation cores internally.

## 12. D4 evidence mapping policy

For q_need and required-resistance calculated outputs:

- origin = CALCULATED
- evidence_status = PARTIAL

Reason:

An active Formula Registry entry proves the formula mapping used by the
project, but the result dictionary alone does not prove complete
parameter-level provenance for every engineering input.

Therefore the adapter shall not mark these design values VERIFIED merely
because their Formula IDs are active.

For support_efficiency_ks in the current D4 adapter:

- origin = USER_INPUT
- evidence_status = EVIDENCE_GAP

unless an independently traced upstream parameter source is introduced later.

This policy may be upgraded later only when parameter-level provenance is
available. The numerical calculation formula itself is not changed by this
status policy.
