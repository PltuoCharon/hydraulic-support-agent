import math

import pytest
from pydantic import ValidationError

from app.models.linkage_geometry import (
    DegreeParameter,
    EngineeringPoint2D,
    MillimetreParameter,
)
from app.models.linkage_top_beam import (
    ShieldTopBeamJointAttachment,
    ShieldTopBeamJointPropagationProvenance,
    ShieldTopBeamJointTrajectoryResult,
    ShieldTopBeamJointTrajectorySample,
)


def input_mm(value):
    return MillimetreParameter(
        value=value,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
    )


def calculated_mm(
    value,
    *,
    formula_ids=None,
    calculation_record_ids=None,
):
    return MillimetreParameter(
        value=value,
        origin="CALCULATED",
        evidence_status="PARTIAL",
        formula_ids=(
            []
            if formula_ids is None
            else formula_ids
        ),
        calculation_record_ids=(
            []
            if calculation_record_ids is None
            else calculation_record_ids
        ),
    )


def deg(value):
    return DegreeParameter(
        value=value,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
    )


def input_point(x, y):
    return EngineeringPoint2D(
        x_mm=input_mm(x),
        y_mm=input_mm(y),
    )


def calculated_point(
    x,
    y,
    *,
    formula_ids=None,
):
    return EngineeringPoint2D(
        x_mm=calculated_mm(
            x,
            formula_ids=formula_ids,
        ),
        y_mm=calculated_mm(
            y,
            formula_ids=formula_ids,
        ),
    )


def attachment():
    return ShieldTopBeamJointAttachment(
        reference_rear_link_shield=(
            input_point(1, 2)
        ),
        reference_front_link_shield=(
            input_point(5, 2)
        ),
        reference_joint_center=(
            input_point(6, 3)
        ),
        longitudinal_offset_mm=(
            calculated_mm(5)
        ),
        normal_offset_mm=(
            calculated_mm(1)
        ),
    )


def trajectory_sample(
    index,
    angle,
    *,
    state="TWO_SOLUTIONS",
):
    selected = state in {
        "TWO_SOLUTIONS",
        "TANGENT",
    }

    return ShieldTopBeamJointTrajectorySample(
        sample_index=index,
        requested_angle_deg=deg(angle),
        closure_state=state,
        selected_pose_available=selected,
        joint_center=(
            calculated_point(
                10 + index,
                20 + index,
            )
            if selected
            else None
        ),
    )


def trajectory_result(
    samples,
    *,
    direction="INCREASING",
    branch="POSITIVE",
    reference_angle=0,
    requested_angle_count=None,
    termination="COMPLETED",
):
    if requested_angle_count is None:
        requested_angle_count = len(samples)

    return ShieldTopBeamJointTrajectoryResult(
        attachment=attachment(),
        direction=direction,
        reference_branch=branch,
        reference_angle_deg=deg(
            reference_angle
        ),
        requested_angle_count=(
            requested_angle_count
        ),
        samples=samples,
        termination=termination,
    )


def test_valid_attachment():
    item = attachment()

    assert item.version == 1

    assert (
        item.longitudinal_offset_mm.value
        == 5
    )

    assert (
        item.normal_offset_mm.value
        == 1
    )


def test_attachment_preserves_reference_input_provenance():
    item = attachment()

    assert (
        item.reference_joint_center
        .x_mm.origin
        == "USER_INPUT"
    )

    assert (
        item.reference_joint_center
        .x_mm.evidence_status
        == "EVIDENCE_GAP"
    )


def test_attachment_rejects_exact_zero_length_bc_axis():
    with pytest.raises(
        ValidationError,
        match="zero length",
    ):
        ShieldTopBeamJointAttachment(
            reference_rear_link_shield=(
                input_point(1, 2)
            ),
            reference_front_link_shield=(
                input_point(1, 2)
            ),
            reference_joint_center=(
                input_point(2, 3)
            ),
            longitudinal_offset_mm=(
                calculated_mm(1)
            ),
            normal_offset_mm=(
                calculated_mm(1)
            ),
        )


def test_attachment_rejects_non_calculated_longitudinal_offset():
    with pytest.raises(
        ValidationError,
        match="origin CALCULATED",
    ):
        ShieldTopBeamJointAttachment(
            reference_rear_link_shield=(
                input_point(1, 2)
            ),
            reference_front_link_shield=(
                input_point(5, 2)
            ),
            reference_joint_center=(
                input_point(6, 3)
            ),
            longitudinal_offset_mm=(
                input_mm(5)
            ),
            normal_offset_mm=(
                calculated_mm(1)
            ),
        )


def test_attachment_rejects_fake_formula_trace_on_offset():
    with pytest.raises(
        ValidationError,
        match="must not claim Formula IDs",
    ):
        ShieldTopBeamJointAttachment(
            reference_rear_link_shield=(
                input_point(1, 2)
            ),
            reference_front_link_shield=(
                input_point(5, 2)
            ),
            reference_joint_center=(
                input_point(6, 3)
            ),
            longitudinal_offset_mm=(
                calculated_mm(
                    5,
                    formula_ids=["F-FAKE"],
                )
            ),
            normal_offset_mm=(
                calculated_mm(1)
            ),
        )


def test_provenance_defaults_are_frozen():
    p = (
        ShieldTopBeamJointPropagationProvenance()
    )

    assert (
        p.engine
        == "W40_SHIELD_TOP_BEAM_JOINT_RIGID_PROPAGATION"
    )

    assert p.evidence_status == "PARTIAL"
    assert p.formula_ids == []
    assert p.calculation_record_ids == []


def test_provenance_rejects_formula_ids():
    with pytest.raises(
        ValidationError,
        match="Formula Registry IDs",
    ):
        ShieldTopBeamJointPropagationProvenance(
            formula_ids=["F-FAKE"]
        )


def test_provenance_rejects_calculation_record_ids():
    with pytest.raises(
        ValidationError,
        match="Calculation Record IDs",
    ):
        ShieldTopBeamJointPropagationProvenance(
            calculation_record_ids=[999]
        )


def test_valid_two_solution_sample():
    sample = trajectory_sample(
        0,
        0,
    )

    assert (
        sample.closure_state
        == "TWO_SOLUTIONS"
    )

    assert sample.selected_pose_available

    assert sample.joint_center is not None


def test_valid_tangent_sample():
    sample = trajectory_sample(
        1,
        10,
        state="TANGENT",
    )

    assert sample.selected_pose_available
    assert sample.joint_center is not None


def test_valid_no_solution_sample():
    sample = trajectory_sample(
        1,
        10,
        state="NO_SOLUTION",
    )

    assert not sample.selected_pose_available
    assert sample.joint_center is None


def test_valid_degenerate_sample():
    sample = trajectory_sample(
        1,
        10,
        state="DEGENERATE",
    )

    assert not sample.selected_pose_available
    assert sample.joint_center is None


def test_selected_sample_requires_joint_center():
    with pytest.raises(
        ValidationError,
        match="requires joint_center",
    ):
        ShieldTopBeamJointTrajectorySample(
            sample_index=0,
            requested_angle_deg=deg(0),
            closure_state="TWO_SOLUTIONS",
            selected_pose_available=True,
            joint_center=None,
        )


def test_unsolved_sample_forbids_joint_center():
    with pytest.raises(
        ValidationError,
        match="must not contain joint_center",
    ):
        ShieldTopBeamJointTrajectorySample(
            sample_index=1,
            requested_angle_deg=deg(10),
            closure_state="NO_SOLUTION",
            selected_pose_available=False,
            joint_center=(
                calculated_point(1, 2)
            ),
        )


def test_two_solution_cannot_be_unavailable():
    with pytest.raises(
        ValidationError,
        match="requires NO_SOLUTION or DEGENERATE",
    ):
        ShieldTopBeamJointTrajectorySample(
            sample_index=0,
            requested_angle_deg=deg(0),
            closure_state="TWO_SOLUTIONS",
            selected_pose_available=False,
            joint_center=None,
        )


def test_no_solution_cannot_be_selected():
    with pytest.raises(
        ValidationError,
        match="requires TWO_SOLUTIONS or TANGENT",
    ):
        ShieldTopBeamJointTrajectorySample(
            sample_index=1,
            requested_angle_deg=deg(10),
            closure_state="NO_SOLUTION",
            selected_pose_available=True,
            joint_center=(
                calculated_point(1, 2)
            ),
        )


def test_joint_center_must_be_calculated_partial():
    with pytest.raises(
        ValidationError,
        match="origin CALCULATED",
    ):
        ShieldTopBeamJointTrajectorySample(
            sample_index=0,
            requested_angle_deg=deg(0),
            closure_state="TWO_SOLUTIONS",
            selected_pose_available=True,
            joint_center=input_point(1, 2),
        )


def test_sample_requested_angle_must_be_finite():
    with pytest.raises(
        ValidationError,
        match="must be finite",
    ):
        ShieldTopBeamJointTrajectorySample(
            sample_index=0,
            requested_angle_deg=deg(
                math.inf
            ),
            closure_state="TWO_SOLUTIONS",
            selected_pose_available=True,
            joint_center=(
                calculated_point(1, 2)
            ),
        )


def test_completed_increasing_trajectory():
    result = trajectory_result([
        trajectory_sample(0, 0),
        trajectory_sample(1, 5),
        trajectory_sample(2, 10),
    ])

    assert result.termination == "COMPLETED"
    assert len(result.samples) == 3


def test_completed_decreasing_trajectory():
    result = trajectory_result(
        [
            trajectory_sample(0, 20),
            trajectory_sample(1, 10),
            trajectory_sample(2, 0),
        ],
        direction="DECREASING",
        branch="NEGATIVE",
        reference_angle=20,
    )

    assert result.direction == "DECREASING"
    assert result.reference_branch == "NEGATIVE"


def test_tangent_boundary_trajectory():
    result = trajectory_result(
        [
            trajectory_sample(0, 0),
            trajectory_sample(1, 10),
            trajectory_sample(
                2,
                20,
                state="TANGENT",
            ),
        ],
        requested_angle_count=4,
        termination="TANGENT_BOUNDARY",
    )

    assert len(result.samples) == 3

    assert (
        result.samples[-1].closure_state
        == "TANGENT"
    )


def test_no_solution_boundary_trajectory():
    result = trajectory_result(
        [
            trajectory_sample(0, 0),
            trajectory_sample(1, 10),
            trajectory_sample(
                2,
                20,
                state="NO_SOLUTION",
            ),
        ],
        requested_angle_count=5,
        termination="NO_SOLUTION_BOUNDARY",
    )

    assert (
        result.samples[-1].joint_center
        is None
    )


def test_degenerate_boundary_trajectory():
    result = trajectory_result(
        [
            trajectory_sample(0, 0),
            trajectory_sample(1, 10),
            trajectory_sample(
                2,
                20,
                state="DEGENERATE",
            ),
        ],
        requested_angle_count=5,
        termination="DEGENERATE_BOUNDARY",
    )

    assert (
        result.samples[-1].joint_center
        is None
    )


def test_sample_count_cannot_exceed_requested_count():
    with pytest.raises(
        ValidationError,
        match="cannot exceed",
    ):
        trajectory_result(
            [
                trajectory_sample(0, 0),
                trajectory_sample(1, 10),
            ],
            requested_angle_count=1,
        )


def test_completed_requires_all_requested_samples():
    with pytest.raises(
        ValidationError,
        match="must contain every processed requested angle",
    ):
        trajectory_result(
            [
                trajectory_sample(0, 0),
                trajectory_sample(1, 10),
            ],
            requested_angle_count=3,
            termination="COMPLETED",
        )


def test_sample_indexes_must_be_contiguous():
    with pytest.raises(
        ValidationError,
        match="contiguous from zero",
    ):
        trajectory_result([
            trajectory_sample(0, 0),
            trajectory_sample(2, 10),
        ])


def test_first_angle_must_equal_reference_angle():
    with pytest.raises(
        ValidationError,
        match="must equal the reference angle",
    ):
        trajectory_result(
            [
                trajectory_sample(0, 5),
                trajectory_sample(1, 10),
            ],
            reference_angle=0,
        )


def test_increasing_angles_must_remain_increasing():
    with pytest.raises(
        ValidationError,
        match="strictly increasing",
    ):
        trajectory_result([
            trajectory_sample(0, 0),
            trajectory_sample(1, 10),
            trajectory_sample(2, 5),
        ])


def test_decreasing_angles_must_remain_decreasing():
    with pytest.raises(
        ValidationError,
        match="strictly decreasing",
    ):
        trajectory_result(
            [
                trajectory_sample(0, 20),
                trajectory_sample(1, 5),
                trajectory_sample(2, 10),
            ],
            direction="DECREASING",
            branch="NEGATIVE",
            reference_angle=20,
        )


def test_tangent_boundary_requires_final_tangent():
    with pytest.raises(
        ValidationError,
        match="requires a final selected TANGENT",
    ):
        trajectory_result(
            [
                trajectory_sample(0, 0),
                trajectory_sample(1, 10),
            ],
            requested_angle_count=3,
            termination="TANGENT_BOUNDARY",
        )


def test_completed_trajectory_rejects_tangent_sample():
    with pytest.raises(
        ValidationError,
        match="only selected TWO_SOLUTIONS",
    ):
        trajectory_result(
            [
                trajectory_sample(0, 0),
                trajectory_sample(
                    1,
                    10,
                    state="TANGENT",
                ),
            ],
            termination="COMPLETED",
        )


def test_result_provenance_defaults_are_frozen():
    result = trajectory_result([
        trajectory_sample(0, 0),
        trajectory_sample(1, 10),
    ])

    assert (
        result.provenance.engine
        == "W40_SHIELD_TOP_BEAM_JOINT_RIGID_PROPAGATION"
    )

    assert (
        result.provenance.evidence_status
        == "PARTIAL"
    )

    assert result.provenance.formula_ids == []

    assert (
        result.provenance.calculation_record_ids
        == []
    )


def test_result_rejects_unknown_support_height_field():
    with pytest.raises(
        ValidationError,
    ):
        ShieldTopBeamJointTrajectoryResult(
            attachment=attachment(),
            direction="INCREASING",
            reference_branch="POSITIVE",
            reference_angle_deg=deg(0),
            requested_angle_count=2,
            samples=[
                trajectory_sample(0, 0),
                trajectory_sample(1, 10),
            ],
            termination="COMPLETED",
            support_height_mm=input_mm(3000),
        )


def test_result_contains_no_beam_tip_or_support_height_fields():
    result = trajectory_result([
        trajectory_sample(0, 0),
        trajectory_sample(1, 10),
    ])

    payload = result.model_dump(
        mode="json"
    )

    assert "support_height_mm" not in payload
    assert "top_beam_angle_deg" not in payload
    assert "beam_tip_trajectory" not in payload
    assert (
        "beam_tip_horizontal_displacement_mm"
        not in payload
    )


def test_result_json_round_trip():
    original = trajectory_result([
        trajectory_sample(0, 0),
        trajectory_sample(1, 10),
    ])

    rebuilt = (
        ShieldTopBeamJointTrajectoryResult
        .model_validate(
            original.model_dump(
                mode="json"
            )
        )
    )

    assert rebuilt == original


def test_model_construction_does_not_mutate_source_objects():
    source_attachment = attachment()

    source_samples = [
        trajectory_sample(0, 0),
        trajectory_sample(1, 10),
    ]

    attachment_before = (
        source_attachment.model_dump(
            mode="json"
        )
    )

    samples_before = [
        item.model_dump(
            mode="json"
        )
        for item in source_samples
    ]

    ShieldTopBeamJointTrajectoryResult(
        attachment=source_attachment,
        direction="INCREASING",
        reference_branch="POSITIVE",
        reference_angle_deg=deg(0),
        requested_angle_count=2,
        samples=source_samples,
        termination="COMPLETED",
    )

    assert (
        source_attachment.model_dump(
            mode="json"
        )
        == attachment_before
    )

    assert [
        item.model_dump(
            mode="json"
        )
        for item in source_samples
    ] == samples_before
