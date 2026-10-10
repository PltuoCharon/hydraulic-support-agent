# W40-D6 Continuous Four-Bar Kinematics Closeout

## 1. Stage objective

W40 establishes deterministic sampled continuous motion for the hydraulic
support four-bar mechanism while preserving the engineering branch semantics
frozen in W39.

W40 also audits the boundary between four-bar motion, shield/top-beam joint
motion, top-beam orientation, beam-tip trajectory, and operating-height
validation.

W40 is now closed at the engineering boundary supported by current geometry.

## 2. Final implemented chain

The completed executable chain is:

rear_link_angle_deg samples

-> deterministic W39 four-bar closure

-> branch-preserving selected B/C poses

-> ordered B/C trajectory

-> shield rigid-body pose

-> deterministic shield/top-beam joint-center E trajectory

The chain is deterministic for explicit valid reference geometry.

## 3. Motion parameter

The W40 independent motion parameter is:

rear_link_angle_deg

The trajectory is therefore an:

angle-parameterized sampled kinematic trajectory.

It shall not be described as an operating-height trajectory.

W40 does not prove continuous-time motion.

## 4. Motion continuity semantics

One W40 motion segment:

- starts at the explicit engineering reference pose
- follows strictly monotonic requested rear-link angles
- preserves one explicit POSITIVE or NEGATIVE reference branch
- reuses the deterministic W39 closure solver
- stops at the first terminal geometric boundary
- never skips a failed angle and resumes later

Continuity means ordered sampled branch-preserving kinematics.

It does not mean a mathematical continuous-time proof.

## 5. Normal interior motion

Normal interior samples require:

TWO_SOLUTIONS

with:

selection_status = SELECTED

and:

selected_pose.branch = frozen reference branch

and:

branch_resolution = REFERENCE_POSE

The unselected mathematical candidate remains preserved inside the W39 result.

## 6. Tangent boundary

A terminal:

TANGENT

pose is accepted as one final unique selected pose.

Its termination is:

TANGENT_BOUNDARY

The trajectory stops there.

W40 does not automatically cross the tangent into the opposite assembly branch.

## 7. No-solution boundary

A terminal:

NO_SOLUTION

sample is retained as the final attempted motion sample.

Its termination is:

NO_SOLUTION_BOUNDARY

It has no selected pose.

The trajectory does not skip that angle and continue.

## 8. Degenerate boundary

A terminal:

DEGENERATE

sample is retained as the final attempted motion sample.

Its termination is:

DEGENERATE_BOUNDARY

It has no selected pose.

The trajectory stops immediately.

## 9. Branch ambiguity boundary

A:

TWO_SOLUTIONS + BRANCH_AMBIGUOUS

state is not a valid W40 motion termination.

It is an explicit service error.

W40 never chooses:

- the first candidate
- the closest candidate
- the candidate with larger X
- the candidate with larger Y
- a visually preferred candidate

to continue motion.

## 10. B/C trajectory capability

For every selected W40 motion sample, the system provides:

B = rear_link_shield

C = front_link_shield

as provenance-aware deterministic calculated points.

The ordered selected B/C poses form the completed four-bar trajectory output.

## 11. Shield rigid-body semantics

The directed segment:

B -> C

defines the planar shield-beam rigid-body reference axis.

Its direction is frozen and deterministic.

W40 does not reverse that frame from coordinate magnitude or visual
orientation.

## 12. Explicit E attachment

When explicit:

shield_top_beam_pivot = E0

is available in the reference geometry, W40 derives the local shield-frame
coordinates:

s_E

n_E

using the directed reference:

B0 -> C0

No missing E geometry is inferred from historical/default dimensions.

## 13. E trajectory capability

For every selected B/C pose:

Bi

Ci

W40 propagates:

Ei = Bi + s_E * ui + n_E * vi

where:

ui

is the unit vector along:

Bi -> Ci

and:

vi

is its positive 90-degree planar normal.

This produces a deterministic E trajectory.

## 14. E boundary samples

For:

TWO_SOLUTIONS + SELECTED

E is available.

For terminal:

TANGENT + SELECTED

one final E point is available.

For:

NO_SOLUTION

E is null.

For:

DEGENERATE

E is null.

The E trajectory remains one-to-one aligned with the processed W40 motion
samples.

## 15. W40 completed capability

At W40 closeout, the executable deterministic capability is:

rear-link-angle samples

-> B/C trajectory

-> shield rigid-body pose

-> E trajectory

This capability is complete for the geometry represented by the current
contracts.

## 16. Support-height mapping status

W40 does not establish a deterministic mapping:

rear_link_angle_deg
-> support_height_mm

No support height is inferred from:

B.y

C.y

E.y

shield angle

beam-tip Y

or another single coordinate.

Therefore the W40 trajectory is not yet a complete operating-height-range
trajectory.

## 17. Existing operating-height boundaries

Stored:

operating_height_min_mm

and:

operating_height_max_mm

remain design boundaries.

They are not automatically rear-link-angle limits.

W40 does not fabricate an angle interval from those values.

## 18. 100 mm calculation interval boundary

The project evidence records a 100 mm interval for calculations across the
support operating-height range.

W40 does not reinterpret that requirement as:

rear_link_angle_deg sweep spacing.

A height-domain calculation interval cannot be converted into an angle-domain
sampling interval without a deterministic height-to-angle mapping.

## 19. Top-beam orientation status

Knowing:

B

C

and:

E

does not uniquely determine top-beam orientation.

The top beam retains an independently constrained kinematic degree of freedom.

Current project geometry does not provide a deterministic complete top-beam
orientation relation.

## 20. Balance-jack geometry gap

The project recognizes the engineering role of the balance jack, but current
model-specific geometry is insufficient to solve top-beam orientation.

The missing information includes, as applicable:

shield-side balance-jack pivot

top-beam-side balance-jack pivot

effective jack length

stroke limits

installation offsets

or another explicit top-beam pose law.

W40 does not fabricate these dimensions.

## 21. Beam-tip reference point status

An explicit:

beam_tip_reference_point = T0

is only a reference-pose coordinate.

T0 alone does not define the top-beam rotational law.

Therefore W40 does not rigidly rotate T0 with the shield beam and call the
result a physical beam-tip trajectory.

## 22. Beam-tip trajectory status

At W40 closeout:

beam-tip trajectory = NOT EXECUTABLE

The reason is missing deterministic top-beam orientation geometry.

This is an engineering evidence boundary, not a software failure.

## 23. MT/T 556 80 mm boundary

The project retains the engineering validation boundary:

beam-tip horizontal displacement <= 80 mm

over the support operating-height range.

The boundary remains available for future validation.

W40 does not claim compliance.

## 24. 80 mm validation status

At W40 closeout:

80 mm validation = NOT EXECUTABLE

because executable validation requires both:

1. deterministic beam-tip trajectory
2. deterministic coverage of the complete operating-height range

Neither prerequisite is completed by the current B/C/E trajectory alone.

## 25. Historical geometry prohibition

W40 does not convert historical or generic values such as:

canopy_len

beam_length

roof_end_distance

center_dist

into missing:

top-beam length

E attachment

beam-tip offset

balance-jack installation geometry

top-beam angle law

or operating-height mapping.

Missing engineering geometry remains missing.

## 26. Legacy result containers

Legacy:

PoseResult

and:

TrajectoryResults

remain reserved containers.

W40 does not populate PoseResult by inventing support_height_mm.

W40-D5 also does not mutate:

TrajectoryResults.shield_top_beam_joint_trajectory

as an implicit side effect.

The dedicated W40 typed results remain authoritative.

## 27. Numerical policy

W40 reuses explicit NumericalTolerance semantics.

Scale-aware distance tolerance follows the established W39 policy:

max(
    tolerance.absolute_mm,
    tolerance.relative * scale_mm
)

No undocumented geometric tolerance or inter-sample jump threshold is
introduced.

## 28. Provenance

Deterministic W40 calculation outputs remain:

origin = CALCULATED

evidence_status = PARTIAL

with:

formula_ids = []

calculation_record_ids = []

W40 introduces no unsupported Formula Registry ID.

W40 creates no fabricated Calculation Record.

Deterministic software calculation does not promote missing engineering
geometry to VERIFIED.

## 29. Input immutability and determinism

W40 services preserve their source inputs.

Repeated execution with identical validated inputs produces equal deterministic
outputs.

No random state is used.

No visual or proximity heuristic is used for branch selection.

## 30. Automated validation boundary

W40 automated tests validate:

strongly typed state invariants

branch-preserving sampled motion

boundary termination behavior

reference-pose consistency

deterministic B/C motion

rigid E attachment

deterministic E propagation

provenance constraints

input immutability

and deterministic repeated execution.

Passing software tests does not prove physical mechanism correctness for a
specific hydraulic-support product.

## 31. W40 final scientific wording

The W40 result shall be described as:

a deterministic sampled branch-preserving four-bar kinematic trajectory with
rigid propagation of the explicit shield/top-beam joint center.

It shall not be described as:

a validated full-support operating-height trajectory

a solved top-beam trajectory

a solved beam-tip trajectory

or proof of MT/T 556 80 mm compliance.

## 32. W40 final status

Completed:

angle-driven branch-preserving four-bar motion

B/C trajectory

shield rigid-body pose

explicit E attachment derivation

E trajectory

Not executable with current geometry:

support-height mapping

top-beam orientation trajectory

beam-tip T trajectory

80 mm beam-tip displacement validation

The unresolved items are explicit engineering-geometry gaps.

## 33. W41 handoff

W41 may now begin the mature-algorithm optimization baseline for the
four-bar mechanism.

The optimization baseline shall operate only on objectives and constraints
that are deterministically executable.

W41 shall not optimize:

beam-tip displacement

80 mm compliance

or operating-height trajectory objectives

until their prerequisite geometry and mappings become executable.

W41 shall preserve the W39/W40 mechanism semantics rather than bypassing them.

## 34. Final principle

W40 closes with a working deterministic kinematic foundation and an explicit
engineering evidence boundary.

A missing engineering relation is not repaired by assumption merely to produce
a numerical result.

Missing geometry shall not be fabricated.
