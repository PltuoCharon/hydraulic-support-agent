# W39-D1 Deterministic Four-Bar Closure Contract

## 1. Objective

W39-D1 freezes the mathematical semantics for deterministic four-bar closure
and pose solving.

W39 builds directly on the W38 canonical linkage geometry.

W39-D1 defines semantics only.

It does not yet implement the numerical closure solver.

It does not introduce optimization.

## 2. Canonical topology

Canonical joint notation is:

A = rear_link_base

B = rear_link_shield

C = front_link_shield

D = front_link_base

Canonical rigid-link lengths are:

AB = rear_link_length_mm

BC = shield_beam_effective_length_mm

CD = front_link_length_mm

DA = base_pivot_spacing_mm

The canonical closed chain is:

A -> B -> C -> D -> A

Top-beam geometry is not part of this four-bar closure.

## 3. First independent motion variable

The first deterministic W39 solver shall use:

rear_link_angle_deg

as the independent motion variable.

The angle follows the existing W38 coordinate convention:

- measured from +X
- positive according to ordinary planar atan2 orientation
- unit = degree

support_height_mm is not the independent solver variable in W39.

W39-D1 does not infer a mechanism pose directly from support height.

## 4. Deterministic point B

Given:

A = rear_link_base

AB = rear_link_length_mm

theta = rear_link_angle_deg

point B is determined by:

Bx = Ax + AB * cos(theta)

By = Ay + AB * sin(theta)

The trigonometric implementation shall convert the degree input explicitly.

No internal presentation rounding is permitted.

The resulting B coordinate is deterministic calculated geometry.

This elementary geometry relation does not introduce a new Formula Registry
ID in W39.

## 5. Point C closure problem

After B is determined, point C must satisfy both rigid-link constraints:

distance(B, C) = BC

distance(D, C) = CD

Therefore C is obtained from the intersection of two circles:

circle 1:

center = B
radius = BC

circle 2:

center = D
radius = CD

Let:

q = distance(B, D)

r1 = BC

r2 = CD

The solver shall evaluate the mathematical relationship between q, r1 and r2
before constructing candidate coordinates.

## 6. Closure multiplicity

The closure calculation shall expose one of four mathematical states:

NO_SOLUTION

TANGENT

TWO_SOLUTIONS

DEGENERATE

### NO_SOLUTION

NO_SOLUTION includes:

q > r1 + r2

and:

q < abs(r1 - r2)

after applying the frozen numerical tolerance policy.

If the circle centers coincide but the radii are different, the result is also
NO_SOLUTION.

### TANGENT

TANGENT means there is exactly one geometric C point within numerical
tolerance.

Both external tangency and internal tangency are included.

### TWO_SOLUTIONS

TWO_SOLUTIONS means there are two distinct finite C candidates.

### DEGENERATE

DEGENERATE includes mathematical configurations where a finite discrete
candidate set cannot be defined.

In particular, if the circle centers coincide within tolerance and the radii
are also equal within tolerance, infinitely many intersections exist.

That case is DEGENERATE.

It is not TWO_SOLUTIONS.

No arbitrary C coordinate may be invented for a degenerate case.

## 7. Deterministic circle-intersection construction

For a non-degenerate circle-intersection problem:

q = distance(B, D)

a = (r1^2 - r2^2 + q^2) / (2*q)

h^2 = r1^2 - a^2

The base point P lies on the directed line B -> D.

The candidate C coordinates are obtained by applying positive and negative
perpendicular offsets from P.

When h is zero within numerical tolerance, the result is TANGENT.

When h is strictly positive beyond tolerance, two candidate points exist.

Small negative h^2 caused only by floating-point tolerance may be clamped to
zero according to the centralized numerical policy.

A physically impossible negative h^2 shall not be silently clamped into a
valid pose.

## 8. Numerical tolerance policy

W39 shall use a centralized numerical tolerance policy.

The tolerance is computational infrastructure.

It is not a hydraulic-support engineering design parameter.

The solver shall support both:

- absolute distance tolerance
- relative tolerance scaled to current geometry magnitude

The effective tolerance shall be scale-aware.

W39-D1 does not freeze arbitrary engineering dimensions as numerical
tolerances.

The exact strongly typed tolerance representation belongs to W39-D2.

## 9. Candidate branch sign

When TWO_SOLUTIONS exists, W39 shall classify each C candidate relative to the
directed line:

B -> D

For candidate C, use the signed 2D cross product between:

D - B

and

C - B

Candidate branch classes are:

POSITIVE

NEGATIVE

TANGENT

For two distinct non-degenerate intersections, the two candidates are expected
to occupy opposite sides of the directed B-D line.

W39-D1 does not rename these candidate branch classes OPEN or CROSSED.

OPEN / CROSSED terminology remains deferred until mechanism-specific
kinematic semantics are explicitly frozen.

## 10. W38 assembly signature is not W39 branch sign

W38 ReferencePoseAnalysis defines:

SAME_SIDE
OPPOSITE_SIDE
DEGENERATE

using moving-pivot positions relative to the fixed base line:

A -> D

W39 candidate branch sign uses candidate C relative to:

B -> D

These are different geometric classifiers.

W38 assembly_side_signature shall not be used as a substitute for the W39
candidate branch sign.

The two concepts shall remain separately named and separately implemented.

## 11. Reference branch selection

When the explicit W38 reference pose is complete, it may establish the
reference closure branch.

The reference points are:

reference B = reference_pose.rear_link_shield

reference C = reference_pose.front_link_shield

fixed D = front_link_base

The reference branch sign is calculated from reference C relative to the
directed line:

reference B -> D

For TWO_SOLUTIONS, the solver shall select the candidate whose W39 branch sign
matches the non-degenerate reference branch sign.

The solver must not select a candidate merely because:

- it is returned first by a circle-intersection algorithm
- it has the smaller X coordinate
- it has the larger X coordinate
- it has the smaller Y coordinate
- it has the larger Y coordinate
- it appears visually more plausible

If TWO_SOLUTIONS exists but the reference pose cannot determine an unambiguous
branch, selection shall be reported as ambiguous.

The solver shall not guess.

For TANGENT, only one finite candidate exists and branch selection is unique.

## 12. Selection status

Closure multiplicity and candidate selection are separate concepts.

A later solver result shall distinguish closure state from selection state.

Expected selection semantics include:

SELECTED

BRANCH_AMBIGUOUS

NOT_APPLICABLE

NO_SOLUTION and DEGENERATE do not produce a selected pose.

TANGENT may produce a unique selected pose.

TWO_SOLUTIONS requires explicit branch resolution before one candidate becomes
the selected engineering pose.

## 13. Continuity boundary

Reference-branch matching is the first W39 branch-selection mechanism.

For a later operating-range sweep, the previously solved pose may also be used
to enforce configuration continuity.

That continuous motion policy belongs to W40.

W39-D1 does not yet define full trajectory continuity.

A future sweep shall not silently jump between mathematical branches.

## 14. Required input validity

Closure solving requires finite canonical geometry.

Required rigid-link lengths shall be strictly positive beyond numerical
tolerance:

- AB
- BC
- CD
- DA

Zero or near-zero canonical link lengths are invalid solver inputs.

NaN is invalid.

Positive infinity is invalid.

Negative infinity is invalid.

Fixed pivot coordinates must be finite.

Missing required geometry shall produce an explicit failure.

Missing geometry shall not be replaced with:

- zero
- canopy_len
- center_dist
- historical beam_length
- historical roof_end_distance
- historical example dimensions

## 15. Provenance of solved geometry

Coordinates produced by the deterministic W39 solver shall use:

origin = CALCULATED

evidence_status = PARTIAL

This means the coordinates are mathematically derived from the supplied
geometry.

It does not independently verify that the supplied geometry is physically
correct for a real hydraulic support.

W39-D1 introduces no Formula Registry ID.

W39-D1 introduces no Calculation Record.

Input geometry provenance shall remain unchanged.

AI_PROPOSED geometry shall not be promoted automatically to VERIFIED.

## 16. Support-height boundary

W39 closure solving is driven by rear_link_angle_deg.

reference_pose.support_height_mm remains reference-pose metadata.

The mathematical mapping between:

four-bar mechanism pose

and

hydraulic-support support_height_mm

has not yet been frozen.

Therefore W39 shall not claim that an arbitrary solved four-bar pose
corresponds to a particular hydraulic-support height.

That mapping must be established explicitly before W40 height-range kinematics
uses it.

## 17. Top-beam and 80 mm boundary

W39 solves only the canonical four-bar mechanism.

W39-D1 does not calculate:

- top-beam pose
- beam-tip position
- beam-tip trajectory
- beam-tip horizontal displacement

The MT/T 556-1996 80 mm requirement remains a stored validation boundary.

It is not yet executable at W39-D1.

## 18. Optimization boundary

W39-D1 contains no:

- GA
- PSO
- NSGA-II
- objective-function search
- parameter optimization

Mature optimization belongs after deterministic kinematics are independently
testable.

## 19. Benchmark classes

W39 shall distinguish mathematical software benchmarks from engineering
reference cases.

SYNTHETIC_MATH benchmark:

- may use deliberately simple artificial geometry
- validates mathematics and software behavior
- does not constitute hydraulic-support engineering validation

ENGINEERING_REFERENCE benchmark:

- must come from traceable hydraulic-support geometry or a traceable technical
  source
- must preserve provenance
- may be used for engineering comparison only to the extent supported by its
  source

Synthetic 3-4-5 or other convenient geometries shall never be presented as
verified hydraulic-support design data.

## 20. W39-D2 entry condition

W39-D2 may introduce strongly typed models for:

- solver input
- numerical tolerance
- closure multiplicity
- closure candidates
- branch sign
- selection status
- selected pose
- solver provenance

W39-D2 remains data-model work.

It shall not yet implement the numerical closure solver.
