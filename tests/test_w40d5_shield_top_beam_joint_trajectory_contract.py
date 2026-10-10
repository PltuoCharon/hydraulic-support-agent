from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w40/"
    "W40D5_shield_top_beam_joint_trajectory_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_d5_targets_typed_model_service_and_operation():
    s = normalized()

    assert "app/models/linkage_top_beam.py" in s
    assert "app/services/linkage_top_beam.py" in s
    assert "propagate_shield_top_beam_joint(" in s


def test_d5_uses_linkage_motion_and_explicit_tolerance():
    s = normalized()

    assert "LinkageGeometry" in s
    assert "MotionSegmentResult" in s
    assert "NumericalTolerance" in s

    assert (
        "shall not introduce a hidden tolerance"
        in s
    )


def test_b0_c0_e0_are_required():
    s = normalized()

    assert (
        "linkage.reference_pose.rear_link_shield = B0"
        in s
    )

    assert (
        "linkage.reference_pose.front_link_shield = C0"
        in s
    )

    assert (
        "linkage.top_beam_interface."
        "shield_top_beam_pivot = E0"
        in s
    )


def test_missing_e_is_not_derived_from_historical_geometry():
    s = normalized()

    for item in (
        "canopy_len",
        "beam_length",
        "roof_end_distance",
        "center_dist",
        "support_height_mm",
        "beam_tip_reference_point",
    ):
        assert item in s

    assert (
        "No zero coordinate or project-wide default "
        "shall replace missing E0"
        in s
    )


def test_reference_shield_frame_formula_is_frozen():
    s = normalized()

    assert "L0 = |C0 - B0|" in s
    assert "u0 = (C0 - B0) / L0" in s
    assert "v0 = (-u0_y, u0_x)" in s

    assert "B0 -> C0" in s


def test_attachment_local_coordinates_are_frozen():
    s = normalized()

    assert "s_E = dot(E0 - B0, u0)" in s
    assert "n_E = dot(E0 - B0, v0)" in s

    assert (
        "frozen local shield-body coordinate"
        in s
    )


def test_attachment_model_is_typed():
    s = normalized()

    assert "ShieldTopBeamJointAttachment" in s
    assert "longitudinal_offset_mm = s_E" in s
    assert "normal_offset_mm = n_E" in s

    assert (
        "shall not contain beam-tip geometry"
        in s
    )


def test_motion_reference_must_match_linkage_reference():
    s = normalized()

    assert "B_motion0" in s
    assert "C_motion0" in s

    assert (
        "A reference mismatch is an explicit error"
        in s
    )


def test_tolerance_is_scale_aware_and_explicit():
    s = normalized()

    assert "scale-aware effective millimetre tolerance" in s
    assert "absolute_mm" in s
    assert "relative" in s

    assert (
        "without introducing another undocumented "
        "tolerance constant"
        in s
    )


def test_reference_e_round_trip_is_required():
    s = normalized()

    assert (
        "E_roundtrip = B0 + s_E * u0 + n_E * v0"
        in s
    )

    assert (
        "shall be within the explicit effective tolerance"
        in s
    )


def test_per_sample_frame_and_e_formula_are_frozen():
    s = normalized()

    assert "ui = (Ci - Bi) / Li" in s
    assert "vi = (-ui_y, ui_x)" in s

    assert (
        "Ei = Bi + s_E * ui + n_E * vi"
        in s
    )


def test_trajectory_sample_is_typed():
    s = normalized()

    assert "ShieldTopBeamJointTrajectorySample" in s
    assert "sample_index" in s
    assert "requested_angle_deg" in s
    assert "selected_pose_available" in s
    assert "joint_center" in s


def test_output_has_one_to_one_motion_sample_alignment():
    s = normalized()

    assert (
        "exactly one trajectory sample for every "
        "MotionSample"
        in s
    )

    assert "skip input samples" in s
    assert "insert intermediate samples" in s
    assert "reorder samples" in s


def test_normal_selected_pose_gets_e():
    s = normalized()

    assert "TWO_SOLUTIONS + SELECTED" in s

    assert (
        "calculate one propagated E coordinate"
        in s
    )

    assert (
        "joint_center shall not be null"
        in s
    )


def test_tangent_selected_pose_gets_final_e():
    s = normalized()

    assert "TANGENT + SELECTED" in s

    assert (
        "one final propagated E coordinate"
        in s
    )


def test_no_solution_keeps_alignment_without_e():
    s = normalized()

    assert "NO_SOLUTION" in s
    assert "selected_pose_available = false" in s
    assert "joint_center = null" in s


def test_degenerate_keeps_alignment_without_e():
    s = normalized()

    assert "DEGENERATE" in s

    assert (
        "shall not fabricate an E coordinate"
        in s
    )


def test_motion_termination_is_preserved():
    s = normalized()

    assert "MotionTermination" in s

    for item in (
        "COMPLETED",
        "TANGENT_BOUNDARY",
        "NO_SOLUTION_BOUNDARY",
        "DEGENERATE_BOUNDARY",
    ):
        assert item in s


def test_d5_does_not_fabricate_unprocessed_angles():
    s = normalized()

    assert "len(motion.samples)" in s
    assert "motion.requested_angle_count" in s

    assert (
        "shall not fabricate trajectory entries for "
        "angles that W40-D3 never solved"
        in s
    )


def test_trajectory_result_is_typed_without_top_beam_outputs():
    s = normalized()

    assert "ShieldTopBeamJointTrajectoryResult" in s

    assert "support_height_mm" in s
    assert "top_beam_angle_deg" in s
    assert "beam_tip_trajectory" in s

    assert (
        "It shall not require"
        in s
    )


def test_provenance_is_calculated_partial():
    s = normalized()

    assert "W40_SHIELD_TOP_BEAM_JOINT_RIGID_PROPAGATION" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert "origin = CALCULATED" in s


def test_rigid_attachment_local_coordinates_do_not_drift():
    s = normalized()

    assert (
        "reproduce: s_E and: n_E"
        in s
    )

    assert (
        "No arbitrary coordinate-jump threshold is introduced"
        in s
    )


def test_inputs_and_legacy_slots_are_not_mutated():
    s = normalized()

    assert "LinkageGeometry.trajectory_results" in s

    assert (
        "shall not mutate"
        in s
    )

    assert (
        "D5 typed result is the authoritative propagation result"
        in s
    )


def test_d5_does_not_infer_beam_tip_or_support_height():
    s = normalized()

    assert "beam_tip_horizontal_displacement_mm" in s
    assert "80 mm compliance" in s
    assert "support_height_mm" in s

    assert (
        "Known E motion does not remove the independent "
        "top-beam orientation degree of freedom"
        in s
    )


def test_d6_preserves_completed_bce_capability_and_open_gap():
    s = normalized()

    assert (
        "deterministic B/C trajectory"
        in s
    )

    assert (
        "deterministic E trajectory"
        in s
    )

    assert "beam-tip trajectory = NOT EXECUTABLE" in s
    assert "80 mm validation = NOT EXECUTABLE" in s

    assert (
        "explicit evidence gap"
        in s
    )
