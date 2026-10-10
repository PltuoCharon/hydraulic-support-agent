import math

import pytest
from pydantic import ValidationError

from app.models.linkage_closure import (
    ClosureSolverInput,
    NumericalTolerance,
)
from app.models.linkage_geometry import (
    DegreeParameter,
    EngineeringPoint2D,
    MillimetreParameter,
)
from app.models.linkage_motion import (
    MotionSample,
    MotionSegmentResult,
    MotionSweepInput,
    MotionSweepProvenance,
)
from app.services.linkage_closure import (
    solve_closure,
)


def mm(value):
    return MillimetreParameter(
        value=value,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
    )


def deg(value):
    return DegreeParameter(
        value=value,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
    )


def point(x, y):
    return EngineeringPoint2D(
        x_mm=mm(x),
        y_mm=mm(y),
    )


def tolerance():
    return NumericalTolerance(
        absolute_mm=1e-9,
        relative=1e-12,
    )


def task(
    *,
    angle=0,
    branch="POSITIVE",
    front_base=(8, 0),
    ab=5,
    bc=5,
    cd=5,
    da=8,
):
    return ClosureSolverInput(
        front_link_base=point(
            *front_base
        ),
        rear_link_length_mm=mm(ab),
        shield_beam_effective_length_mm=mm(bc),
        front_link_length_mm=mm(cd),
        base_pivot_spacing_mm=mm(da),
        rear_link_angle_deg=deg(angle),
        reference_branch=branch,
        tolerance=tolerance(),
    )


def result_at(
    angle,
    *,
    branch="POSITIVE",
):
    return solve_closure(
        task(
            angle=angle,
            branch=branch,
        )
    )


def sample(
    index,
    angle,
    result,
):
    return MotionSample(
        sample_index=index,
        requested_angle_deg=deg(angle),
        closure_result=result,
    )


def completed_segment(
    *,
    branch="POSITIVE",
    direction="INCREASING",
    angles=(0, 5, 10),
):
    samples = [
        sample(
            index,
            angle,
            result_at(
                angle,
                branch=branch,
            ),
        )
        for index, angle
        in enumerate(angles)
    ]

    return MotionSegmentResult(
        direction=direction,
        reference_branch=branch,
        reference_angle_deg=deg(
            angles[0]
        ),
        requested_angle_count=len(
            angles
        ),
        samples=samples,
        termination="COMPLETED",
    )


def tangent_angle():
    # For A=(0,0), D=(8,0), AB=BC=CD=5:
    # q^2 = 89 - 80*cos(theta).
    # External tangent occurs at q=10.
    return math.degrees(
        math.acos(
            -11.0 / 80.0
        )
    )


def tangent_result():
    angle = tangent_angle()

    return (
        angle,
        result_at(
            angle,
            branch="POSITIVE",
        ),
    )


def no_solution_result():
    angle = 120.0

    return (
        angle,
        result_at(
            angle,
            branch="POSITIVE",
        ),
    )


def degenerate_result():
    angle = 10.0

    d_x = 5.0 * math.cos(
        math.radians(angle)
    )

    d_y = 5.0 * math.sin(
        math.radians(angle)
    )

    result = solve_closure(
        task(
            angle=angle,
            branch="POSITIVE",
            front_base=(d_x, d_y),
            ab=5,
            bc=2,
            cd=2,
            da=5,
        )
    )

    return angle, result


def test_valid_increasing_sweep_input():
    reference = task(
        angle=0,
        branch="POSITIVE",
    )

    model = MotionSweepInput(
        reference_task=reference,
        direction="INCREASING",
        angle_samples_deg=[
            deg(0),
            deg(5),
            deg(10),
        ],
    )

    assert model.version == 1
    assert model.direction == "INCREASING"
    assert len(model.angle_samples_deg) == 3


def test_valid_decreasing_sweep_input():
    reference = task(
        angle=20,
        branch="NEGATIVE",
    )

    model = MotionSweepInput(
        reference_task=reference,
        direction="DECREASING",
        angle_samples_deg=[
            deg(20),
            deg(10),
            deg(0),
        ],
    )

    assert model.direction == "DECREASING"


def test_sweep_input_rejects_null_reference_branch():
    reference = task(
        angle=0,
        branch=None,
    )

    with pytest.raises(
        ValidationError,
        match="non-null",
    ):
        MotionSweepInput(
            reference_task=reference,
            direction="INCREASING",
            angle_samples_deg=[
                deg(0),
                deg(5),
            ],
        )


def test_sweep_input_requires_at_least_two_angles():
    with pytest.raises(
        ValidationError,
    ):
        MotionSweepInput(
            reference_task=task(),
            direction="INCREASING",
            angle_samples_deg=[
                deg(0),
            ],
        )


@pytest.mark.parametrize(
    "bad_value",
    [
        math.nan,
        math.inf,
        -math.inf,
    ],
)
def test_sweep_input_rejects_nonfinite_angle(
    bad_value,
):
    with pytest.raises(
        ValidationError,
        match="finite",
    ):
        MotionSweepInput(
            reference_task=task(),
            direction="INCREASING",
            angle_samples_deg=[
                deg(0),
                deg(bad_value),
            ],
        )


def test_sweep_input_requires_reference_angle_first():
    with pytest.raises(
        ValidationError,
        match="first motion angle",
    ):
        MotionSweepInput(
            reference_task=task(
                angle=0,
            ),
            direction="INCREASING",
            angle_samples_deg=[
                deg(1),
                deg(2),
            ],
        )


def test_increasing_rejects_duplicate_angle():
    with pytest.raises(
        ValidationError,
        match="strictly increasing",
    ):
        MotionSweepInput(
            reference_task=task(),
            direction="INCREASING",
            angle_samples_deg=[
                deg(0),
                deg(5),
                deg(5),
            ],
        )


def test_increasing_rejects_decreasing_angle():
    with pytest.raises(
        ValidationError,
        match="strictly increasing",
    ):
        MotionSweepInput(
            reference_task=task(),
            direction="INCREASING",
            angle_samples_deg=[
                deg(0),
                deg(5),
                deg(4),
            ],
        )


def test_decreasing_rejects_increasing_angle():
    with pytest.raises(
        ValidationError,
        match="strictly decreasing",
    ):
        MotionSweepInput(
            reference_task=task(
                angle=10,
                branch="NEGATIVE",
            ),
            direction="DECREASING",
            angle_samples_deg=[
                deg(10),
                deg(5),
                deg(6),
            ],
        )


def test_motion_models_forbid_extra_fields():
    with pytest.raises(
        ValidationError,
    ):
        MotionSweepInput(
            reference_task=task(),
            direction="INCREASING",
            angle_samples_deg=[
                deg(0),
                deg(5),
            ],
            support_height_mm=3000,
        )


def test_sweep_input_does_not_mutate_sources():
    reference = task()

    angles = [
        deg(0),
        deg(5),
        deg(10),
    ]

    reference_snapshot = (
        reference.model_dump(
            mode="json"
        )
    )

    angle_snapshot = [
        item.model_dump(
            mode="json"
        )
        for item in angles
    ]

    MotionSweepInput(
        reference_task=reference,
        direction="INCREASING",
        angle_samples_deg=angles,
    )

    assert (
        reference.model_dump(
            mode="json"
        )
        == reference_snapshot
    )

    assert [
        item.model_dump(
            mode="json"
        )
        for item in angles
    ] == angle_snapshot


def test_motion_sample_requires_nonnegative_index():
    with pytest.raises(
        ValidationError,
    ):
        MotionSample(
            sample_index=-1,
            requested_angle_deg=deg(0),
            closure_result=result_at(0),
        )


def test_motion_sweep_provenance_defaults():
    provenance = MotionSweepProvenance()

    assert (
        provenance.engine
        == "W40_BRANCH_PRESERVING_ANGLE_SWEEP"
    )

    assert (
        provenance.evidence_status
        == "PARTIAL"
    )

    assert provenance.formula_ids == []

    assert (
        provenance.calculation_record_ids
        == []
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "formula_ids": [
                "F-FAKE-001",
            ]
        },
        {
            "calculation_record_ids": [
                1,
            ]
        },
    ],
)
def test_motion_provenance_rejects_fake_trace(
    kwargs,
):
    with pytest.raises(
        ValidationError,
    ):
        MotionSweepProvenance(
            **kwargs
        )


def test_completed_positive_segment_is_valid():
    segment = completed_segment(
        branch="POSITIVE",
    )

    assert segment.termination == "COMPLETED"

    assert [
        item.closure_result
        .selected_pose.branch
        for item in segment.samples
    ] == [
        "POSITIVE",
        "POSITIVE",
        "POSITIVE",
    ]


def test_completed_negative_segment_is_valid():
    segment = completed_segment(
        branch="NEGATIVE",
    )

    assert [
        item.closure_result
        .selected_pose.branch
        for item in segment.samples
    ] == [
        "NEGATIVE",
        "NEGATIVE",
        "NEGATIVE",
    ]


def test_completed_requires_every_requested_angle():
    base = completed_segment()

    payload = base.model_dump(
        mode="python"
    )

    payload["requested_angle_count"] = 4

    with pytest.raises(
        ValidationError,
        match="process every requested angle",
    ):
        MotionSegmentResult.model_validate(
            payload
        )


def test_completed_rejects_boundary_sample():
    angle, tangent = tangent_result()

    with pytest.raises(
        ValidationError,
        match="COMPLETED",
    ):
        MotionSegmentResult(
            direction="INCREASING",
            reference_branch="POSITIVE",
            reference_angle_deg=deg(0),
            requested_angle_count=2,
            samples=[
                sample(
                    0,
                    0,
                    result_at(0),
                ),
                sample(
                    1,
                    angle,
                    tangent,
                ),
            ],
            termination="COMPLETED",
        )


def test_segment_rejects_opposite_selected_branch():
    with pytest.raises(
        ValidationError,
        match="reference branch",
    ):
        MotionSegmentResult(
            direction="INCREASING",
            reference_branch="POSITIVE",
            reference_angle_deg=deg(0),
            requested_angle_count=2,
            samples=[
                sample(
                    0,
                    0,
                    result_at(
                        0,
                        branch="POSITIVE",
                    ),
                ),
                sample(
                    1,
                    5,
                    result_at(
                        5,
                        branch="NEGATIVE",
                    ),
                ),
            ],
            termination="COMPLETED",
        )


def test_segment_rejects_noncontiguous_indexes():
    with pytest.raises(
        ValidationError,
        match="indexes",
    ):
        MotionSegmentResult(
            direction="INCREASING",
            reference_branch="POSITIVE",
            reference_angle_deg=deg(0),
            requested_angle_count=2,
            samples=[
                sample(
                    0,
                    0,
                    result_at(0),
                ),
                sample(
                    2,
                    5,
                    result_at(5),
                ),
            ],
            termination="COMPLETED",
        )


def test_segment_rejects_wrong_result_angle_order():
    with pytest.raises(
        ValidationError,
        match="strictly increasing",
    ):
        MotionSegmentResult(
            direction="INCREASING",
            reference_branch="POSITIVE",
            reference_angle_deg=deg(0),
            requested_angle_count=3,
            samples=[
                sample(
                    0,
                    0,
                    result_at(0),
                ),
                sample(
                    1,
                    10,
                    result_at(10),
                ),
                sample(
                    2,
                    5,
                    result_at(5),
                ),
            ],
            termination="COMPLETED",
        )


def test_segment_requires_reference_angle_as_first_sample():
    with pytest.raises(
        ValidationError,
        match="reference angle",
    ):
        MotionSegmentResult(
            direction="INCREASING",
            reference_branch="POSITIVE",
            reference_angle_deg=deg(0),
            requested_angle_count=2,
            samples=[
                sample(
                    0,
                    1,
                    result_at(1),
                ),
                sample(
                    1,
                    2,
                    result_at(2),
                ),
            ],
            termination="COMPLETED",
        )


def test_tangent_boundary_is_valid():
    angle, tangent = tangent_result()

    segment = MotionSegmentResult(
        direction="INCREASING",
        reference_branch="POSITIVE",
        reference_angle_deg=deg(0),
        requested_angle_count=3,
        samples=[
            sample(
                0,
                0,
                result_at(0),
            ),
            sample(
                1,
                30,
                result_at(30),
            ),
            sample(
                2,
                angle,
                tangent,
            ),
        ],
        termination="TANGENT_BOUNDARY",
    )

    assert (
        segment.samples[-1]
        .closure_result.closure_state
        == "TANGENT"
    )


def test_tangent_boundary_requires_final_tangent():
    with pytest.raises(
        ValidationError,
        match="final TANGENT",
    ):
        MotionSegmentResult(
            direction="INCREASING",
            reference_branch="POSITIVE",
            reference_angle_deg=deg(0),
            requested_angle_count=2,
            samples=[
                sample(
                    0,
                    0,
                    result_at(0),
                ),
                sample(
                    1,
                    5,
                    result_at(5),
                ),
            ],
            termination="TANGENT_BOUNDARY",
        )


def test_no_solution_boundary_is_valid():
    angle, failure = no_solution_result()

    segment = MotionSegmentResult(
        direction="INCREASING",
        reference_branch="POSITIVE",
        reference_angle_deg=deg(0),
        requested_angle_count=3,
        samples=[
            sample(
                0,
                0,
                result_at(0),
            ),
            sample(
                1,
                30,
                result_at(30),
            ),
            sample(
                2,
                angle,
                failure,
            ),
        ],
        termination="NO_SOLUTION_BOUNDARY",
    )

    assert (
        segment.samples[-1]
        .closure_result.closure_state
        == "NO_SOLUTION"
    )

    assert (
        segment.samples[-1]
        .closure_result.selected_pose
        is None
    )


def test_degenerate_boundary_is_valid():
    angle = 10.0

    d_x = 5.0 * math.cos(
        math.radians(angle)
    )

    d_y = 5.0 * math.sin(
        math.radians(angle)
    )

    reference_result = solve_closure(
        task(
            angle=0,
            branch="POSITIVE",
            front_base=(d_x, d_y),
            ab=5,
            bc=2,
            cd=2,
            da=5,
        )
    )

    _, boundary = degenerate_result()

    segment = MotionSegmentResult(
        direction="INCREASING",
        reference_branch="POSITIVE",
        reference_angle_deg=deg(0),
        requested_angle_count=2,
        samples=[
            sample(
                0,
                0,
                reference_result,
            ),
            sample(
                1,
                angle,
                boundary,
            ),
        ],
        termination="DEGENERATE_BOUNDARY",
    )

    assert (
        segment.samples[-1]
        .closure_result.closure_state
        == "DEGENERATE"
    )


def test_boundary_cannot_have_post_boundary_sample():
    angle, tangent = tangent_result()

    with pytest.raises(
        ValidationError,
    ):
        MotionSegmentResult(
            direction="INCREASING",
            reference_branch="POSITIVE",
            reference_angle_deg=deg(0),
            requested_angle_count=3,
            samples=[
                sample(
                    0,
                    0,
                    result_at(0),
                ),
                sample(
                    1,
                    angle,
                    tangent,
                ),
                sample(
                    2,
                    angle + 1,
                    result_at(
                        angle + 1,
                    ),
                ),
            ],
            termination="TANGENT_BOUNDARY",
        )


def test_ambiguous_two_solution_is_invalid():
    ambiguous = result_at(
        5,
        branch=None,
    )

    assert (
        ambiguous.selection_status
        == "BRANCH_AMBIGUOUS"
    )

    with pytest.raises(
        ValidationError,
        match="ambiguous",
    ):
        MotionSegmentResult(
            direction="INCREASING",
            reference_branch="POSITIVE",
            reference_angle_deg=deg(0),
            requested_angle_count=2,
            samples=[
                sample(
                    0,
                    0,
                    result_at(0),
                ),
                sample(
                    1,
                    5,
                    ambiguous,
                ),
            ],
            termination="COMPLETED",
        )


def test_motion_sample_preserves_w39_candidates():
    closure = result_at(
        5,
        branch="POSITIVE",
    )

    motion_sample = sample(
        0,
        5,
        closure,
    )

    assert len(
        motion_sample
        .closure_result
        .candidates
    ) == 2

    assert {
        candidate.branch
        for candidate
        in motion_sample
        .closure_result
        .candidates
    } == {
        "POSITIVE",
        "NEGATIVE",
    }


def test_motion_result_has_no_support_height_or_top_beam_fields():
    fields = (
        MotionSegmentResult
        .model_fields
    )

    assert "support_height_mm" not in fields
    assert "top_beam_pose" not in fields
    assert "beam_tip_trajectory" not in fields


def test_motion_models_round_trip_through_json_payload():
    original = completed_segment()

    payload = original.model_dump(
        mode="json"
    )

    restored = (
        MotionSegmentResult
        .model_validate(
            payload
        )
    )

    assert restored == original


def test_result_construction_does_not_mutate_w39_results():
    closure_a = result_at(0)
    closure_b = result_at(5)

    before_a = closure_a.model_dump(
        mode="json"
    )

    before_b = closure_b.model_dump(
        mode="json"
    )

    MotionSegmentResult(
        direction="INCREASING",
        reference_branch="POSITIVE",
        reference_angle_deg=deg(0),
        requested_angle_count=2,
        samples=[
            sample(
                0,
                0,
                closure_a,
            ),
            sample(
                1,
                5,
                closure_b,
            ),
        ],
        termination="COMPLETED",
    )

    assert (
        closure_a.model_dump(
            mode="json"
        )
        == before_a
    )

    assert (
        closure_b.model_dump(
            mode="json"
        )
        == before_b
    )
