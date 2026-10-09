import math

import pytest
from pydantic import ValidationError

from app.models.linkage_closure import (
    ClosureCandidate,
    ClosureResult,
    ClosureSelectedPose,
    ClosureSolverInput,
    ClosureSolverProvenance,
    NumericalTolerance,
    serialize_closure_result,
    validate_closure_result,
    validate_closure_solver_input,
)
from app.models.linkage_geometry import (
    DegreeParameter,
    EngineeringPoint2D,
    MillimetreParameter,
)


def mm(
    value,
    *,
    origin="USER_INPUT",
    evidence_status="EVIDENCE_GAP",
):
    return MillimetreParameter(
        value=value,
        origin=origin,
        evidence_status=evidence_status,
    )


def deg(
    value,
    *,
    origin="USER_INPUT",
    evidence_status="EVIDENCE_GAP",
):
    return DegreeParameter(
        value=value,
        origin=origin,
        evidence_status=evidence_status,
    )


def input_point(
    x,
    y,
    *,
    role=None,
):
    return EngineeringPoint2D(
        x_mm=mm(x),
        y_mm=mm(y),
        point_role=role,
    )


def calculated_mm(value):
    return MillimetreParameter(
        value=value,
        origin="CALCULATED",
        evidence_status="PARTIAL",
    )


def calculated_point(
    x,
    y,
    *,
    role=None,
):
    return EngineeringPoint2D(
        x_mm=calculated_mm(x),
        y_mm=calculated_mm(y),
        point_role=role,
    )


def tolerance():
    return NumericalTolerance(
        absolute_mm=1e-9,
        relative=1e-12,
    )


def solver_input(**updates):
    data = {
        "front_link_base": input_point(
            1000,
            0,
            role="front_link_base",
        ),
        "rear_link_length_mm": mm(800),
        "shield_beam_effective_length_mm": mm(900),
        "front_link_length_mm": mm(700),
        "base_pivot_spacing_mm": mm(1000),
        "rear_link_angle_deg": deg(45),
        "reference_branch": None,
        "tolerance": tolerance(),
    }

    data.update(updates)

    return ClosureSolverInput(**data)


def candidate(branch, x, y):
    return ClosureCandidate(
        point_c=calculated_point(
            x,
            y,
            role="front_link_shield",
        ),
        branch=branch,
    )


def selected_pose(
    branch,
    *,
    b=(500, 500),
    c=(900, 700),
):
    return ClosureSelectedPose(
        rear_link_shield=calculated_point(
            b[0],
            b[1],
            role="rear_link_shield",
        ),
        front_link_shield=calculated_point(
            c[0],
            c[1],
            role="front_link_shield",
        ),
        rear_link_angle_deg=deg(45),
        branch=branch,
    )


def provenance(branch_resolution="NONE"):
    return ClosureSolverProvenance(
        branch_resolution=branch_resolution,
    )


def solved_b():
    return calculated_point(
        500,
        500,
        role="rear_link_shield",
    )


def test_numerical_tolerance_accepts_explicit_positive_values():
    t = tolerance()

    assert t.absolute_mm == 1e-9
    assert t.relative == 1e-12


@pytest.mark.parametrize(
    "field,value",
    [
        ("absolute_mm", 0),
        ("absolute_mm", -1),
        ("absolute_mm", math.inf),
        ("absolute_mm", math.nan),
        ("relative", 0),
        ("relative", -1),
        ("relative", math.inf),
        ("relative", math.nan),
    ],
)
def test_numerical_tolerance_rejects_invalid_values(
    field,
    value,
):
    payload = {
        "absolute_mm": 1e-9,
        "relative": 1e-12,
    }

    payload[field] = value

    with pytest.raises(ValidationError):
        NumericalTolerance(**payload)


def test_solver_input_reuses_w38_geometry_types():
    task = solver_input()

    assert task.version == 1
    assert task.rear_link_base.x_mm == 0
    assert task.rear_link_base.y_mm == 0

    assert task.front_link_base.x_mm.value == 1000
    assert task.rear_link_length_mm.value == 800
    assert task.rear_link_angle_deg.value == 45


def test_solver_input_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        solver_input(
            unexpected_field=123,
        )


@pytest.mark.parametrize(
    "field",
    [
        "rear_link_length_mm",
        "shield_beam_effective_length_mm",
        "front_link_length_mm",
        "base_pivot_spacing_mm",
    ],
)
def test_solver_input_rejects_nonpositive_link_lengths(
    field,
):
    with pytest.raises(ValidationError):
        solver_input(
            **{
                field: mm(0),
            }
        )


def test_solver_input_rejects_nonfinite_angle():
    with pytest.raises(ValidationError):
        solver_input(
            rear_link_angle_deg=deg(
                math.inf
            )
        )


def test_reference_branch_does_not_accept_tangent():
    with pytest.raises(ValidationError):
        solver_input(
            reference_branch="TANGENT"
        )


def test_solver_input_contains_no_support_height_or_canopy_fields():
    fields = ClosureSolverInput.model_fields

    assert "support_height_mm" not in fields
    assert "canopy_len" not in fields
    assert "center_dist" not in fields


def test_candidate_requires_calculated_partial_coordinate():
    good = candidate(
        "POSITIVE",
        900,
        700,
    )

    assert good.branch == "POSITIVE"
    assert (
        good.point_c.x_mm.origin
        == "CALCULATED"
    )
    assert (
        good.point_c.x_mm.evidence_status
        == "PARTIAL"
    )

    with pytest.raises(ValidationError):
        ClosureCandidate(
            point_c=input_point(
                900,
                700,
            ),
            branch="POSITIVE",
        )


def test_provenance_rejects_fake_formula_ids():
    with pytest.raises(ValidationError):
        ClosureSolverProvenance(
            formula_ids=[
                "F-JACK-FAKE",
            ]
        )


def test_provenance_rejects_fake_calculation_record():
    with pytest.raises(ValidationError):
        ClosureSolverProvenance(
            calculation_record_ids=[
                123,
            ]
        )


def test_no_solution_valid_result():
    result = ClosureResult(
        closure_state="NO_SOLUTION",
        selection_status="NOT_APPLICABLE",
        rear_link_shield=solved_b(),
    )

    assert result.candidates == []
    assert result.selected_pose is None
    assert (
        result.provenance.branch_resolution
        == "NONE"
    )


def test_no_solution_rejects_candidate():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="NO_SOLUTION",
            selection_status="NOT_APPLICABLE",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "POSITIVE",
                    900,
                    700,
                )
            ],
        )


def test_degenerate_valid_result_has_no_arbitrary_candidate():
    result = ClosureResult(
        closure_state="DEGENERATE",
        selection_status="NOT_APPLICABLE",
        rear_link_shield=solved_b(),
    )

    assert result.candidates == []
    assert result.selected_pose is None


def test_tangent_valid_result_is_uniquely_selected():
    c = candidate(
        "TANGENT",
        900,
        0,
    )

    pose = selected_pose(
        "TANGENT",
        c=(900, 0),
    )

    result = ClosureResult(
        closure_state="TANGENT",
        selection_status="SELECTED",
        rear_link_shield=solved_b(),
        candidates=[c],
        selected_pose=pose,
        provenance=provenance(
            "TANGENT_UNIQUE"
        ),
    )

    assert len(result.candidates) == 1
    assert (
        result.selected_pose.branch
        == "TANGENT"
    )


def test_tangent_rejects_positive_candidate():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="TANGENT",
            selection_status="SELECTED",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "POSITIVE",
                    900,
                    0,
                )
            ],
            selected_pose=selected_pose(
                "TANGENT",
                c=(900, 0),
            ),
            provenance=provenance(
                "TANGENT_UNIQUE"
            ),
        )


def test_two_solutions_can_remain_branch_ambiguous():
    result = ClosureResult(
        closure_state="TWO_SOLUTIONS",
        selection_status="BRANCH_AMBIGUOUS",
        rear_link_shield=solved_b(),
        candidates=[
            candidate(
                "POSITIVE",
                900,
                700,
            ),
            candidate(
                "NEGATIVE",
                900,
                -700,
            ),
        ],
    )

    assert result.selected_pose is None
    assert (
        result.provenance.branch_resolution
        == "NONE"
    )


def test_two_solutions_can_select_reference_branch():
    result = ClosureResult(
        closure_state="TWO_SOLUTIONS",
        selection_status="SELECTED",
        rear_link_shield=solved_b(),
        candidates=[
            candidate(
                "POSITIVE",
                900,
                700,
            ),
            candidate(
                "NEGATIVE",
                900,
                -700,
            ),
        ],
        selected_pose=selected_pose(
            "POSITIVE",
            c=(900, 700),
        ),
        provenance=provenance(
            "REFERENCE_POSE"
        ),
    )

    assert result.selected_pose is not None
    assert (
        result.selected_pose.branch
        == "POSITIVE"
    )


def test_two_solutions_reject_duplicate_positive_branches():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="TWO_SOLUTIONS",
            selection_status="BRANCH_AMBIGUOUS",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "POSITIVE",
                    900,
                    700,
                ),
                candidate(
                    "POSITIVE",
                    900,
                    -700,
                ),
            ],
        )


def test_two_solutions_reject_tangent_candidate():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="TWO_SOLUTIONS",
            selection_status="BRANCH_AMBIGUOUS",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "POSITIVE",
                    900,
                    700,
                ),
                candidate(
                    "TANGENT",
                    900,
                    0,
                ),
            ],
        )


def test_branch_ambiguous_rejects_selected_pose():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="TWO_SOLUTIONS",
            selection_status="BRANCH_AMBIGUOUS",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "POSITIVE",
                    900,
                    700,
                ),
                candidate(
                    "NEGATIVE",
                    900,
                    -700,
                ),
            ],
            selected_pose=selected_pose(
                "POSITIVE"
            ),
        )


def test_selected_requires_selected_pose():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="TWO_SOLUTIONS",
            selection_status="SELECTED",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "POSITIVE",
                    900,
                    700,
                ),
                candidate(
                    "NEGATIVE",
                    900,
                    -700,
                ),
            ],
            provenance=provenance(
                "REFERENCE_POSE"
            ),
        )


def test_selected_two_solution_requires_reference_resolution():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="TWO_SOLUTIONS",
            selection_status="SELECTED",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "POSITIVE",
                    900,
                    700,
                ),
                candidate(
                    "NEGATIVE",
                    900,
                    -700,
                ),
            ],
            selected_pose=selected_pose(
                "POSITIVE"
            ),
            provenance=provenance(
                "NONE"
            ),
        )


def test_result_rejects_unexpected_field():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="NO_SOLUTION",
            selection_status="NOT_APPLICABLE",
            rear_link_shield=solved_b(),
            unexpected_field=True,
        )


def test_solver_input_and_result_helpers_round_trip():
    task = solver_input(
        reference_branch="POSITIVE"
    )

    rebuilt_task = validate_closure_solver_input(
        task.model_dump(mode="json")
    )

    assert rebuilt_task == task

    result = ClosureResult(
        closure_state="NO_SOLUTION",
        selection_status="NOT_APPLICABLE",
        rear_link_shield=solved_b(),
    )

    payload = serialize_closure_result(
        result
    )

    rebuilt_result = validate_closure_result(
        payload
    )

    assert rebuilt_result == result
    assert payload["version"] == 1


def test_selected_pose_rear_link_shield_must_match_result_b():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="TWO_SOLUTIONS",
            selection_status="SELECTED",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "POSITIVE",
                    900,
                    700,
                ),
                candidate(
                    "NEGATIVE",
                    900,
                    -700,
                ),
            ],
            selected_pose=selected_pose(
                "POSITIVE",
                b=(501, 500),
                c=(900, 700),
            ),
            provenance=provenance(
                "REFERENCE_POSE"
            ),
        )


def test_tangent_selected_pose_must_match_candidate_point():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="TANGENT",
            selection_status="SELECTED",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "TANGENT",
                    900,
                    0,
                )
            ],
            selected_pose=selected_pose(
                "TANGENT",
                c=(901, 0),
            ),
            provenance=provenance(
                "TANGENT_UNIQUE"
            ),
        )


def test_two_solution_selected_pose_must_match_selected_candidate():
    with pytest.raises(ValidationError):
        ClosureResult(
            closure_state="TWO_SOLUTIONS",
            selection_status="SELECTED",
            rear_link_shield=solved_b(),
            candidates=[
                candidate(
                    "POSITIVE",
                    900,
                    700,
                ),
                candidate(
                    "NEGATIVE",
                    900,
                    -700,
                ),
            ],
            selected_pose=selected_pose(
                "POSITIVE",
                c=(901, 700),
            ),
            provenance=provenance(
                "REFERENCE_POSE"
            ),
        )
