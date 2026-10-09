# W39-D1 Four-Bar Closure Benchmark Policy

## 1. Purpose

W39 separates mathematical software benchmarks from hydraulic-support
engineering reference cases.

This prevents convenient artificial geometry from being presented as physical
validation.

## 2. SYNTHETIC_MATH

SYNTHETIC_MATH cases are deliberately constructed mathematical examples.

They may be used to verify:

- point-B calculation
- circle-intersection multiplicity
- tangency
- no-solution behavior
- coincident-circle degeneracy
- branch-sign calculation
- numerical-tolerance behavior

They are not hydraulic-support design data.

They do not validate the physical correctness of a hydraulic-support
mechanism.

Current registered synthetic cases are:

- SM-001 TWO_SOLUTIONS
- SM-002 TANGENT
- SM-003 separated-circle NO_SOLUTION
- SM-004 contained-circle NO_SOLUTION
- SM-005 coincident equal-circle DEGENERATE
- SM-006 coincident unequal-circle NO_SOLUTION

## 3. ENGINEERING_REFERENCE

An ENGINEERING_REFERENCE case must have traceable hydraulic-support geometry.

A solver-ready engineering reference requires, at minimum:

- fixed pivot A
- fixed pivot D
- rear-link length AB
- shield linkage length BC
- front-link length CD
- one traceable reference configuration or branch definition
- source provenance

If equivalent information is supplied as coordinates, those coordinates must
also preserve provenance.

Historical example dimensions alone are insufficient when they do not define
the complete canonical geometry.

## 4. Current engineering-reference status

At W39-D1, no audited engineering reference case is solver-ready.

ER-001 is intentionally registered as:

NOT_SOLVER_READY

The project shall preserve this missing-data state instead of fabricating
pivot coordinates or a reference branch.

W38 historical literature/example geometry remains research evidence only.

It does not become a project default.

## 5. Promotion rule

An ENGINEERING_REFERENCE case may move to READY only after:

1. source material is traceable
2. parameter semantics are unambiguous
3. all solver-required geometry is available
4. units are explicit
5. configuration/branch information is sufficient
6. provenance is recorded

Passing SYNTHETIC_MATH tests shall never promote an engineering case to
verified status.

## 6. W39 usage

W39 closure implementation shall first pass all SYNTHETIC_MATH cases.

Engineering comparison begins only when at least one ENGINEERING_REFERENCE case
becomes solver-ready.

Software validation and engineering validation remain separate.
