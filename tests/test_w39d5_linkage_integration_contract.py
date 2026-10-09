from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D5_linkage_integration_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_d5_target_service_and_round_trip_are_frozen():
    s = normalized()

    assert (
        "app/services/linkage_closure_integration.py"
        in s
    )

    assert (
        "explicit W38 reference pose -> derive mechanism geometry "
        "-> derive rear-link angle -> derive W39 reference branch "
        "-> build ClosureSolverInput -> solve closure "
        "-> recover the same reference B/C pose"
        in s
    )


def test_d5_public_operations_are_frozen():
    s = text()

    assert "build_closure_task_from_linkage" in s
    assert "validate_reference_pose_round_trip" in s
    assert "solve_linkage_reference_pose" in s

    assert (
        "NumericalTolerance is required explicitly"
        in s
    )


def test_missing_w38_geometry_is_not_filled():
    s = normalized()

    assert "front_link_base is missing" in s
    assert "reference_pose is missing" in s

    assert "canopy_len" in s
    assert "center_dist" in s

    assert (
        "shall not fill missing geometry"
        in s
    )


def test_d5_requires_fresh_geometry_derivation():
    s = normalized()

    assert "derive_geometry(linkage)" in s
    assert "fresh DerivedGeometry" in s

    assert (
        "shall not use: linkage.derived_geometry "
        "as the authoritative solver geometry"
        in s
    )

    assert (
        "shall not silently overwrite linkage.derived_geometry"
        in s
    )


def test_all_four_fresh_lengths_are_required():
    s = text()

    for item in (
        "base_pivot_spacing_mm",
        "rear_link_length_mm",
        "shield_beam_effective_length_mm",
        "front_link_length_mm",
    ):
        assert item in s

    assert "DA" in s
    assert "AB" in s
    assert "BC" in s
    assert "CD" in s


def test_d5_reuses_w38_rear_link_angle():
    s = normalized()

    assert "analyze_reference_pose(linkage)" in s

    assert (
        "ReferencePoseAnalysis.rear_link_angle_deg"
        in s
    )

    assert (
        "shall not independently create a second A-to-B angle convention"
        in s
    )


def test_degenerate_w38_reference_is_not_baseline():
    s = normalized()

    assert (
        "ReferencePoseAnalysis.geometry_degenerate = true"
        in s
    )

    assert (
        "not accepted as the D5 engineering reference baseline"
        in s
    )


def test_reference_branch_comes_from_b_c_d_not_signature():
    s = normalized()

    assert "derive_reference_branch(...)" in s

    assert (
        "reference_b = reference_pose.rear_link_shield"
        in s
    )

    assert (
        "reference_c = reference_pose.front_link_shield"
        in s
    )

    assert (
        "shall not use: ReferencePoseAnalysis.assembly_side_signature"
        in s
    )

    assert "B -> D" in s


def test_null_reference_branch_is_not_guessed():
    s = normalized()

    assert "derive_reference_branch may return: null" in s

    assert (
        "shall not invent POSITIVE or NEGATIVE"
        in s
    )

    assert (
        "does not by itself terminate the integration workflow"
        in s
    )


def test_closure_solver_input_mapping_is_explicit():
    s = normalized()

    assert (
        "rear_link_length_mm = fresh "
        "DerivedGeometry.rear_link_length_mm"
        in s
    )

    assert (
        "rear_link_angle_deg = "
        "ReferencePoseAnalysis.rear_link_angle_deg"
        in s
    )

    assert (
        "reference_branch = W39-D4 derived reference branch"
        in s
    )

    assert (
        "typed ClosureSolverInput"
        in s
    )


def test_support_height_is_not_solver_driver():
    s = normalized()

    assert (
        "reference_pose.support_height_mm shall not be mapped "
        "into ClosureSolverInput"
        in s
    )

    assert (
        "Changing only support_height_mm"
        in s
    )

    assert (
        "Support-height-driven pose solving remains outside W39"
        in s
    )


def test_top_beam_is_not_consumed():
    s = normalized()

    assert "top_beam_interface.shield_top_beam_pivot" in s
    assert "top_beam_interface.beam_tip_reference_point" in s

    assert (
        "shall not change the D5 closure task"
        in s
    )


def test_d5_reuses_existing_d3_d4_solver():
    s = normalized()

    assert "call the existing W39 solve_closure(task)" in s

    assert (
        "shall not implement a second circle-intersection solver"
        in s
    )

    assert (
        "shall not implement a second reference-branch resolver"
        in s
    )


def test_reference_pose_round_trip_requires_selected_pose():
    s = normalized()

    assert "result.selected_pose != null" in s

    assert (
        "selected_pose.rear_link_shield"
        in s
    )

    assert (
        "selected_pose.front_link_shield"
        in s
    )

    assert (
        "within the explicit numerical tolerance"
        in s
    )


def test_round_trip_uses_euclidean_mm_error():
    s = normalized()

    assert (
        "point_error_mm = hypot( "
        "solved_x_mm - reference_x_mm, "
        "solved_y_mm - reference_y_mm )"
        in s
    )

    assert (
        "effective_tolerance_mm = max( "
        "absolute_mm, relative * scale_mm )"
        in s
    )


def test_unsuccessful_reference_states_fail_integration():
    s = normalized()

    assert "NO_SOLUTION" in s
    assert "DEGENERATE" in s

    assert (
        "TWO_SOLUTIONS + BRANCH_AMBIGUOUS"
        in s
    )

    assert (
        "shall fail the D5 reference-pose round-trip workflow"
        in s
    )


def test_two_solution_branch_must_round_trip():
    s = normalized()

    assert (
        "final selected pose branch shall equal: "
        "ClosureSolverInput.reference_branch"
        in s
    )

    assert (
        "branch_resolution = REFERENCE_POSE"
        in s
    )

    assert (
        "shall not accept a geometrically close point "
        "from the opposite mathematical branch"
        in s
    )


def test_round_trip_does_not_promote_evidence():
    s = normalized()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s

    assert (
        "shall not promote any of these values to VERIFIED"
        in s
    )

    assert (
        "A software round trip is not independent engineering evidence"
        in s
    )


def test_d5_does_not_mutate_linkage():
    s = normalized()

    assert "D5 shall not mutate:" in s
    assert "LinkageGeometry" in s
    assert "derived_geometry" in s
    assert "reference_pose" in s

    assert (
        "complete input LinkageGeometry serialization "
        "shall remain unchanged"
        in s
    )


def test_engineering_reference_remains_pending():
    s = normalized()

    assert "ER-001 remains:" in s
    assert "ENGINEERING_REFERENCE NOT_SOLVER_READY" in s

    assert (
        "synthetic D5 integration fixture shall not be "
        "relabelled as engineering validation"
        in s
    )


def test_w40_owns_continuous_motion():
    s = normalized()

    assert "previous-pose continuity" in s
    assert "branch continuity across multiple poses" in s
    assert "operating-height sweep" in s

    assert (
        "Continuous multi-pose motion belongs to W40"
        in s
    )
