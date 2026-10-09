# W39 Four-Bar Deterministic Closure Closeout

## 1. W39 objective

W39 establishes the deterministic single-pose four-bar closure foundation
required before W40 continuous operating-range kinematics.

The W39 scope is:

explicit geometry
-> mathematical closure
-> explicit engineering branch resolution
-> W38/W39 reference-pose integration

W39 does not implement continuous motion trajectories.

## 2. D1: closure semantics and benchmark boundary

W39-D1 froze:

- canonical A/B/C/D topology
- rear_link_angle_deg as the W39 driving variable
- NO_SOLUTION
- TANGENT
- TWO_SOLUTIONS
- DEGENERATE
- POSITIVE / NEGATIVE / TANGENT candidate branch semantics
- reference-branch selection semantics
- synthetic mathematical benchmark policy
- PushJack traceability audit

The W39 branch is defined relative to directed B -> D.

It is not the W38 SAME_SIDE / OPPOSITE_SIDE assembly signature.

## 3. D2: strongly typed closure model

W39-D2 introduced:

app/models/linkage_closure.py

The model layer freezes:

ClosureSolverInput

NumericalTolerance

ClosureCandidate

ClosureSelectedPose

ClosureSolverProvenance

ClosureResult

The models reject contradictory closure and selection states before solver
execution.

No W39 Formula Registry ID or Calculation Record is fabricated.

## 4. D3: deterministic mathematical closure

W39-D3 introduced deterministic numerical closure solving in:

app/services/linkage_closure.py

D3 implements:

rear-link angle -> point B

fixed-base consistency validation

two-circle closure classification

candidate C generation

candidate branch classification

The synthetic benchmark results are frozen as:

SM-001 -> TWO_SOLUTIONS

SM-002 -> TANGENT

SM-003 -> NO_SOLUTION

SM-004 -> NO_SOLUTION

SM-005 -> DEGENERATE

SM-006 -> NO_SOLUTION

TWO_SOLUTIONS remains mathematically unresolved at D3.

## 5. D4: engineering reference-branch resolution

W39-D4 adds reference-branch resolution on top of the D3 mathematical result.

For TWO_SOLUTIONS:

reference_branch = POSITIVE

selects the POSITIVE candidate.

reference_branch = NEGATIVE

selects the NEGATIVE candidate.

No reference branch means:

BRANCH_AMBIGUOUS

D4 selects by explicit branch semantics.

It does not select by candidate list index, X coordinate, Y coordinate, or
visual plausibility.

Both mathematical candidates remain preserved after engineering selection.

## 6. D5: W38-to-W39 integration

W39-D5 introduced:

app/services/linkage_closure_integration.py

The integration chain is:

LinkageGeometry

-> fresh derive_geometry(linkage)

-> analyze_reference_pose(linkage)

-> derive_reference_branch(...)

-> ClosureSolverInput

-> solve_closure(...)

-> reference-pose round-trip validation

For a successful reference fixture, the solved B/C coordinates reproduce the
explicit W38 reference B/C coordinates within W39 numerical tolerance.

Stored linkage.derived_geometry is not used as authoritative solver geometry.

## 7. W39 numerical policy

W39 uses explicit scale-aware distance tolerance:

effective_tolerance_mm = max(
    absolute_mm,
    relative * scale_mm
)

Tolerance is computational infrastructure.

It is not a hydraulic-support engineering design parameter.

Distance-like comparisons are performed in millimetres.

Raw mm^2 cross products are not directly compared against an mm tolerance.

## 8. Provenance boundary

Calculated W39 geometry uses:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

Passing deterministic software tests does not automatically produce VERIFIED
engineering evidence.

W39 introduces no new Formula Registry ID.

W39 creates no Calculation Record.

## 9. PushJack status

The W39-D1 PushJack audit retains the current deterministic PushJack
calculation.

PushJack remains traceability-partial.

No F-JACK Formula Registry ID is created in W39.

No PushJack Calculation Record is fabricated.

PushJack evidence debt remains a separate follow-up item and is not a blocker
for the W39 four-bar closure foundation.

## 10. Engineering-reference status

The current W39 executable benchmark set proves deterministic mathematics and
software behavior.

The D5 reference-pose fixtures prove internal integration consistency.

They do not independently validate a real hydraulic-support mechanism.

ER-001 remains:

ENGINEERING_REFERENCE

NOT_SOLVER_READY

because a complete traceable real-support A/B/C/D geometry and reference branch
has not yet been frozen.

W39 does not fabricate missing engineering-reference geometry.

## 11. What W39 now guarantees

At W39 closeout the project can deterministically:

- accept explicit canonical four-bar geometry
- calculate B from rear-link angle
- distinguish zero, one, two, and degenerate mathematical closures
- generate deterministic C candidates
- classify POSITIVE and NEGATIVE branches
- preserve mathematical ambiguity when reference evidence is unavailable
- select the explicit engineering reference branch when available
- integrate W38 explicit reference geometry into W39 solving
- reproduce a valid reference pose through a numerical round trip
- preserve provenance and input immutability

These are deterministic software guarantees.

They are not physical certification.

## 12. Explicitly not completed in W39

W39 does not provide:

- support-height-to-pose mapping
- operating-height sweep
- previous-pose continuity
- branch continuity over motion
- automatic branch switching policy
- pivot trajectories
- top-beam pose propagation
- beam-tip trajectory
- beam-tip horizontal displacement
- MT/T 556 80 mm operating-range validation
- interference checking
- linkage optimization
- GA
- PSO
- NSGA-II

## 13. W40 entry condition

W40 starts from the frozen W39 single-pose closure solver.

W40 shall focus on continuous operating-height kinematics.

The planned W40 chain is:

selected reference branch
-> admissible motion parameter range
-> multiple deterministic poses
-> continuity-preserving branch tracking
-> pivot trajectories
-> top-beam interface propagation
-> beam-tip trajectory
-> horizontal beam-tip displacement
-> 80 mm validation

W40 shall not silently jump between POSITIVE and NEGATIVE branches.

W40 shall not claim support-height inversion until the geometric relationship
between support height and the mechanism/top-beam configuration is explicitly
defined.

## 14. Optimization boundary

Four-bar optimization does not belong to W39.

GA, PSO and NSGA-II remain planned for the later optimization baseline stage.

W39 supplies the deterministic mechanism evaluator required before such
optimization is meaningful.

## 15. W39 closeout conclusion

W39 closes the project's single-pose deterministic four-bar foundation.

The software now separates:

mathematical closure

from:

engineering branch selection

and connects both to the existing W38 canonical geometry model.

The next research step is continuous kinematic behavior across the operating
range, not additional single-pose closure semantics.
