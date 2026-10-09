# W39-D1 Four-Bar Closure Semantics Closeout

## 1. Scope

W39-D1 freezes the mathematical, evidence and validation boundaries required
before implementation of a deterministic hydraulic-support four-bar closure
solver.

W39-D1 does not implement the numerical solver.

Completed W39-D1 work includes:

- four-bar closure mathematical contract
- closure multiplicity semantics
- candidate branch semantics
- reference-branch selection semantics
- numerical-tolerance requirements
- synthetic mathematical benchmark registry
- engineering-reference benchmark policy
- push-jack traceability side-line audit

## 2. Frozen canonical mechanism

The W38 canonical topology remains unchanged:

A = rear_link_base

B = rear_link_shield

C = front_link_shield

D = front_link_base

Rigid-link lengths are:

AB = rear_link_length_mm

BC = shield_beam_effective_length_mm

CD = front_link_length_mm

DA = base_pivot_spacing_mm

The canonical closed chain is:

A -> B -> C -> D -> A

Top-beam geometry remains outside the canonical four-bar closure.

## 3. First solver variable

The first W39 deterministic solver shall use:

rear_link_angle_deg

as the independent motion variable.

Given A, AB and rear_link_angle_deg, point B is deterministic.

support_height_mm is not yet a pose-solving variable.

W39-D1 does not define a support-height-to-four-bar-pose mapping.

## 4. Point-C closure semantics

Point C must satisfy:

distance(B, C) = BC

distance(D, C) = CD

Therefore C is a two-circle intersection problem.

Frozen closure states are:

NO_SOLUTION

TANGENT

TWO_SOLUTIONS

DEGENERATE

Coincident equal circles are DEGENERATE because infinitely many mathematical
C points exist.

They are not TWO_SOLUTIONS.

No arbitrary C point may be created for a degenerate case.

## 5. Branch semantics

For TWO_SOLUTIONS, each C candidate is classified using the signed 2D cross
product relative to directed line:

B -> D

Candidate branch classes are:

POSITIVE

NEGATIVE

TANGENT

These W39 branch classes are not the same concept as the W38:

SAME_SIDE
OPPOSITE_SIDE
DEGENERATE

assembly-side signature.

W38 classifies moving pivots relative to A -> D.

W39 classifies candidate C relative to B -> D.

The two classifiers shall remain separate.

W39 does not yet rename candidate branches OPEN or CROSSED.

## 6. Branch selection

When a complete non-degenerate W38 reference pose is available, its reference
B, reference C and fixed D may establish the reference W39 branch sign.

For TWO_SOLUTIONS, a future solver shall select the candidate matching the
reference branch.

It shall not select a candidate because it:

- is returned first
- has a preferred X coordinate
- has a preferred Y coordinate
- appears visually plausible

If two candidates exist and reference branch information is insufficient,
selection is BRANCH_AMBIGUOUS.

The solver shall not guess.

Closure multiplicity and candidate selection remain separate concepts.

## 7. Numerical boundary

W39 requires a centralized, scale-aware numerical tolerance policy containing
both absolute and relative tolerance concepts.

Numerical tolerance is computational infrastructure.

It is not a hydraulic-support engineering design parameter.

The strongly typed tolerance model belongs to W39-D2.

## 8. Benchmark boundary

W39-D1 registers two benchmark classes:

SYNTHETIC_MATH

and:

ENGINEERING_REFERENCE

Six SYNTHETIC_MATH cases currently cover:

- TWO_SOLUTIONS
- external TANGENT
- separated-circle NO_SOLUTION
- contained-circle NO_SOLUTION
- coincident equal-circle DEGENERATE
- coincident unequal-circle NO_SOLUTION

Synthetic benchmarks validate mathematics and software behavior only.

Passing a SYNTHETIC_MATH benchmark does not constitute hydraulic-support
engineering validation.

They do not constitute hydraulic-support engineering validation.

ER-001 is currently:

ENGINEERING_REFERENCE
NOT_SOLVER_READY

No audited engineering reference currently contains sufficient complete
traceable canonical geometry and branch information for solver validation.

Missing engineering geometry remains missing.

It shall not be fabricated.

## 9. Historical-data boundary

W39 shall not complete linkage geometry using:

- canopy_len
- center_dist
- historical beam_length
- historical roof_end_distance
- historical example dimensions

Historical examples may remain research evidence but are not project defaults.

## 10. Provenance boundary

Future W39 solved coordinates shall use:

origin = CALCULATED

evidence_status = PARTIAL

The result is mathematically derived.

That does not independently verify the physical source geometry.

W39-D1 introduces no Formula Registry ID.

W39-D1 introduces no Calculation Record.

AI_PROPOSED geometry is not automatically promoted to VERIFIED.

## 11. Push-jack side-line decision

The W39-D1 system-completeness audit confirms that the existing push-jack
calculation core is usable and shall not be rewritten during W39.

The current core supports:

- push demand
- explicit pressure
- candidate bore calculation
- candidate-bore push-force check
- optional rod diameter
- optional pull-force check
- optional explicit stroke

Current boundaries remain:

mt_t94_verified = false

formula_ids = []

calculation_record_ids = []

No active F-JACK Formula ID exists.

Push-jack traceability remains PARTIAL.

This is classified as P1 system-completeness evidence debt and is not a P0
blocker for W39 linkage research.

## 12. Explicitly not implemented

At W39-D1 closeout, the following are still NOT IMPLEMENTED:

- strongly typed closure solver models
- numerical point-B solver
- numerical circle-intersection solver
- closure candidate generation
- reference-branch candidate selection
- continuous pose tracking
- support-height-driven pose solving
- operating-range trajectory analysis
- beam-tip trajectory
- 80 mm beam-tip validation
- linkage optimization

## 13. W39-D2 entry condition

W39-D2 shall introduce strongly typed data models for:

- closure solver input
- numerical tolerance
- closure multiplicity
- candidate branch sign
- closure candidate
- selection status
- closure result
- selected pose
- solver provenance

W39-D2 remains a model and contract layer.

W39-D2 shall not yet implement the numerical closure solver.

Numerical closure implementation begins only after the D2 models are frozen.

## 14. Validation status

W39-D1 targeted tests validate the frozen contract, mathematical benchmark
registry and push-jack traceability audit.

Passing these tests demonstrates software and contract consistency.

It does not constitute physical validation of a hydraulic-support linkage.

The next engineering-validation milestone requires at least one solver-ready
ENGINEERING_REFERENCE case with traceable geometry.
