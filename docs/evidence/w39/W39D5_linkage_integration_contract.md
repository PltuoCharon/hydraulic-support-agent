# W39-D5 W38-to-W39 Linkage Integration Contract

## 1. Objective

W39-D5 integrates the W38 canonical LinkageGeometry representation with the
W39 deterministic closure solver.

The target integration service is:

app/services/linkage_closure_integration.py

W39-D5 shall bridge:

W38 explicit geometry

to:

W39 strongly typed closure solving

without changing the mathematical behavior frozen in W39-D3 or the branch
semantics frozen in W39-D4.

The primary D5 invariant is a deterministic reference-pose round trip:

explicit W38 reference pose
-> derive mechanism geometry
-> derive rear-link angle
-> derive W39 reference branch
-> build ClosureSolverInput
-> solve closure
-> recover the same reference B/C pose within numerical tolerance


## 2. Public integration boundary

W39-D5 shall provide an operation equivalent to:

build_closure_task_from_linkage(
    *,
    linkage: LinkageGeometry,
    tolerance: NumericalTolerance
) -> ClosureSolverInput

W39-D5 shall also provide:

validate_reference_pose_round_trip(
    *,
    linkage: LinkageGeometry,
    task: ClosureSolverInput,
    result: ClosureResult
) -> None

and:

solve_linkage_reference_pose(
    *,
    linkage: LinkageGeometry,
    tolerance: NumericalTolerance
) -> ClosureResult

NumericalTolerance is required explicitly.

D5 shall not introduce a hidden default solver tolerance.


## 3. Required W38 source geometry

A D5 reference-pose solve requires:

fixed_geometry.rear_link_base

fixed_geometry.front_link_base

reference_pose.rear_link_shield

reference_pose.front_link_shield

reference_pose.support_height_mm remains part of the W38 reference-pose record,
but it is not the W39 closure-driving variable.

If front_link_base is missing, D5 shall fail explicitly.

If reference_pose is missing, D5 shall fail explicitly.

D5 shall not fill missing geometry from:

- canopy_len
- center_dist
- historical support examples
- top-beam geometry
- default dimensions


## 4. Fresh geometry derivation is authoritative

D5 shall call the existing W38:

derive_geometry(linkage)

for the current integration solve.

The resulting fresh DerivedGeometry is the authoritative geometric input for
constructing ClosureSolverInput.

D5 shall not use:

linkage.derived_geometry

as the authoritative solver geometry merely because values are already stored
there.

The stored derived_geometry object may represent an earlier calculation,
external data, user input, or stale state.

D5 shall not silently overwrite linkage.derived_geometry.

The W38 LinkageGeometry object shall remain unchanged.


## 5. Required freshly derived dimensions

The fresh W38 derivation must provide:

base_pivot_spacing_mm

rear_link_length_mm

shield_beam_effective_length_mm

front_link_length_mm

These correspond to:

DA

AB

BC

CD

respectively.

If any required derived dimension is missing, D5 shall fail explicitly.

D5 shall not replace a missing derived dimension with zero.

D5 shall not fall back to stored historical dimensions.

Positive-value enforcement remains consistent with the W39-D2
ClosureSolverInput model.


## 6. Rear-link driving angle

D5 shall call the existing W38:

analyze_reference_pose(linkage)

and use:

ReferencePoseAnalysis.rear_link_angle_deg

as the W39 solver driving angle.

D5 shall not independently create a second A-to-B angle convention.

If rear_link_angle_deg is unavailable, D5 shall fail explicitly.

The W38 ordinary planar atan2 angle convention remains authoritative for the
reference rear-link angle.

## 7. W38 degeneracy boundary

The D5 reference-pose integration workflow requires a non-degenerate W38
reference configuration.

If:

ReferencePoseAnalysis.geometry_degenerate = true

D5 shall reject the reference configuration as unsuitable for the D5
reference-pose round-trip workflow.

This does not redefine all mathematically possible singular four-bar states as
invalid.

It only states that a degenerate W38 reference configuration is not accepted
as the D5 engineering reference baseline.


## 8. Reference branch derivation

D5 shall derive the W39 reference branch using the W39-D4 operation:

derive_reference_branch(...)

with:

reference_b = reference_pose.rear_link_shield

reference_c = reference_pose.front_link_shield

front_link_base = fixed_geometry.front_link_base

and the explicit W39 NumericalTolerance.

D5 shall not use:

ReferencePoseAnalysis.assembly_side_signature

as the W39 reference branch.

D5 shall not translate:

SAME_SIDE -> POSITIVE

or:

OPPOSITE_SIDE -> NEGATIVE

The W39 reference branch remains defined relative to directed line:

B -> D


## 9. Unavailable non-degenerate branch label

derive_reference_branch may return:

null

D5 shall preserve that result when constructing ClosureSolverInput.

D5 shall not invent POSITIVE or NEGATIVE.

A null reference_branch does not by itself terminate the integration workflow.

The mathematical solver shall determine whether the reference geometry
corresponds to a unique TANGENT state or whether branch selection remains
ambiguous.

A successful D5 round trip still requires a unique selected pose at the end of
the integrated solve.


## 10. ClosureSolverInput mapping

D5 shall construct ClosureSolverInput using:

rear_link_base =
    linkage.fixed_geometry.rear_link_base

front_link_base =
    linkage.fixed_geometry.front_link_base

rear_link_length_mm =
    fresh DerivedGeometry.rear_link_length_mm

shield_beam_effective_length_mm =
    fresh DerivedGeometry.shield_beam_effective_length_mm

front_link_length_mm =
    fresh DerivedGeometry.front_link_length_mm

base_pivot_spacing_mm =
    fresh DerivedGeometry.base_pivot_spacing_mm

rear_link_angle_deg =
    ReferencePoseAnalysis.rear_link_angle_deg

reference_branch =
    W39-D4 derived reference branch

tolerance =
    explicit caller-supplied NumericalTolerance

The task shall be a typed ClosureSolverInput.

D5 shall not pass an unstructured dictionary into the W39 solver.


## 11. Support-height boundary

reference_pose.support_height_mm shall not be mapped into
ClosureSolverInput.

Changing only support_height_mm while keeping A/B/C/D coordinates unchanged
shall not change the D5 closure task.

Changing only support_height_mm while keeping A/B/C/D coordinates unchanged
shall not change the D5 closure result.

Support-height-driven pose solving remains outside W39.


## 12. Top-beam boundary

D5 closure-task construction shall not consume:

top_beam_interface.shield_top_beam_pivot

or:

top_beam_interface.beam_tip_reference_point

Changing only top_beam_interface shall not change the D5 closure task or
reference-pose closure result.

Top-beam motion belongs to later kinematic work.


## 13. Integrated solver execution

solve_linkage_reference_pose shall:

1. build one ClosureSolverInput from the W38 geometry
2. call the existing W39 solve_closure(task)
3. receive one typed ClosureResult
4. validate reference-pose round-trip consistency
5. return the validated ClosureResult

D5 shall not implement a second circle-intersection solver.

D5 shall not implement a second reference-branch resolver.

D3 and D4 remain authoritative for those operations.


## 14. Reference-pose round-trip invariant

A successful D5 integrated reference-pose solve requires:

result.selected_pose != null

The solved:

selected_pose.rear_link_shield

shall reproduce:

reference_pose.rear_link_shield

within the explicit numerical tolerance.

The solved:

selected_pose.front_link_shield

shall reproduce:

reference_pose.front_link_shield

within the explicit numerical tolerance.

The comparison shall use planar Euclidean point error in millimetres.

D5 shall not use rounded display coordinates for round-trip validation.


## 15. Round-trip tolerance policy

For round-trip point comparison:

point_error_mm = hypot(
    solved_x_mm - reference_x_mm,
    solved_y_mm - reference_y_mm
)

The comparison shall use the same scale-aware W39 tolerance principle:

effective_tolerance_mm = max(
    absolute_mm,
    relative * scale_mm
)

scale_mm shall be derived from relevant geometric distance magnitudes in the
current reference mechanism.

The tolerance has unit mm.

D5 shall not introduce a looser presentation tolerance merely to make a round
trip pass.


## 16. Successful closure states

For a non-degenerate explicit W38 reference pose, a successful D5 round trip
shall end with a unique selected pose.

The normal successful result may be:

TWO_SOLUTIONS + SELECTED + REFERENCE_POSE

or:

TANGENT + SELECTED + TANGENT_UNIQUE

A final result of:

NO_SOLUTION

DEGENERATE

or:

TWO_SOLUTIONS + BRANCH_AMBIGUOUS

shall fail the D5 reference-pose round-trip workflow.

D5 shall expose the inconsistency rather than inventing a selected pose.


## 17. Branch round-trip invariant

When the mathematical closure state is:

TWO_SOLUTIONS

the final selected pose branch shall equal:

ClosureSolverInput.reference_branch

The successful branch resolution shall report:

branch_resolution = REFERENCE_POSE

D5 shall not accept a geometrically close point from the opposite mathematical
branch.


## 18. Provenance preservation

Freshly derived W38 lengths retain:

origin = CALCULATED

evidence_status = PARTIAL

The W38 calculated rear-link angle retains its existing provenance.

W39 solved B/C coordinates retain:

origin = CALCULATED

evidence_status = PARTIAL

formula_ids = []

calculation_record_ids = []

D5 shall not promote any of these values to VERIFIED merely because the
round-trip software check passes.

A software round trip is not independent engineering evidence.

D5 introduces no Formula Registry ID.

D5 creates no Calculation Record.

## 19. Input immutability

D5 shall not mutate:

- LinkageGeometry
- fixed_geometry
- reference_pose
- derived_geometry
- top_beam_interface
- provenance

The complete input LinkageGeometry serialization shall remain unchanged after
task construction and integrated solving.


## 20. Validation boundary

A successful reference-pose round trip demonstrates consistency between:

W38 geometry representation

W38 deterministic geometry derivation

W38 reference-angle analysis

W39 reference-branch semantics

W39 deterministic closure solving

It does not independently prove that the reference geometry belongs to a real
hydraulic support.

ER-001 remains:

ENGINEERING_REFERENCE

NOT_SOLVER_READY

until a complete traceable real-support reference mechanism is available.

A synthetic D5 integration fixture shall not be relabelled as engineering
validation.


## 21. Explicitly outside W39-D5

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

## 22. W39 closeout direction

After D5 integration is implemented and tested, W39 may close with:

- W38 -> W39 reference-pose integration
- deterministic mathematical closure
- explicit reference branch resolution
- synthetic benchmark regression
- reference-pose round-trip regression
- explicit statement that engineering-reference validation remains pending

Continuous multi-pose motion belongs to W40.

