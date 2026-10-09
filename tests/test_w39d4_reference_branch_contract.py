from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D4_reference_branch_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_d4_separates_math_from_engineering_selection():
    s = normalized()

    assert (
        "W39-D3 answers: What mathematical closure solutions exist?"
        in s
    )

    assert (
        "W39-D4 answers: When TWO_SOLUTIONS exists"
        in s
    )


def test_reference_branch_uses_explicit_b_c_d_geometry():
    s = text()

    assert "reference B = reference_pose.rear_link_shield" in s
    assert "reference C = reference_pose.front_link_shield" in s
    assert "fixed D = front_link_base" in s
    assert "reference B -> D" in s


def test_reference_branch_uses_signed_distance_mm():
    s = normalized()

    assert (
        "reference_signed_distance_mm"
        in s
    )

    assert (
        "cross / distance(reference B, D)"
        in s
    )

    assert (
        "raw cross product has unit mm^2"
        in s
    )


def test_w38_assembly_signature_is_not_w39_branch():
    s = normalized()

    assert "W38 assembly_side_signature" in s
    assert "A -> D side classification" in s

    assert (
        "SAME_SIDE -> POSITIVE"
        in s
    )

    assert (
        "OPPOSITE_SIDE -> NEGATIVE"
        in s
    )

    assert "No such mapping is frozen" in s


def test_degenerate_reference_does_not_guess_branch():
    s = normalized()

    assert "reference_branch = null" in s

    assert (
        "The system shall not guess POSITIVE or NEGATIVE"
        in s
    )

    assert "BRANCH_AMBIGUOUS" in s


def test_d4_reuses_numerical_tolerance_policy():
    s = normalized()

    assert (
        "effective_tolerance_mm = max( "
        "absolute_mm, relative * scale_mm )"
        in s
    )

    assert (
        "shall not introduce a second incompatible tolerance policy"
        in s
    )


def test_reference_derivation_and_resolution_are_separate():
    s = text()

    assert "derive_reference_branch" in s
    assert "resolve_reference_branch" in s

    assert (
        "It shall not solve the four-bar mechanism"
        in s
    )


def test_non_two_solution_results_are_preserved():
    s = normalized()

    assert "NO_SOLUTION" in s
    assert "DEGENERATE" in s
    assert "TANGENT" in s

    assert (
        "TANGENT_UNIQUE"
        in s
    )

    assert (
        "shall not relabel tangent uniqueness "
        "as REFERENCE_POSE selection"
        in s
    )


def test_two_solution_without_reference_stays_ambiguous():
    s = normalized()

    assert "task.reference_branch = null" in s
    assert "selection_status = BRANCH_AMBIGUOUS" in s
    assert "selected_pose = null" in s
    assert "branch_resolution = NONE" in s


def test_branch_selection_is_by_semantics_not_index():
    s = normalized()

    assert (
        "Candidate lookup shall be by branch semantics"
        in s
    )

    assert (
        "Candidate list position shall not be used for selection"
        in s
    )


def test_selected_pose_reuses_d3_coordinates():
    s = normalized()

    assert (
        "rear_link_shield = result.rear_link_shield"
        in s
    )

    assert (
        "front_link_shield = selected candidate point_c"
        in s
    )

    assert (
        "No B or C coordinate shall be recomputed in D4"
        in s
    )


def test_successful_resolution_preserves_both_candidates():
    s = normalized()

    assert "branch_resolution becomes: REFERENCE_POSE" in s

    assert (
        "The original two candidates remain present"
        in s
    )

    assert (
        "Engineering selection shall not destroy "
        "the original mathematical solution set"
        in s
    )


def test_d4_rejects_already_selected_two_solution():
    s = normalized()

    assert (
        "If a TWO_SOLUTIONS result is already: SELECTED"
        in s
    )

    assert (
        "reject it as an invalid layer input"
        in s
    )

    assert "double resolution" in s


def test_candidate_integrity_never_falls_back():
    s = normalized()

    assert (
        "If the requested reference branch cannot be found"
        in s
    )

    assert "shall fail explicitly" in s
    assert "substitute the other candidate" in s
    assert "manufacture a new candidate" in s


def test_integrated_solver_calls_d3_then_d4():
    s = normalized()

    assert "solve_closure(" in s

    assert (
        "call the W39-D3 mathematical closure solver exactly once"
        in s
    )

    assert (
        "shall not contain a second circle-intersection implementation"
        in s
    )


def test_d4_does_not_promote_geometry_to_verified():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "branch_resolution = REFERENCE_POSE" in s

    assert (
        "does not promote geometric evidence_status to VERIFIED"
        in s
    )


def test_d5_is_integration_not_math_rewrite():
    s = normalized()

    assert "W39-D5 may integrate" in s
    assert "W38 LinkageGeometry" in s
    assert "W38 explicit ReferencePose" in s

    assert (
        "shall not change D3 circle-intersection mathematics "
        "merely to make an engineering example pass"
        in s
    )
