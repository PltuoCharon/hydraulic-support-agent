from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D1_four_bar_closure_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_w39_uses_canonical_abcd_topology():
    s = text()

    assert "A = rear_link_base" in s
    assert "B = rear_link_shield" in s
    assert "C = front_link_shield" in s
    assert "D = front_link_base" in s

    assert "A -> B -> C -> D -> A" in s


def test_w39_freezes_four_rigid_link_lengths():
    s = text()

    for item in (
        "rear_link_length_mm",
        "shield_beam_effective_length_mm",
        "front_link_length_mm",
        "base_pivot_spacing_mm",
    ):
        assert item in s


def test_rear_link_angle_is_first_independent_variable():
    s = normalized()

    assert "rear_link_angle_deg" in s

    assert (
        "as the independent motion variable"
        in s
    )

    assert (
        "support_height_mm is not the independent solver variable"
        in s
    )


def test_point_b_relation_is_explicit():
    s = text()

    assert "Bx = Ax + AB * cos(theta)" in s
    assert "By = Ay + AB * sin(theta)" in s


def test_point_c_is_two_circle_intersection():
    s = normalized()

    assert "distance(B, C) = BC" in s
    assert "distance(D, C) = CD" in s

    assert "center = B radius = BC" in s
    assert "center = D radius = CD" in s


def test_closure_multiplicity_is_frozen():
    s = text()

    for item in (
        "NO_SOLUTION",
        "TANGENT",
        "TWO_SOLUTIONS",
        "DEGENERATE",
    ):
        assert item in s


def test_coincident_equal_circles_are_degenerate():
    s = normalized()

    assert "infinitely many intersections exist" in s
    assert "That case is DEGENERATE" in s
    assert "It is not TWO_SOLUTIONS" in s


def test_circle_intersection_construction_is_explicit():
    s = text()

    assert "a = (r1^2 - r2^2 + q^2) / (2*q)" in s
    assert "h^2 = r1^2 - a^2" in s

    assert (
        "physically impossible negative h^2 shall not be silently clamped"
        in normalized()
    )


def test_numerical_tolerance_is_infrastructure():
    s = normalized()

    assert "centralized numerical tolerance policy" in s
    assert "absolute distance tolerance" in s
    assert "relative tolerance" in s

    assert (
        "not a hydraulic-support engineering design parameter"
        in s
    )


def test_candidate_branch_uses_bd_line():
    s = normalized()

    assert "directed line: B -> D" in s
    assert "signed 2D cross product" in s

    for item in (
        "POSITIVE",
        "NEGATIVE",
        "TANGENT",
    ):
        assert item in s


def test_w38_signature_and_w39_branch_are_not_conflated():
    s = normalized()

    assert "A -> D" in s
    assert "B -> D" in s

    assert (
        "These are different geometric classifiers"
        in s
    )

    assert (
        "assembly_side_signature shall not be used as a substitute"
        in s
    )


def test_reference_pose_controls_two_solution_selection():
    s = normalized()

    assert "reference_pose.rear_link_shield" in s
    assert "reference_pose.front_link_shield" in s

    assert (
        "branch sign matches the non-degenerate reference branch sign"
        in s
    )


def test_solver_never_selects_first_candidate_arbitrarily():
    s = normalized()

    assert (
        "it is returned first by a circle-intersection algorithm"
        in s
    )

    assert "The solver shall not guess" in s


def test_selection_status_is_separate_from_closure_state():
    s = text()

    for item in (
        "SELECTED",
        "BRANCH_AMBIGUOUS",
        "NOT_APPLICABLE",
    ):
        assert item in s

    assert (
        "Closure multiplicity and candidate selection are separate concepts"
        in s
    )


def test_invalid_geometry_is_not_fabricated():
    s = text()

    assert "Zero or near-zero canonical link lengths" in s
    assert "NaN is invalid" in s
    assert "Positive infinity is invalid" in s
    assert "Negative infinity is invalid" in s

    for item in (
        "canopy_len",
        "center_dist",
        "historical beam_length",
        "historical example dimensions",
    ):
        assert item in s


def test_solved_geometry_preserves_provenance_boundary():
    s = normalized()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s

    assert "introduces no Formula Registry ID" in s
    assert "introduces no Calculation Record" in s

    assert (
        "AI_PROPOSED geometry shall not be promoted automatically to VERIFIED"
        in s
    )


def test_support_height_mapping_remains_unfrozen():
    s = normalized()

    assert (
        "W39 closure solving is driven by rear_link_angle_deg"
        in s
    )

    assert (
        "mapping between: four-bar mechanism pose and "
        "hydraulic-support support_height_mm has not yet been frozen"
        in s
    )


def test_top_beam_and_optimization_remain_outside_w39d1():
    s = text()

    assert "beam-tip trajectory" in s
    assert "80 mm" in s

    assert "GA" in s
    assert "PSO" in s
    assert "NSGA-II" in s


def test_benchmark_classes_separate_math_from_engineering():
    s = normalized()

    assert "SYNTHETIC_MATH" in s
    assert "ENGINEERING_REFERENCE" in s

    assert (
        "does not constitute hydraulic-support engineering validation"
        in s
    )

    assert (
        "shall never be presented as verified hydraulic-support design data"
        in s
    )


def test_w39d2_remains_model_only():
    s = normalized()

    assert (
        "W39-D2 may introduce strongly typed models"
        in s
    )

    assert (
        "It shall not yet implement the numerical closure solver"
        in s
    )
