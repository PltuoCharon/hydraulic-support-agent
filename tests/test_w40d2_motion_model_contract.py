from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w40/W40D2_motion_model_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_d2_target_and_model_types_are_frozen():
    s = normalized()

    assert "app/models/linkage_motion.py" in s

    for item in (
        "MotionDirection",
        "MotionTermination",
        "MotionSweepInput",
        "MotionSample",
        "MotionSweepProvenance",
        "MotionSegmentResult",
    ):
        assert item in s


def test_one_segment_represents_one_direction():
    s = normalized()

    assert "INCREASING" in s
    assert "DECREASING" in s

    assert (
        "construct two explicit motion segments"
        in s
    )


def test_direction_has_no_auto_mode():
    s = normalized()

    assert "No AUTO direction is allowed" in s
    assert "No UNKNOWN direction is allowed" in s


def test_termination_values_are_frozen():
    s = normalized()

    for item in (
        "COMPLETED",
        "TANGENT_BOUNDARY",
        "NO_SOLUTION_BOUNDARY",
        "DEGENERATE_BOUNDARY",
    ):
        assert item in s

    assert (
        "BRANCH_AMBIGUOUS is not a normal termination value"
        in s
    )


def test_sweep_input_reuses_reference_task():
    s = normalized()

    assert "reference_task: ClosureSolverInput" in s
    assert "angle_samples_deg: list[DegreeParameter]" in s

    assert (
        "NumericalTolerance remains inside reference_task"
        in s
    )


def test_reference_branch_must_be_non_null():
    s = normalized()

    assert (
        "reference_task.reference_branch shall be non-null"
        in s
    )

    assert "POSITIVE" in s
    assert "NEGATIVE" in s


def test_reference_angle_is_first_explicit_sample():
    s = normalized()

    assert (
        "angle_samples_deg[0].value = "
        "reference_task.rear_link_angle_deg.value"
        in s
    )

    assert (
        "starts at its engineering reference pose"
        in s
    )


def test_sweep_requires_at_least_two_samples():
    s = normalized()

    assert (
        "at least two angle samples"
        in s
    )

    assert (
        "One isolated reference angle is a W39 single-pose problem"
        in s
    )


def test_input_angles_are_finite_and_monotonic():
    s = normalized()

    assert "NaN is invalid" in s
    assert "Positive infinity is invalid" in s
    assert "Negative infinity is invalid" in s

    assert "angle[i + 1] > angle[i]" in s
    assert "angle[i + 1] < angle[i]" in s


def test_mechanism_geometry_is_not_duplicated_at_sweep_top_level():
    s = normalized()

    assert (
        "shall not duplicate those authoritative mechanism fields "
        "at the MotionSweepInput top level"
        in s
    )

    assert (
        "changing only: rear_link_angle_deg"
        in s
    )


def test_motion_sample_embeds_complete_w39_result():
    s = normalized()

    assert "closure_result: ClosureResult" in s

    assert (
        "complete W39 ClosureResult remains authoritative"
        in s
    )

    assert (
        "shall not duplicate authoritative B/C coordinates"
        in s
    )


def test_normal_sample_is_selected_reference_branch():
    s = normalized()

    assert "closure_state = TWO_SOLUTIONS" in s
    assert "selection_status = SELECTED" in s

    assert (
        "selected_pose.branch = frozen segment reference branch"
        in s
    )

    assert "branch_resolution = REFERENCE_POSE" in s


def test_tangent_is_typed_terminal_boundary():
    s = normalized()

    assert "selected_pose.branch = TANGENT" in s
    assert "branch_resolution = TANGENT_UNIQUE" in s

    assert (
        "termination shall be: TANGENT_BOUNDARY"
        in s
    )


def test_no_solution_and_degenerate_are_typed_boundaries():
    s = normalized()

    assert (
        "termination shall be: NO_SOLUTION_BOUNDARY"
        in s
    )

    assert (
        "termination shall be: DEGENERATE_BOUNDARY"
        in s
    )

    assert "It is not a trajectory pose" in s


def test_ambiguous_two_solution_is_invalid():
    s = normalized()

    assert (
        "TWO_SOLUTIONS with: selection_status = BRANCH_AMBIGUOUS"
        in s
    )

    assert (
        "shall fail explicitly"
        in s
    )


def test_branch_continuity_is_model_invariant():
    s = normalized()

    assert (
        "selected_pose.branch shall equal: "
        "MotionSegmentResult.reference_branch"
        in s
    )

    assert (
        "A POSITIVE segment cannot contain a selected NEGATIVE sample"
        in s
    )


def test_sample_indexes_are_contiguous():
    s = normalized()

    assert "0, 1, 2, ..., n - 1" in s
    assert "Missing indexes are invalid" in s
    assert "Duplicate indexes are invalid" in s


def test_result_preserves_angle_order():
    s = normalized()

    assert (
        "preserve the processed input order"
        in s
    )

    assert (
        "shall not reorder samples by coordinate values or closure state"
        in s
    )


def test_motion_provenance_is_partial_without_formula_ids():
    s = normalized()

    assert "W40_BRANCH_PRESERVING_ANGLE_SWEEP" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s


def test_result_records_requested_and_processed_semantics():
    s = normalized()

    assert "requested_angle_count" in s

    assert (
        "len(samples) <= requested_angle_count"
        in s
    )

    assert (
        "len(samples) = requested_angle_count"
        in s
    )


def test_completed_result_contains_only_normal_selected_samples():
    s = normalized()

    assert (
        "A COMPLETED result shall not contain"
        in s
    )

    assert "TANGENT" in s
    assert "NO_SOLUTION" in s
    assert "DEGENERATE" in s


def test_boundary_sample_must_be_last():
    s = normalized()

    assert (
        "No MotionSegmentResult may contain samples after"
        in s
    )

    assert (
        "gap-and-resume invalid at the data-model layer"
        in s
    )


def test_w39_mathematical_candidates_are_preserved():
    s = normalized()

    assert (
        "mathematical candidates remain available for auditing"
        in s
    )

    assert (
        "shall not discard the unselected mathematical candidate"
        in s
    )


def test_motion_models_do_not_require_support_height():
    s = normalized()

    assert (
        "No W40-D2 model shall require: support_height_mm"
        in s
    )

    assert (
        "W38 PoseResult type is therefore not used"
        in s
    )


def test_d3_service_boundary_is_frozen():
    s = normalized()

    assert "sweep_rear_link_angles(...)" in s

    assert (
        "stop at the first tangent, no-solution, or degenerate boundary"
        in s
    )

    assert "never gap and resume" in s

    assert (
        "shall not introduce support-height solving"
        in s
    )
