# W39-D5 W38-to-W39 Linkage Integration Closeout

## 1. Scope

W39-D5 integrates the W38 canonical LinkageGeometry representation with the
W39 deterministic four-bar closure solver.

The implementation is:

app/services/linkage_closure_integration.py

W39-D5 now supports:

- fresh W38 four-bar geometry derivation
- W38 reference rear-link angle reuse
- W39 reference-branch derivation from explicit B/C/D geometry
- typed ClosureSolverInput construction
- reuse of the existing W39 D3+D4 solver chain
- reference-pose B/C round-trip validation
- explicit numerical tolerance
- input immutability checks

W39-D5 does not implement continuous multi-pose kinematics.

## 2. Integration chain

The frozen integration chain is:

LinkageGeometry

-> derive_geometry(linkage)

-> analyze_reference_pose(linkage)

-> derive_reference_branch(...)

-> ClosureSolverInput

-> solve_closure(...)

-> validate_reference_pose_round_trip(...)

-> ClosureResult

D5 does not duplicate the D3 circle-intersection algorithm.

D5 does not duplicate the D4 reference-branch resolver.

## 3. Fresh geometry is authoritative

For every D5 integration solve, the current A/B/C/D geometry is freshly
processed through:

derive_geometry(linkage)

The resulting DerivedGeometry supplies:

DA = base_pivot_spacing_mm

AB = rear_link_length_mm

BC = shield_beam_effective_length_mm

CD = front_link_length_mm

The existing:

linkage.derived_geometry

is not treated as authoritative solver geometry.

This prevents stale, historical, user-entered, or externally populated derived
values from silently controlling the closure solve.

D5 does not overwrite linkage.derived_geometry.

## 4. Reference rear-link angle

D5 reuses the existing W38:

analyze_reference_pose(linkage)

and takes:

ReferencePoseAnalysis.rear_link_angle_deg

as the W39 driving angle.

No second A-to-B angular convention is introduced.

support_height_mm is not used as the W39 closure-driving variable.

## 5. Reference branch

The W39 reference branch is derived from explicit:

B = reference_pose.rear_link_shield

C = reference_pose.front_link_shield

D = fixed_geometry.front_link_base

using the W39-D4 directed:

B -> D

branch definition.

D5 does not derive W39 branch from:

ReferencePoseAnalysis.assembly_side_signature

Therefore:

SAME_SIDE

and:

OPPOSITE_SIDE

remain separate from:

POSITIVE

and:

NEGATIVE

No direct mapping between those classifications is assumed.

## 6. Degenerate W38 reference boundary

A W38 reference configuration marked:

geometry_degenerate = true

is rejected as the D5 engineering reference baseline.

This does not claim that every mathematically singular four-bar configuration
is invalid.

It means only that W39-D5 requires a stable non-degenerate W38 reference
configuration for its engineering round-trip baseline.

## 7. Typed solver task

D5 constructs one strongly typed ClosureSolverInput containing:

- rear_link_base
- front_link_base
- rear_link_length_mm
- shield_beam_effective_length_mm
- front_link_length_mm
- base_pivot_spacing_mm
- rear_link_angle_deg
- reference_branch
- explicit NumericalTolerance

No unstructured solver dictionary is used.

No missing geometry is filled from historical support fields.

## 8. Support-height boundary

reference_pose.support_height_mm remains stored in the W38 reference pose.

It is not mapped into ClosureSolverInput.

Changing only support_height_mm while preserving A/B/C/D does not change the
D5 closure task.

Support-height-to-pose solving remains outside W39.

## 9. Top-beam boundary

D5 does not consume:

top_beam_interface.shield_top_beam_pivot

or:

top_beam_interface.beam_tip_reference_point

Changing only top_beam_interface does not change the D5 four-bar closure task.

Top-beam kinematics remain outside W39.

## 10. Reference-pose round trip

A successful D5 integrated solve requires a unique selected pose.

The solved:

rear_link_shield

must reproduce the W38 reference B point within numerical tolerance.

The solved:

front_link_shield

must reproduce the W38 reference C point within numerical tolerance.

Point comparison uses Euclidean distance in millimetres.

No display rounding is used for the numerical round-trip check.

## 11. Round-trip tolerance

D5 reuses the W39 scale-aware numerical tolerance principle:

effective_tolerance_mm = max(
    absolute_mm,
    relative * scale_mm
)

The comparison quantity and tolerance both have unit mm.

D5 does not introduce a separate loose display tolerance.

## 12. TWO_SOLUTIONS round trip

For TWO_SOLUTIONS, a successful D5 round trip requires:

selection_status = SELECTED

selected_pose != null

selected_pose.branch = ClosureSolverInput.reference_branch

branch_resolution = REFERENCE_POSE

The selected B/C coordinates must reproduce the supplied reference pose.

The opposite mathematical candidate remains preserved in ClosureResult.

## 13. TANGENT round trip

A reference configuration may have:

reference_branch = null

and still successfully round trip when the mathematical closure is uniquely:

TANGENT

In that case:

selection_status = SELECTED

selected_pose.branch = TANGENT

branch_resolution = TANGENT_UNIQUE

D5 does not invent POSITIVE or NEGATIVE.

## 14. Failed integration states

The D5 reference-pose workflow rejects a final result that cannot provide a
unique selected reference pose.

This includes:

NO_SOLUTION

DEGENERATE

and:

TWO_SOLUTIONS + BRANCH_AMBIGUOUS

D5 exposes the inconsistency instead of inventing a pose.

## 15. Provenance boundary

Fresh W38 dimensions retain:

origin = CALCULATED

evidence_status = PARTIAL

The W38 calculated rear-link angle retains its calculated provenance.

W39 solved B/C coordinates retain:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

A successful software round trip does not promote any value to VERIFIED.

W39-D5 introduces no Formula Registry ID.

W39-D5 creates no Calculation Record.

## 16. Immutability

Task construction and integrated solving do not mutate the supplied
LinkageGeometry.

This includes existing:

- fixed_geometry
- reference_pose
- derived_geometry
- top_beam_interface
- provenance

The complete serialized input remains unchanged.

## 17. Validation achieved

W39-D5 automated tests establish:

- fresh geometry wins over stale stored derived_geometry
- W38 rear-link angle is reused
- W38 assembly signature is not used as W39 branch
- POSITIVE reference-pose round trip
- NEGATIVE reference-pose round trip
- TANGENT reference-pose round trip
- support-height independence
- top-beam independence
- round-trip B mismatch detection
- round-trip C mismatch detection
- provenance preservation
- input immutability
- deterministic repeated solving
- explicit tolerance requirement
- exactly one call into the existing integrated W39 solver

These establish software-level and semantic integration consistency.

## 18. Engineering validation remains pending

The current D5 integration fixtures are synthetic or constructed test
geometries.

They do not establish validation against a traceable real hydraulic-support
mechanism.

ER-001 therefore remains:

ENGINEERING_REFERENCE

NOT_SOLVER_READY

No missing real-support geometry is fabricated to close W39.

## 19. Explicitly outside W39-D5

W39-D5 does not implement:

- support-height-to-pose inversion
- operating-height sweep
- previous-pose continuity
- branch continuity across multiple poses
- automatic branch switching
- top-beam pose
- beam-tip trajectory
- 80 mm beam-tip displacement validation
- interference checking
- linkage optimization
- GA
- PSO
- NSGA-II

## 20. Completion

W39-D5 is complete when:

- its integration contract passes
- its integration service tests pass
- this closeout contract passes
- W39 regression passes
- full-project regression passes
- git diff checks are clean

Continuous multi-pose motion belongs to W40.
