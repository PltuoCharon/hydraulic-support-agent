from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D2_closure_model_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_d2_is_model_layer_not_solver():
    s = normalized()

    assert "app/models/linkage_closure.py" in s
    assert "does not implement" in s
    assert "circle intersection" in s

    assert (
        "Numerical closure implementation belongs to a later W39 step"
        in s
    )


def test_d2_reuses_w38_types():
    s = text()

    for item in (
        "EngineeringPoint2D",
        "NormalizedOriginPoint",
        "MillimetreParameter",
        "DegreeParameter",
        "StrictModel",
    ):
        assert item in s

    assert "do not replace hs.linkageGeometry.v1" in s


def test_closure_multiplicity_enum_is_frozen():
    s = text()

    for item in (
        "NO_SOLUTION",
        "TANGENT",
        "TWO_SOLUTIONS",
        "DEGENERATE",
    ):
        assert item in s


def test_selection_and_branch_enums_are_frozen():
    s = text()

    for item in (
        "POSITIVE",
        "NEGATIVE",
        "SELECTED",
        "BRANCH_AMBIGUOUS",
        "NOT_APPLICABLE",
    ):
        assert item in s

    assert "ReferenceBranch intentionally excludes TANGENT" in s


def test_numerical_tolerance_is_explicit_and_non_engineering():
    s = normalized()

    assert "absolute_mm" in s
    assert "relative" in s
    assert "must be finite" in s
    assert "must be strictly positive" in s

    assert (
        "They are numerical-computation infrastructure"
        in s
    )

    assert (
        "shall require an explicit NumericalTolerance object"
        in s
    )


def test_solver_input_contains_canonical_geometry():
    s = text()

    for item in (
        "rear_link_base",
        "front_link_base",
        "rear_link_length_mm",
        "shield_beam_effective_length_mm",
        "front_link_length_mm",
        "base_pivot_spacing_mm",
        "rear_link_angle_deg",
        "reference_branch",
        "tolerance",
    ):
        assert item in s


def test_base_spacing_redundancy_is_for_validation_not_repair():
    s = normalized()

    assert (
        "This redundancy exists so a later solver can validate consistency"
        in s
    )

    assert "shall not move D" in s
    assert "shall not rewrite base_pivot_spacing_mm" in s


def test_candidate_is_not_automatically_selected():
    s = normalized()

    assert "ClosureCandidate" in s

    assert (
        "It is not automatically the selected engineering pose"
        in s
    )


def test_solver_provenance_preserves_current_boundary():
    s = text()

    assert "evidence_status" in s
    assert "PARTIAL" in s
    assert "formula_ids shall currently remain empty" in s
    assert "calculation_record_ids shall currently remain empty" in s

    for item in (
        "REFERENCE_POSE",
        "TANGENT_UNIQUE",
        "NONE",
    ):
        assert item in s


def test_no_solution_and_degenerate_have_no_candidates():
    s = normalized()

    assert "closure_state = NO_SOLUTION" in s
    assert "closure_state = DEGENERATE" in s
    assert "candidates = []" in s
    assert "selection_status = NOT_APPLICABLE" in s
    assert "selected_pose = null" in s


def test_tangent_invariant_is_frozen():
    s = normalized()

    assert "closure_state = TANGENT" in s
    assert "exactly one ClosureCandidate shall exist" in s
    assert "selection_status shall be: SELECTED" in s
    assert "branch_resolution shall be: TANGENT_UNIQUE" in s


def test_two_solution_invariant_is_frozen():
    s = normalized()

    assert "closure_state = TWO_SOLUTIONS" in s
    assert "exactly two ClosureCandidate objects shall exist" in s

    assert (
        "Their branch set shall be exactly: POSITIVE NEGATIVE"
        in s
    )

    assert "BRANCH_AMBIGUOUS" in s


def test_selected_and_ambiguous_are_distinct():
    s = normalized()

    assert (
        "selection_status = SELECTED"
        in s
    )

    assert (
        "selection_status = BRANCH_AMBIGUOUS"
        in s
    )

    assert (
        "shall not convert BRANCH_AMBIGUOUS into an arbitrary selected pose"
        in s
    )


def test_invalid_result_combinations_must_be_rejected():
    s = text()

    assert "NO_SOLUTION with a candidate" in s
    assert "TANGENT with two candidates" in s
    assert "TWO_SOLUTIONS with two POSITIVE candidates" in s
    assert "SELECTED without selected_pose" in s


def test_d2_preserves_provenance_and_no_historical_fill():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s

    for item in (
        "canopy_len",
        "center_dist",
        "historical beam_length",
        "historical example dimensions",
    ):
        assert item in s


def test_d3_must_use_typed_result_model():
    s = normalized()

    assert "W39-D3" in s

    assert (
        "shall use the D2 models rather than returning an unstructured dict"
        in s
    )


def test_selected_pose_identity_is_frozen():
    s = normalized()

    assert (
        "selected_pose.rear_link_shield"
        in s
    )

    assert (
        "shall equal the sole candidate point_c"
        in s
    )

    assert (
        "Matching the branch label alone is insufficient"
        in s
    )

    assert (
        "exact data-consistency invariants"
        in s
    )
