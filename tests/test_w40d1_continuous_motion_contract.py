from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w40/W40D1_continuous_motion_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_w40_keeps_rear_link_angle_as_first_motion_parameter():
    s = normalized()

    assert "rear_link_angle_deg" in s

    assert (
        "does not redefine support_height_mm as the four-bar "
        "driving variable"
        in s
    )


def test_continuous_sweep_requires_non_degenerate_reference_branch():
    s = normalized()

    assert "POSITIVE" in s
    assert "NEGATIVE" in s

    assert (
        "A null reference branch is not sufficient"
        in s
    )

    assert (
        "shall not by itself define the W40 continuous branch seed"
        in s
    )


def test_angle_sequence_is_ordered_and_strictly_monotonic():
    s = normalized()

    assert "strictly monotonic" in s
    assert "strictly increasing" in s
    assert "strictly decreasing" in s

    assert (
        "Duplicate consecutive angles are invalid"
        in s
    )


def test_reference_angle_must_anchor_sweep():
    s = normalized()

    assert (
        "reference rear-link angle shall be explicitly represented"
        in s
    )

    assert (
        "shall not infer an unknown reference angle "
        "from support_height_mm"
        in s
    )


def test_rigid_geometry_is_constant_during_sweep():
    s = normalized()

    for item in (
        "rear_link_base A",
        "front_link_base D",
        "AB rear-link length",
        "BC shield-beam effective linkage length",
        "CD front-link length",
        "DA base-pivot spacing",
        "NumericalTolerance",
        "reference branch",
    ):
        assert item in s

    assert (
        "Only rear_link_angle_deg changes"
        in s
    )


def test_w40_reuses_existing_w39_solver():
    s = normalized()

    assert "solve_closure(...)" in s

    assert (
        "shall not implement a second circle-intersection solver"
        in s
    )

    assert (
        "shall not implement a second branch-resolution algorithm"
        in s
    )


def test_normal_sample_preserves_reference_branch():
    s = normalized()

    assert "closure_state = TWO_SOLUTIONS" in s
    assert "selection_status = SELECTED" in s
    assert "branch_resolution = REFERENCE_POSE" in s

    assert (
        "selected_pose.branch = reference branch"
        in s
    )


def test_branch_continuity_never_uses_candidate_position():
    s = normalized()

    assert (
        "A POSITIVE sweep shall not silently select NEGATIVE"
        in s
    )

    assert (
        "A NEGATIVE sweep shall not silently select POSITIVE"
        in s
    )

    assert "candidate list index" in s
    assert "visual appearance" in s


def test_tangent_is_terminal_not_branch_switch_permission():
    s = normalized()

    assert "selected_pose.branch = TANGENT" in s
    assert "branch_resolution = TANGENT_UNIQUE" in s

    assert (
        "TANGENT does not authorize automatic switching"
        in s
    )

    assert (
        "stop that sweep direction"
        in s
    )


def test_unreachable_sample_terminates_continuous_segment():
    s = normalized()

    assert "NO_SOLUTION" in s

    assert (
        "shall not skip the failed sample and resume"
        in s
    )

    assert (
        "terminates in that sweep direction"
        in s
    )


def test_degenerate_sample_does_not_fabricate_pose():
    s = normalized()

    assert "DEGENERATE" in s

    assert (
        "shall not manufacture a finite C point"
        in s
    )


def test_unexpected_two_solution_ambiguity_fails():
    s = normalized()

    assert (
        "TWO_SOLUTIONS + BRANCH_AMBIGUOUS"
        in s
    )

    assert (
        "shall fail explicitly"
        in s
    )


def test_motion_segment_cannot_gap_and_resume():
    s = normalized()

    assert (
        "one contiguous run of valid selected poses"
        in s
    )

    assert (
        "shall not resume later"
        in s
    )


def test_no_arbitrary_coordinate_jump_threshold_is_added():
    s = normalized()

    assert (
        "does not introduce an arbitrary maximum allowed "
        "B or C displacement per sample"
        in s
    )

    assert (
        "No unverified engineering jump threshold shall be invented"
        in s
    )


def test_provenance_remains_calculated_partial():
    s = normalized()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert (
        "does not promote geometry to VERIFIED"
        in s
    )


def test_existing_pose_result_is_not_abused():
    s = normalized()

    assert (
        "current W38 PoseResult model requires: support_height_mm"
        in s
    )

    assert (
        "shall not populate PoseResult by inventing support_height_mm"
        in s
    )


def test_existing_trajectory_result_is_not_abused():
    s = normalized()

    assert "beam_tip_trajectory" in s
    assert "beam_tip_horizontal_displacement_mm" in s

    assert (
        "shall not populate those future slots merely because "
        "the container exists"
        in s
    )


def test_top_beam_propagation_is_not_yet_defined():
    s = normalized()

    assert "shield_top_beam_pivot" in s
    assert "beam_tip_reference_point" in s

    assert "top-beam local coordinate frame" in s
    assert "attachment transform" in s

    assert (
        "does not propagate top-beam or beam-tip coordinates"
        in s
    )


def test_80mm_is_preserved_but_not_yet_executable():
    s = normalized()

    assert "shall not exceed 80 mm" in s

    assert (
        "80 mm value is a validation boundary"
        in s
    )

    assert (
        "shall not claim 80 mm compliance from an arbitrary "
        "rear-link-angle sweep"
        in s
    )


def test_support_height_is_not_inferred_from_joint_coordinates():
    s = normalized()

    assert "does not calculate: support_height_mm" in s

    for item in (
        "B.y",
        "C.y",
        "shield_top_beam_pivot.y",
        "beam_tip_reference_point.y",
    ):
        assert item in s


def test_operating_height_limits_are_not_converted_to_angle_limits():
    s = normalized()

    assert "operating_height_min_mm" in s
    assert "operating_height_max_mm" in s

    assert (
        "shall not be converted into rear-link-angle limits"
        in s
    )


def test_w40d2_requires_new_typed_motion_model():
    s = normalized()

    assert (
        "W40-D2 may introduce a strongly typed motion model"
        in s
    )

    assert (
        "shall not require support_height_mm until "
        "support-height semantics exist"
        in s
    )


def test_later_80mm_validation_remains_conditional():
    s = normalized()

    assert "W40-D4:" in s
    assert "W40-D5:" in s
    assert "W40-D6:" in s

    assert (
        "preserve that item as an explicit evidence/geometry gap"
        in s
    )
