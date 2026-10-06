# W37-D2 OverallSupportDesign v1 Contract

## 1. Purpose

OverallSupportDesign v1 是一次液压支架工程设计项目的统一数据契约。

它用于连接：

Working Condition
→ Support Requirement
→ Reference Support
→ Overall Parameters
→ Hydraulic Components
→ Linkage
→ Structure
→ Engineering Analyses

本契约只定义数据语义与边界。
W37-D2 不新增工程公式，不修改数据库，不改变现有计算结果。

## 2. Contract version

Canonical identifier:

hs.overallDesign.v1

The version field is:

version = 1

hs.designTransfer.v1 remains the existing lightweight page-transfer contract.
It shall not be replaced or expanded into OverallSupportDesign.

## 3. Parameter origin

Every engineering parameter that enters the design lifecycle shall be able to
identify its origin.

Allowed origin values:

- RETRIEVED: retrieved from database, historical case, standard or other source
- CALCULATED: produced by deterministic engineering calculation
- USER_INPUT: explicitly provided or confirmed by the engineer
- AI_PROPOSED: proposed by AI and not treated as verified engineering fact

AI_PROPOSED shall never be silently promoted to CALCULATED or VERIFIED.

## 4. Evidence status

Parameter origin and engineering/evidence status are independent dimensions.

Canonical evidence-status values for v1:

- VERIFIED
- PARTIAL
- EVIDENCE_GAP
- NOT_APPLICABLE

Historical database data_status shall be preserved independently where relevant.
A support_models data_status value shall not be rewritten as parameter
evidence_status.

## 5. Parameter envelope

The canonical conceptual parameter representation is:

- value
- unit
- origin
- evidence_status
- source_text
- formula_ids
- calculation_record_ids
- note

Not every optional trace field must be populated.

NULL or missing evidence shall remain explicit.
Missing values shall not be guessed by AI.

## 6. Top-level structure

OverallSupportDesign v1 contains these top-level sections:

- version
- metadata
- working_condition
- reference_support
- support_requirement
- overall_parameters
- hydraulic_components
- linkage
- structure
- analyses
- provenance
- status

The structure is designed to remain extensible for later linkage optimization,
FEA and AI generative structural optimization.

## 7. Working condition

working_condition stores the engineering condition used for the current design.

Candidate fields include:

- coal_thickness_m
- mining_height_m
- dip_angle_deg
- roof_condition
- roof_class
- floor_condition
- gas_level
- daily_output_t
- working_face_name

Additional q_need-specific inputs remain explicit:

- initial_weighting_step_m
- periodic_weighting_step_m
- control_width_m
- direct_roof_filling_coefficient
- roof_unit_weight_kn_m3
- k1
- dynamic_load_factor_k

control_width_m means verified Bc.

It shall not be inferred silently from canopy_len.

## 8. Reference support

reference_support represents a retrieved historical/model reference.

Candidate fields include:

- support_id
- support_model
- support_type
- working_resistance_kn
- height_min_m
- height_max_m
- manufacturer
- center_distance_m
- support_length_parameter_m
- reference_intensity
- reference_initial_force
- weight_t
- source_text
- data_status

support_length_parameter_m maps from historical canopy_len.

This mapping does not redefine canopy_len as:
- control width Bc
- roof-control distance
- top-beam length
- roof-end distance

reference_initial_force preserves the current historical database meaning and
shall not automatically be treated as a verified whole-support rated setting force.

## 9. Support requirement

support_requirement may contain deterministic results from the active
engineering calculation chain.

Current/future fields include:

- p1_mpa
- p2_mpa
- p3_mpa
- required_support_intensity_mpa
- governing_method
- control_area_m2
- base_resistance_kn
- required_working_resistance_kn
- support_efficiency_ks

q_need is the project controlling required support intensity.

support_efficiency_ks is Ks.
Ks is not historical column eta.

F-QN-005 to F-QN-007 are currently PARTIAL at product-runtime level because
their calculation core and tests exist but no active router/UI caller exists.

## 10. Overall parameters

overall_parameters represents the current project-level design decisions.

Candidate fields include:

- support_type
- design_working_resistance_kn
- design_height_min_m
- design_height_max_m
- center_distance_m
- design_support_intensity_mpa

A project design value may differ from the corresponding reference-support value.

Reference values and design values shall not be collapsed into the same field.

## 11. Hydraulic components

hydraulic_components contains independent engineering subdesigns.

v1 reserves:

- columns
- push_jack
- valve
- pipeline
- pump_station

### columns

The active column calculation result currently includes:

- d_calc_mm
- d_std_mm
- p_actual_kn
- optional setting_ratio_pct
- optional setting_ok

Inputs include:

- p_kn
- n
- p_mpa
- eta
- optional p_set_kn

eta means historical column correction coefficient.
Its physical interpretation remains EVIDENCE_GAP.
eta is not Ks.

### push_jack

Current result may include:

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

No F-JACK Formula ID or push-jack Calculation Record is claimed in v1.

### valve / pipeline / pump_station

These sections are reserved for later work.

Their current state is NOT_IMPLEMENTED.
No engineering values shall be fabricated merely to populate the contract.

## 12. Linkage

linkage is reserved for the later hydraulic-support linkage/kinematics model.

It may later contain:

- geometry parameters
- joint coordinates
- link lengths
- pose results
- motion trajectories
- interference checks
- optimization results

W37-D2 defines no linkage formula and no geometric default.

## 13. Structure

structure is reserved for engineering structural models including:

- top_beam
- shield_beam
- base
- front_link
- rear_link

Historical canopy_len shall not become top_beam.length automatically.

Structure parameters must be defined independently from historical ambiguous
database geometry fields.

## 14. Analyses

analyses is reserved for:

- kinematic analysis
- finite element analysis
- traditional topology optimization
- AI generative structural optimization

AI-generated geometry is a candidate design.

It must not be represented as physically verified until deterministic
engineering validation has been completed.

## 15. Provenance

provenance may reference:

- source text
- database record
- Formula Registry Formula IDs
- Calculation Record IDs
- engineering document
- standard
- literature
- user confirmation

OverallSupportDesign does not replace Formula Registry or Calculation Record.

## 16. Status

OverallSupportDesign may contain module/project status information.

Development-status terminology such as COMPLETE, PARTIAL, EVIDENCE_GAP,
NOT_IMPLEMENTED and INTENTIONALLY_DEFERRED shall not be confused with
parameter evidence_status.

## 17. D2 implementation boundary

W37-D2 freezes the data contract only.

Authorized next step:
W37-D3 may implement the contract as pure application data models and
serialization/validation helpers.

W37-D2 does not authorize:
- new engineering formulas
- database schema migration
- Formula Registry additions
- automatic AI parameter generation
- linkage formulas
- Valve formulas
- CAD generation
- FEA implementation
