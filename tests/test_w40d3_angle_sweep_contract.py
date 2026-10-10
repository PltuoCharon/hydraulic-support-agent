from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w40/W40D3_angle_sweep_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_d3_target_service_and_public_operation_are_frozen():
    s = normalized()

    assert "app/services/linkage_motion.py" in s
    assert "sweep_rear_link_angles(" in s
    assert "MotionSweepInput" in s
    assert "MotionSegmentResult" in s


def test_existing_w39_solver_is_authoritative():
    s = normalized()

    assert "solve_closure(...)" in s

    assert (
        "exactly once"
        in s
    )

    assert (
        "shall not independently call: "
        "solve_closure_candidates(...)"
        in s
    )


def test_only_rear_link_angle_changes_per_sample():
    s = normalized()

    assert (
        "Only: rear_link_angle_deg shall change"
        in s
    )

    for item in (
        "rear_link_base",
        "front_link_base",
        "rear_link_length_mm",
        "shield_beam_effective_length_mm",
        "front_link_length_mm",
        "base_pivot_spacing_mm",
        "reference_branch",
        "NumericalTolerance",
    ):
        assert item in s


def test_per_angle_task_must_be_revalidated():
    s = normalized()

    assert (
        "shall pass through normal Pydantic validation"
        in s
    )

    assert "ClosureSolverInput.model_validate(...)" in s

    assert (
        "shall not use an unchecked update mechanism"
        in s
    )


def test_reference_sample_must_be_normal_selected_pose():
    s = normalized()

    assert "TWO_SOLUTIONS" in s
    assert "SELECTED" in s
    assert "REFERENCE_POSE" in s

    assert (
        "first solved sample is not a valid "
        "non-degenerate selected reference pose"
        in s
    )


def test_one_motion_sample_is_created_per_processed_angle():
    s = normalized()

    assert (
        "Each processed requested angle shall create "
        "exactly one MotionSample"
        in s
    )

    assert (
        "zero-based processed sequence position"
        in s
    )


def test_completed_requires_all_requested_angles():
    s = normalized()

    assert "termination = COMPLETED" in s

    assert (
        "len(samples) shall equal requested_angle_count"
        in s
    )


def test_tangent_is_appended_then_stops():
    s = normalized()

    assert "termination = TANGENT_BOUNDARY" in s

    assert (
        "tangent result shall be appended as the final MotionSample"
        in s
    )

    assert (
        "No later requested angle shall be solved"
        in s
    )


def test_no_solution_is_appended_then_stops():
    s = normalized()

    assert "termination = NO_SOLUTION_BOUNDARY" in s

    assert (
        "final attempted MotionSample"
        in s
    )

    assert (
        "boundary sample has no selected pose"
        in s
    )


def test_degenerate_is_appended_then_stops():
    s = normalized()

    assert "termination = DEGENERATE_BOUNDARY" in s

    assert (
        "final attempted MotionSample"
        in s
    )


def test_ambiguous_two_solution_is_explicit_error():
    s = normalized()

    assert "BRANCH_AMBIGUOUS" in s

    assert (
        "shall raise an explicit error"
        in s
    )

    assert (
        "shall not select the first candidate"
        in s
    )


def test_opposite_selected_branch_is_explicit_error():
    s = normalized()

    assert (
        "branch does not equal the frozen reference branch"
        in s
    )

    assert (
        "shall fail explicitly"
        in s
    )


def test_no_gap_and_resume_solver_calls():
    s = normalized()

    assert (
        "shall stop processing the requested angle list"
        in s
    )

    assert (
        "shall not call solve_closure(...) for later angles"
        in s
    )


def test_requested_count_records_original_request():
    s = normalized()

    assert (
        "requested_angle_count shall always equal: "
        "len(sweep.angle_samples_deg)"
        in s
    )

    assert (
        "len(samples) records processed work"
        in s
    )


def test_direction_and_reference_are_preserved():
    s = normalized()

    assert (
        "preserve: sweep.direction unchanged"
        in s
    )

    assert (
        "MotionSegmentResult.reference_branch shall equal"
        in s
    )

    assert (
        "MotionSegmentResult.reference_angle_deg shall equal"
        in s
    )


def test_motion_provenance_is_frozen():
    s = normalized()

    assert "W40_BRANCH_PRESERVING_ANGLE_SWEEP" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s


def test_service_does_not_mutate_sources():
    s = normalized()

    assert "MotionSweepInput" in s
    assert "ClosureSolverInput reference_task" in s
    assert "DegreeParameter angle objects" in s

    assert (
        "input serialization shall remain unchanged"
        in s
    )


def test_service_is_deterministic():
    s = normalized()

    assert (
        "repeated execution shall produce equal "
        "MotionSegmentResult values"
        in s
    )

    assert "random branch choice" in s


def test_service_does_not_solve_support_height():
    s = normalized()

    assert (
        "shall not calculate: support_height_mm"
        in s
    )

    assert (
        "output remains angle-parameterized motion"
        in s
    )


def test_service_does_not_propagate_top_beam():
    s = normalized()

    assert "beam_tip_trajectory" in s
    assert "beam_tip_horizontal_displacement" in s
    assert "80 mm validation" in s

    assert (
        "remain later W40 work"
        in s
    )


def test_service_does_not_interpolate_angles():
    s = normalized()

    assert (
        "solves only the explicitly requested angle samples"
        in s
    )

    assert (
        "shall not automatically insert intermediate angles"
        in s
    )


def test_service_does_not_invent_jump_threshold():
    s = normalized()

    assert (
        "shall not reject a mathematically valid adjacent pose"
        in s
    )

    assert (
        "No unsupported maximum step-distance rule is introduced"
        in s
    )


def test_d4_starts_after_bc_trajectory_exists():
    s = normalized()

    assert "B trajectory" in s
    assert "C trajectory" in s

    assert (
        "audit and freeze the missing top-beam "
        "kinematic semantics"
        in s
    )
