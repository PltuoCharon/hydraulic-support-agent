from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w40/W40D4_top_beam_kinematic_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_d4_freezes_b_c_e_t_semantics():
    s = normalized()

    assert "B = rear_link_shield" in s
    assert "C = front_link_shield" in s
    assert "E = shield_top_beam_pivot" in s
    assert "T = beam_tip_reference_point" in s


def test_top_beam_remains_outside_four_bar():
    s = normalized()

    assert (
        "top-beam / shield-beam connection is outside "
        "that canonical four-bar"
        in s
    )


def test_e_is_conditional_explicit_joint_center():
    s = normalized()

    assert (
        "explicit reference: shield_top_beam_pivot = E0"
        in s
    )

    assert (
        "material point fixed in the rigid shield beam"
        in s
    )

    assert (
        "shall not be presented as independently VERIFIED geometry"
        in s
    )


def test_missing_e_is_not_fabricated():
    s = normalized()

    assert (
        "propagate E only when: shield_top_beam_pivot "
        "is explicitly available"
        in s
    )

    assert (
        "No zero/default coordinate shall replace missing E0"
        in s
    )


def test_reference_shield_frame_is_directed_b_to_c():
    s = normalized()

    assert "u0 = (C0 - B0) / L0" in s
    assert "v0 = (-u0_y, u0_x)" in s

    assert (
        "directed B0 -> C0"
        in s
    )


def test_e_local_coordinates_are_frozen():
    s = normalized()

    assert "s_E = dot(E0 - B0, u0)" in s
    assert "n_E = dot(E0 - B0, v0)" in s

    assert (
        "(s_E, n_E)"
        in s
    )


def test_e_propagation_formula_is_frozen():
    s = normalized()

    assert "ui = (Ci - Bi) / Li" in s
    assert "vi = (-ui_y, ui_x)" in s

    assert (
        "Ei = Bi + s_E * ui + n_E * vi"
        in s
    )


def test_frame_orientation_is_not_coordinate_heuristic():
    s = normalized()

    assert "directed: B -> C" in s
    assert "larger X" in s
    assert "larger Y" in s
    assert "candidate ordering" in s


def test_reference_e_round_trip_is_required():
    s = normalized()

    assert (
        "shall reproduce the explicit: E0"
        in s
    )

    assert (
        "within the explicit numerical tolerance"
        in s
    )


def test_motion_reference_must_match_attachment_reference():
    s = normalized()

    assert (
        "motion reference B/C agrees with the "
        "LinkageGeometry reference B/C"
        in s
    )

    assert (
        "apply it silently to another mechanism"
        in s
    )


def test_rigid_local_coordinates_do_not_drift():
    s = normalized()

    assert (
        "local coordinates of E relative to the "
        "directed shield frame shall remain"
        in s
    )

    assert (
        "No independent drift of E relative to "
        "the shield beam is allowed"
        in s
    )


def test_e_can_be_propagated_at_tangent():
    s = normalized()

    assert "TANGENT + SELECTED" in s

    assert (
        "may therefore receive a propagated E point"
        in s
    )


def test_unsolved_boundaries_have_no_e():
    s = normalized()

    assert "NO_SOLUTION" in s
    assert "DEGENERATE" in s

    assert (
        "shall not fabricate E for unsolved boundary samples"
        in s
    )


def test_e_propagation_does_not_solve_t():
    s = normalized()

    assert (
        "does not uniquely determine: Ti = beam_tip position"
        in s
    )

    assert (
        "shall not propagate T using the shield-beam rotation alone"
        in s
    )


def test_top_beam_orientation_is_independently_constrained():
    s = normalized()

    assert (
        "top beam to support different pitch attitudes"
        in s
    )

    assert (
        "balance jack as participating"
        in s
    )

    assert (
        "independently constrained kinematic quantity"
        in s
    )


def test_balance_jack_geometry_gap_is_explicit():
    s = normalized()

    assert "balance-jack shield-side pivot" in s
    assert "balance-jack top-beam-side pivot" in s
    assert "effective jack length for a pose" in s
    assert "stroke limits" in s

    assert (
        "Merely knowing that a balance jack exists is insufficient"
        in s
    )


def test_future_top_beam_constraints_are_explicit():
    s = normalized()

    assert "top-beam angle for each mechanism pose" in s
    assert "balance-jack installation geometry plus jack length" in s
    assert "a second independent top-beam geometry point" in s

    assert (
        "shall not invent one of these constraints"
        in s
    )


def test_reference_t_alone_is_insufficient():
    s = normalized()

    assert "beam_tip_reference_point = T0" in s

    assert (
        "T0 alone is insufficient for a deterministic "
        "beam-tip trajectory"
        in s
    )


def test_historical_geometry_cannot_fill_top_beam_gap():
    s = normalized()

    assert "canopy_len" in s
    assert "beam_length" in s
    assert "roof_end_distance" in s

    assert (
        "Missing top-beam geometry remains missing"
        in s
    )


def test_80mm_validation_remains_blocked():
    s = normalized()

    assert "80 mm" in s

    assert (
        "does not execute that validation"
        in s
    )

    assert (
        "a deterministic beam-tip trajectory"
        in s
    )

    assert (
        "complete operating-height range"
        in s
    )


def test_propagated_e_remains_calculated_partial():
    s = normalized()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert (
        "does not promote the original geometry to VERIFIED"
        in s
    )


def test_d5_is_limited_to_deterministic_e_trajectory():
    s = normalized()

    assert (
        "D5 may implement typed shield/top-beam joint propagation"
        in s
    )

    assert (
        "shall not yet claim a deterministic beam-tip trajectory"
        in s
    )


def test_d6_can_close_with_not_executable_validation():
    s = normalized()

    assert "beam-tip trajectory = NOT EXECUTABLE" in s
    assert "80 mm validation = NOT EXECUTABLE" in s

    assert (
        "Missing evidence shall not be replaced with fabricated geometry"
        in s
    )
