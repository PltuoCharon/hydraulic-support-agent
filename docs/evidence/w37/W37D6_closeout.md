# W37-D6 Overall Design Foundation Closeout

## 1. Week objective

W37 migrated the project from isolated engineering calculation functions
toward a unified overall hydraulic-support design architecture.

No new engineering formula was introduced merely for W37 integration.

The main engineering-data path established in W37 is:

engineering data
→ deterministic calculation result
→ adapter
→ OverallSupportDesign v1
→ structured summary
→ readable engineering report

## 2. Frozen contract

Contract identifier:

hs.overallDesign.v1

The design object separates:

- working condition
- reference support
- support requirement
- overall design parameters
- hydraulic components
- linkage
- structure
- analyses
- provenance
- project status

Historical reference values, deterministic requirement values and current
design decisions remain semantically separate.

They shall not be automatically collapsed into one value.

## 3. Parameter origin and evidence

W37 freezes four parameter origins:

- RETRIEVED
- CALCULATED
- USER_INPUT
- AI_PROPOSED

Parameter origin and engineering evidence status are independent.

Evidence status values are:

- VERIFIED
- PARTIAL
- EVIDENCE_GAP
- NOT_APPLICABLE

AI_PROPOSED shall not silently become CALCULATED or VERIFIED.

## 4. Geometry semantics

Historical database canopy_len maps only to:

support_length_parameter_m

Its current report/UI semantic is:

支护长度参数

Historical canopy_len is not automatically interpreted as:

- Bc / control width
- top-beam length
- roof-control distance

Bc remains an explicit engineering input where required.

## 5. Engineering semantic boundaries

q_need remains the project controlling required support intensity.

It is not automatically renamed standard Ps.

support_efficiency_ks remains Ks.

Ks is not historical column eta.

Historical column eta remains a historical correction coefficient whose
physical interpretation still has an evidence gap.

Successful deterministic calculation does not upgrade eta to VERIFIED.

Column p_actual_kn retains the meaning:

candidate-standard-bore whole-support calculated capacity using column count n
and historical correction coefficient eta.

## 6. Adapter layer

W37 implements pure result adapters for:

- q_need
- required resistance
- column design
- push-jack design

Adapters consume already-computed result dictionaries.

Adapters do not call engineering calculation cores internally.

Adapters may attach:

- units
- parameter origin
- evidence status
- existing Formula IDs
- existing Calculation Record IDs
- source and provenance

Adapters do not:

- recalculate engineering values
- invent missing engineering values
- create engineering defaults
- create nonexistent Formula IDs
- create nonexistent Calculation Records

## 7. Push-jack boundary

Push-jack engineering traceability remains PARTIAL.

Current facts remain:

- no F-JACK Formula ID
- no push-jack Calculation Record
- mt_t94_verified remains False when the source result is False
- candidate bore selection is not represented as independently verified
  MT/T 94 compliance

W37 does not fabricate missing traceability.

## 8. Overall-design reporting

W37 implements:

- structured Python summary
- readable Markdown engineering report

The report distinguishes:

- historical/reference value
- calculated requirement value
- current design value

For working resistance:

reference_support.working_resistance_kn

is semantically different from:

support_requirement.required_working_resistance_kn

and neither automatically becomes:

overall_parameters.design_working_resistance_kn

The report performs no engineering calculation.

## 9. Capability status

### COMPLETE

- OverallSupportDesign v1 contract
- Pydantic overall-design model
- parameter-origin representation
- evidence-status representation
- q_need result adapter
- required-resistance result adapter
- column result adapter
- push-jack result adapter
- provenance aggregation
- structured overall-design summary
- Markdown engineering report

### PARTIAL

- required-resistance product runtime
  - F-QN-005 to F-QN-007 calculation core and tests exist
  - no active product router/UI caller is currently confirmed

- column engineering evidence
  - deterministic implementation exists
  - historical eta physical semantics still have an evidence gap

- push-jack engineering evidence
  - deterministic implementation exists
  - Formula Registry and Calculation Record traceability remain deferred

### NOT_IMPLEMENTED

- OverallSupportDesign database persistence
- OverallSupportDesign API lifecycle
- OverallSupportDesign UI
- automatic AI overall-parameter generation
- Valve engineering design
- Pipeline engineering design
- Pump-station engineering design
- linkage parameter model
- kinematics
- linkage optimization
- structural parameter model
- FEA
- conventional topology optimization
- AI generative structural optimization

## 10. W37 validation

Final W37 validation includes:

- Python full regression
- W37 targeted tests
- frontend Vite production build
- real Playwright browser E2E
- Git diff checks

Validated before final closeout:

- Python baseline after D5: 421 passed
- known warning: Starlette/httpx TestClient deprecation only
- frontend production build: PASS
- frontend chunk-size warning: non-blocking
- Playwright E2E: 1 passed

The Playwright closeout exposed an infrastructure working-directory bug.

The backend webServer command previously started Uvicorn from the web
directory, while SettingsConfigDict(env_file=".env") resolves the environment
file relative to the process working directory.

The Playwright backend command was corrected to start from the project root:

cd .. && PYTHONPATH=. venv/bin/python -m uvicorn app.main:app

A regression test now protects this startup boundary.

Software-test success demonstrates implementation consistency.

It does not constitute independent physical, manufacturing, standard-compliance
or field validation.

## 11. Research route after W37

Priority P0 research route:

working condition
→ overall parameters
→ linkage parametric model
→ kinematics
→ mature optimization algorithms
→ structural parameter model
→ FEA
→ conventional topology-optimization baseline
→ AI generative structural optimization
→ deterministic physical validation

Priority P1 system-completeness route:

column
→ push-jack traceability
→ Valve
→ Pipeline
→ Pump station

P1 shall not indefinitely block the P0 thesis research route.

## 12. W38 entry

W38 starts two controlled branches.

P0:

- audit linkage variables
- audit hydraulic-support geometry semantics
- define linkage parameter contract
- begin a parametric linkage model
- reserve mature optimization methods for implementation support rather than
  claiming them as primary research novelty

P1:

- audit push-jack evidence gaps
- audit candidate F-JACK evidence mapping
- audit Valve evidence before implementing Valve formulas

No Formula ID shall be created without evidence review.

No unverified linkage geometry default shall be introduced merely to make the
model run.
