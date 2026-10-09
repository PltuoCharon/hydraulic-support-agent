import csv
import math
from pathlib import Path

import pytest

from app.models.linkage_closure import (
    ClosureSolverInput,
    NumericalTolerance,
)
from app.models.linkage_geometry import (
    DegreeParameter,
    EngineeringPoint2D,
    MillimetreParameter,
)
from app.services.linkage_closure import (
    calculate_rear_link_shield,
    solve_closure_candidates,
)


ROOT = Path(__file__).resolve().parents[1]

BENCHMARKS = (
    ROOT
    / "docs/evidence/w39/W39D1_closure_benchmarks.csv"
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
):
    return DegreeParameter(
        value=value,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
    )


def point(
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


def tolerance(
    absolute_mm=1e-9,
    relative=1e-12,
):
    return NumericalTolerance(
        absolute_mm=absolute_mm,
        relative=relative,
    )


def task(
    *,
    d_x=8,
    d_y=0,
    ab=5,
    theta=0,
    bc=5,
    cd=5,
    da=None,
    reference_branch=None,
    numerical_tolerance=None,
):
    if da is None:
        da = math.hypot(
            d_x,
            d_y,
        )

    return ClosureSolverInput(
        front_link_base=point(
            d_x,
            d_y,
            role="front_link_base",
        ),
        rear_link_length_mm=mm(ab),
        shield_beam_effective_length_mm=mm(bc),
        front_link_length_mm=mm(cd),
        base_pivot_spacing_mm=mm(da),
        rear_link_angle_deg=deg(theta),
        reference_branch=reference_branch,
        tolerance=(
            numerical_tolerance
            or tolerance()
        ),
    )


def synthetic_rows():
    with BENCHMARKS.open(
        encoding="utf-8",
        newline="",
    ) as f:
        rows = list(
            csv.DictReader(f)
        )

    return {
        row["case_id"]: row
        for row in rows
        if (
            row["benchmark_class"]
            == "SYNTHETIC_MATH"
        )
    }


def task_from_benchmark(
    case_id,
):
    row = synthetic_rows()[case_id]

    ax = float(row["A_x_mm"])
    ay = float(row["A_y_mm"])

    assert ax == 0
    assert ay == 0

    d_x = float(row["D_x_mm"])
    d_y = float(row["D_y_mm"])

    return task(
        d_x=d_x,
        d_y=d_y,
        ab=float(row["AB_mm"]),
        theta=float(
            row["rear_link_angle_deg"]
        ),
        bc=float(row["BC_mm"]),
        cd=float(row["CD_mm"]),
        da=math.hypot(
            d_x - ax,
            d_y - ay,
        ),
    )


def test_point_b_at_zero_degrees():
    result = calculate_rear_link_shield(
        task()
    )

    assert result.x_mm.value == pytest.approx(
        5.0
    )
    assert result.y_mm.value == pytest.approx(
        0.0
    )

    assert result.point_role == "rear_link_shield"


def test_point_b_at_ninety_degrees():
    result = calculate_rear_link_shield(
        task(
            theta=90,
        )
    )

    assert result.x_mm.value == pytest.approx(
        0.0,
        abs=1e-12,
    )

    assert result.y_mm.value == pytest.approx(
        5.0
    )


def test_point_b_has_calculated_partial_provenance():
    result = calculate_rear_link_shield(
        task()
    )

    for parameter in (
        result.x_mm,
        result.y_mm,
    ):
        assert parameter.origin == "CALCULATED"
        assert (
            parameter.evidence_status
            == "PARTIAL"
        )
        assert parameter.formula_ids == []
        assert (
            parameter.calculation_record_ids
            == []
        )

        assert (
            parameter.source_text
            == "W39-D3 deterministic four-bar "
            "closure calculation"
        )


def test_base_spacing_mismatch_is_explicit_failure():
    with pytest.raises(
        ValueError,
        match="inconsistent",
    ):
        solve_closure_candidates(
            task(
                da=9,
            )
        )


def test_base_spacing_mismatch_is_not_no_solution():
    with pytest.raises(ValueError):
        solve_closure_candidates(
            task(
                da=9,
            )
        )


def test_base_spacing_difference_within_tolerance_is_accepted():
    result = solve_closure_candidates(
        task(
            d_x=8.0 + 5e-10,
            da=8.0,
        )
    )

    assert (
        result.closure_state
        == "TWO_SOLUTIONS"
    )


@pytest.mark.parametrize(
    "case_id,expected",
    [
        ("SM-001", "TWO_SOLUTIONS"),
        ("SM-002", "TANGENT"),
        ("SM-003", "NO_SOLUTION"),
        ("SM-004", "NO_SOLUTION"),
        ("SM-005", "DEGENERATE"),
        ("SM-006", "NO_SOLUTION"),
    ],
)
def test_all_synthetic_benchmarks_match_frozen_state(
    case_id,
    expected,
):
    result = solve_closure_candidates(
        task_from_benchmark(
            case_id
        )
    )

    assert result.closure_state == expected


def test_sm001_two_solution_candidate_order_is_stable():
    result = solve_closure_candidates(
        task_from_benchmark(
            "SM-001"
        )
    )

    assert [
        candidate.branch
        for candidate in result.candidates
    ] == [
        "POSITIVE",
        "NEGATIVE",
    ]


def test_sm001_candidate_coordinates_are_expected():
    result = solve_closure_candidates(
        task_from_benchmark(
            "SM-001"
        )
    )

    positive = result.candidates[0].point_c
    negative = result.candidates[1].point_c

    expected_h = math.sqrt(
        25.0 - 1.5 * 1.5
    )

    assert positive.x_mm.value == pytest.approx(
        6.5
    )

    assert positive.y_mm.value == pytest.approx(
        expected_h
    )

    assert negative.x_mm.value == pytest.approx(
        6.5
    )

    assert negative.y_mm.value == pytest.approx(
        -expected_h
    )


def test_sm001_two_solution_remains_ambiguous():
    result = solve_closure_candidates(
        task_from_benchmark(
            "SM-001"
        )
    )

    assert (
        result.selection_status
        == "BRANCH_AMBIGUOUS"
    )

    assert result.selected_pose is None

    assert (
        result.provenance.branch_resolution
        == "NONE"
    )


@pytest.mark.parametrize(
    "reference_branch",
    [
        "POSITIVE",
        "NEGATIVE",
    ],
)
def test_d3_ignores_reference_branch_for_two_solutions(
    reference_branch,
):
    benchmark_task = task_from_benchmark(
        "SM-001"
    )

    modified = benchmark_task.model_copy(
        update={
            "reference_branch": (
                reference_branch
            ),
        }
    )

    result = solve_closure_candidates(
        modified
    )

    assert (
        result.closure_state
        == "TWO_SOLUTIONS"
    )

    assert (
        result.selection_status
        == "BRANCH_AMBIGUOUS"
    )

    assert result.selected_pose is None


def test_sm002_tangent_has_one_selected_candidate():
    result = solve_closure_candidates(
        task_from_benchmark(
            "SM-002"
        )
    )

    assert result.closure_state == "TANGENT"

    assert len(result.candidates) == 1

    assert (
        result.candidates[0].branch
        == "TANGENT"
    )

    assert (
        result.selection_status
        == "SELECTED"
    )

    assert result.selected_pose is not None

    assert (
        result.provenance.branch_resolution
        == "TANGENT_UNIQUE"
    )


def test_sm002_tangent_coordinate_is_expected():
    result = solve_closure_candidates(
        task_from_benchmark(
            "SM-002"
        )
    )

    point_c = (
        result.candidates[0].point_c
    )

    assert point_c.x_mm.value == pytest.approx(
        6.0
    )

    assert point_c.y_mm.value == pytest.approx(
        0.0
    )

    assert (
        result.selected_pose.front_link_shield
        == point_c
    )


@pytest.mark.parametrize(
    "case_id",
    [
        "SM-003",
        "SM-004",
        "SM-006",
    ],
)
def test_no_solution_has_no_candidate_or_selected_pose(
    case_id,
):
    result = solve_closure_candidates(
        task_from_benchmark(
            case_id
        )
    )

    assert (
        result.closure_state
        == "NO_SOLUTION"
    )

    assert result.candidates == []
    assert result.selected_pose is None

    assert (
        result.selection_status
        == "NOT_APPLICABLE"
    )

    assert (
        result.provenance.branch_resolution
        == "NONE"
    )


def test_sm005_degenerate_has_no_arbitrary_candidate():
    result = solve_closure_candidates(
        task_from_benchmark(
            "SM-005"
        )
    )

    assert (
        result.closure_state
        == "DEGENERATE"
    )

    assert result.candidates == []
    assert result.selected_pose is None

    assert (
        result.selection_status
        == "NOT_APPLICABLE"
    )


def test_internal_tangent_is_supported():
    result = solve_closure_candidates(
        task(
            d_x=8,
            ab=5,
            theta=0,
            bc=5,
            cd=2,
            da=8,
        )
    )

    # B=(5,0), D=(8,0), q=3.
    # |BC-CD| = |5-2| = 3.
    assert result.closure_state == "TANGENT"
    assert len(result.candidates) == 1
    assert (
        result.candidates[0].branch
        == "TANGENT"
    )


def test_candidate_coordinates_preserve_d3_provenance():
    result = solve_closure_candidates(
        task_from_benchmark(
            "SM-001"
        )
    )

    for candidate in result.candidates:
        for parameter in (
            candidate.point_c.x_mm,
            candidate.point_c.y_mm,
        ):
            assert (
                parameter.origin
                == "CALCULATED"
            )

            assert (
                parameter.evidence_status
                == "PARTIAL"
            )

            assert parameter.formula_ids == []

            assert (
                parameter.calculation_record_ids
                == []
            )


def test_solver_does_not_mutate_input():
    original = task_from_benchmark(
        "SM-001"
    )

    snapshot = original.model_dump(
        mode="json"
    )

    solve_closure_candidates(
        original
    )

    assert (
        original.model_dump(
            mode="json"
        )
        == snapshot
    )


def test_solver_is_deterministic_for_same_input():
    input_task = task_from_benchmark(
        "SM-001"
    )

    first = solve_closure_candidates(
        input_task
    )

    second = solve_closure_candidates(
        input_task
    )

    assert first == second
