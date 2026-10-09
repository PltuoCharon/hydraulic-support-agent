from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D3_numerical_closure_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_d3_target_service_and_public_boundary_are_frozen():
    s = text()

    assert "app/services/linkage_closure.py" in s
    assert "calculate_rear_link_shield" in s
    assert "solve_closure_candidates" in s
    assert "ClosureSolverInput" in s
    assert "ClosureResult" in s


def test_d3_preserves_canonical_abcd_topology():
    s = text()

    assert "A = rear_link_base" in s
    assert "B = rear_link_shield" in s
    assert "C = front_link_shield" in s
    assert "D = front_link_base" in s
    assert "A -> B -> C -> D -> A" in s


def test_point_b_equations_are_frozen():
    s = text()

    assert "Bx = Ax + AB * cos(theta)" in s
    assert "By = Ay + AB * sin(theta)" in s
    assert "degree to radian" in s


def test_distance_tolerance_is_dimensionally_coherent():
    s = normalized()

    assert (
        "effective_tolerance_mm = max( "
        "absolute_mm, relative * scale_mm )"
        in s
    )

    assert "unit mm" in s

    assert (
        "shall not compare a raw squared-distance quantity directly "
        "against a tolerance expressed in mm"
        in s
    )


def test_base_spacing_mismatch_is_input_failure():
    s = normalized()

    assert "geometric_AD = distance(A, D)" in s

    assert (
        "This is an input-consistency failure"
        in s
    )

    assert "It is not: NO_SOLUTION" in s

    assert "shall not: - move D" in s
    assert "rewrite base_pivot_spacing_mm" in s


def test_coincident_circle_semantics_are_frozen():
    s = normalized()

    assert (
        "q <= effective_tolerance_mm"
        in s
    )

    assert (
        "abs(r1 - r2) <= effective_tolerance_mm"
        in s
    )

    assert "DEGENERATE" in s
    assert "infinitely many mathematical C points" in s


def test_separated_and_contained_states_are_no_solution():
    s = normalized()

    assert "outer_gap = q - (r1 + r2)" in s
    assert "inner_gap = abs(r1 - r2) - q" in s

    assert (
        "outer_gap > effective_tolerance_mm"
        in s
    )

    assert (
        "inner_gap > effective_tolerance_mm"
        in s
    )


def test_external_and_internal_tangency_are_supported():
    s = normalized()

    assert (
        "abs(q - (r1 + r2)) <= effective_tolerance_mm"
        in s
    )

    assert (
        "abs(q - abs(r1 - r2)) <= effective_tolerance_mm"
        in s
    )

    assert "external and internal tangency" in s.lower()


def test_circle_intersection_construction_is_frozen():
    s = normalized()

    assert (
        "a = ( r1^2 - r2^2 + q^2 ) / (2*q)"
        in s
    )

    assert "h^2 = r1^2 - a^2" in s
    assert "C_positive" in s
    assert "C_negative" in s


def test_branch_sign_uses_signed_distance_not_raw_cross_tolerance():
    s = normalized()

    assert "signed_distance_mm = cross / distance(B, D)" in s

    assert (
        "shall use distance-scale tolerance rather than comparing "
        "the raw mm^2 cross product directly against an mm tolerance"
        in s
    )


def test_two_solution_candidate_order_is_deterministic_not_preference():
    s = normalized()

    assert "1. POSITIVE 2. NEGATIVE" in s

    assert (
        "It does not mean that POSITIVE is preferred"
        in s
    )

    assert (
        "D4 branch resolution shall use branch semantics, "
        "not list position"
        in s
    )


def test_d3_never_selects_two_solution_reference_branch():
    s = normalized()

    assert "selection_status = BRANCH_AMBIGUOUS" in s
    assert "selected_pose = null" in s
    assert "branch_resolution = NONE" in s

    assert (
        "D3 shall not consume reference_branch to select a candidate"
        in s
    )


def test_tangent_can_be_mathematically_selected():
    s = normalized()

    assert "branch_resolution = TANGENT_UNIQUE" in s

    assert (
        "This is mathematical uniqueness"
        in s
    )

    assert (
        "It is not reference-branch engineering selection"
        in s
    )


def test_d3_preserves_calculated_partial_provenance():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert "introduces no new Formula Registry ID" in s
    assert "creates no Calculation Record" in s


def test_d3_requires_all_six_synthetic_benchmarks():
    s = text()

    for item in (
        "SM-001 = TWO_SOLUTIONS",
        "SM-002 = TANGENT",
        "SM-003 = NO_SOLUTION",
        "SM-004 = NO_SOLUTION",
        "SM-005 = DEGENERATE",
        "SM-006 = NO_SOLUTION",
    ):
        assert item in s


def test_d3_does_not_overclaim_engineering_validation():
    s = normalized()

    assert "ER-001 remains:" in s
    assert "ENGINEERING_REFERENCE NOT_SOLVER_READY" in s

    assert (
        "does not constitute hydraulic-support engineering validation"
        in s
    )


def test_d4_owns_reference_branch_resolution():
    s = normalized()

    assert (
        "W39-D4 may implement reference-branch resolution"
        in s
    )

    assert (
        "D4 shall not recalculate circle intersection "
        "merely to choose a branch"
        in s
    )

    assert (
        "D4 shall not select by candidate list position"
        in s
    )
