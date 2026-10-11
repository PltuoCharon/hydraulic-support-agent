# W41-D1 Legacy Task Mapping

## 1. Purpose

Map historical development to the V3.0 roadmap (W41-W72).

This mapping preserves historical work. It does not
automatically mark a task as independently verified.

## 2. Historical Baseline

### W33 - Column Strength

Commit: 8f7c1dc

Recorded capability:
- Column strength calculation
- Wall-thickness-related checks
- Euler stability calculation

V3.0 destination:
- W45: evidence and formula review
- W57: detailed column design

Status: HISTORICAL_IMPLEMENTATION
Independent revalidation: PENDING

### W37 - Overall Design Contract

Confirmed W37-D2 commit: b2b336b

Recorded capability:
- Overall design data contract
- Engineering parameter semantics

V3.0 destination:
- W41-D3: parameter schema audit
- W45: overall parameter integration

Status: HISTORICAL_IMPLEMENTATION
Independent revalidation: PENDING

### W38 - Linkage Geometry

Existing evidence directory:
docs/evidence/w38/

Recorded capability:
- Linkage geometry model
- Coordinate system
- Reference pose and geometry derivation

V3.0 destination:
- W41: optimization domain contract
- W43: engineering geometry completion
- W63: parametric CAD integration

Status: HISTORICAL_IMPLEMENTATION
Independent revalidation: PENDING

### W39 - Deterministic Closure

Closeout commit: eb7e85a

Recorded capability:
- Four-bar deterministic closure
- Assembly branch handling
- Synthetic mathematical benchmarks

V3.0 destination:
- W41: unified evaluator
- W42: optimization baseline
- W44: engineering kinematics verification

Status: HISTORICAL_IMPLEMENTATION
Independent revalidation: PENDING

### W40 - Continuous Motion

Closeout commit: 120900a

Recorded capability:
- Rear-link-angle sweep
- B/C trajectory
- Shield rigid pose
- Shield-top-beam joint E trajectory

Historical test record:
1081 passed, 1 warning.

V3.0 destination:
- W41: optimization evaluator integration
- W43: top-beam pose and height mapping
- W44: full operating-domain verification
- W64: 3D motion visualization

Status: HISTORICAL_IMPLEMENTATION
Independent revalidation: PENDING

## 3. Unresolved Engineering Gaps

- No solver-ready engineering reference: ER-001
- Optimization design variable bounds not frozen
- No confirmed GA/PSO/NSGA-II implementation
- Rear-link-angle to support-height mapping missing
- Independently constrained top-beam pose missing
- Physical beam-tip T trajectory missing
- Full operating-height 80 mm verification unavailable

Do not invent missing geometry, loads or dimensions.

## 4. Historical Evidence Gaps

Earlier task records are not all complete.

W34-W36 and other missing daily records require
further evidence reconciliation during W41-D2.

Missing records must not be reconstructed as
completed work without supporting evidence.

## 5. Baseline Decision

W33, W37 and W40 belong to one Git ancestry chain.

Reuse existing computation modules.

Do not rebuild historical modules without an
identified defect or a verified integration need.

G0 baseline verification remains pending W41-D2.

## 6. Evidence Note

This mapping is based on historical records and
W41-D1 terminal inspection.

It is not an independent physical verification.
