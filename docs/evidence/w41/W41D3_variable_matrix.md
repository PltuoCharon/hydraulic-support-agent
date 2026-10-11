# W41-D3 Design Variable Matrix

## 1. Purpose

Define a minimal V1 optimization design vector
for synthetic four-bar mechanism evaluation.

## 2. Frozen V1 Candidate Design Vector

Order is fixed:

1. rear_link_length_mm (AB)
2. shield_beam_effective_length_mm (BC)
3. front_link_length_mm (CD)

All three values use millimetres.

## 3. Fixed Configuration

- Rear-link base A: normalized origin (0, 0)
- Front-link base D: fixed input coordinates
- Base pivot spacing AD: derived or validated
  from fixed pivot coordinates
- Rear-link angle: operating-condition input
- W39 reference_branch: explicit solver configuration and source/rule
- NumericalTolerance: explicit computational configuration

Do not optimize D coordinates and AD spacing
as independent, inconsistent variables.

## 4. Synthetic Mathematical Domain

Domain identifier: SYNTHETIC_MATH

Reference example: W39 SM-001

- A = (0, 0) mm
- D = (8, 0) mm
- AB = 5 mm
- BC = 5 mm
- CD = 5 mm
- Rear-link angle = 0 degrees

These are artificial numerical test dimensions,
not real hydraulic-support engineering data.

Any test bounds must explicitly identify
themselves as synthetic test bounds.

## 5. Engineering Reference Domain

Domain identifier: ENGINEERING_REFERENCE

ER-001 status: NOT_SOLVER_READY

No verified engineering optimization bounds
are available for ER-001.

Do not fabricate dimensions or mark the
engineering reference as verified.

## 6. Validation Requirements

- Fixed variable order and names
- Finite numeric values
- Positive physical lengths
- Explicit millimetre units
- Valid lower and upper bounds
- Values within declared bounds
- Consistent fixed pivot geometry
- No hidden replacement of invalid values
- No fabricated solution for infeasible geometry

## 7. V1 Scope

Today: design vector and data validation.

Not included today:
- GA or PSO
- Objective functions
- Physical height mapping
- Top-beam T trajectory
- Engineering 80 mm verification

## 8. Source-Confirmed V1 Boundary

Confirmed against W38/W39/W40 source at HEAD 999d7b4.
AB/BC/CD are independent W41 candidate inputs subject to closure feasibility.
W38 reference geometry remains coordinate-first with derived lengths.
Use the new candidate adapter, never overwrite W38 derived_geometry.
AD is coordinate-derived; optional declared AD is consistency-checked.
W38 assembly-side signatures are not W39 branch labels.
ENGINEERING_REFERENCE remains blocked from V1 evaluation.
See W41D3_design_vector_contract.md for implemented validation, numeric
coercion, duplicate-key, near-zero and arithmetic-capacity policies.
