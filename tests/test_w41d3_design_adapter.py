import csv
from pathlib import Path

import pytest

from app.models.linkage_optimization import CandidateDesignInput, DESIGN_VARIABLE_ORDER
from app.services.linkage_optimization_adapters import build_closure_task_from_design
from app.services.linkage_closure import solve_closure
from test_w41d3_design_vector_model import parameter, payload


def test_mapping_nonhorizontal_base_and_no_mutation():
    data = payload()
    data["configuration"]["front_link_base"] = dict(x_mm=parameter(6), y_mm=parameter(8))
    for name, value in zip(DESIGN_VARIABLE_ORDER, (4, 7, 9)):
        data["design"][name] = parameter(value)
    candidate = CandidateDesignInput.model_validate(data)
    before = candidate.model_dump()
    task = build_closure_task_from_design(candidate)
    assert task.base_pivot_spacing_mm.value == 10
    assert task.base_pivot_spacing_mm.origin == "CALCULATED"
    assert task.base_pivot_spacing_mm.evidence_status == "PARTIAL"
    assert tuple(getattr(task, n).value for n in DESIGN_VARIABLE_ORDER) == (4, 7, 9)
    assert task.front_link_base.y_mm.value == 8
    task.rear_link_length_mm.value = 12
    assert candidate.model_dump() == before


@pytest.mark.parametrize("declared,accepted", [(8, True), (8 + 1e-10, True), (9, False)])
def test_declared_ad(declared, accepted):
    data = payload()
    data["configuration"]["declared_base_pivot_spacing_mm"] = parameter(declared)
    if accepted:
        task = build_closure_task_from_design(CandidateDesignInput.model_validate(data))
        assert task.base_pivot_spacing_mm.value == 8
    else:
        with pytest.raises(ValueError, match="inconsistent"):
            CandidateDesignInput.model_validate(data)


ROWS = list(csv.DictReader((Path(__file__).resolve().parents[1] /
                           "docs/evidence/w39/W39D1_closure_benchmarks.csv").open()))[:6]


@pytest.mark.parametrize("row", ROWS, ids=[r["case_id"] for r in ROWS])
def test_existing_synthetic_states(row):
    data = payload()
    data["case"]["case_id"] = row["case_id"]
    for name, column in zip(DESIGN_VARIABLE_ORDER, ("AB_mm", "BC_mm", "CD_mm")):
        data["design"][name] = parameter(float(row[column]))
    data["configuration"]["front_link_base"] = dict(
        x_mm=parameter(float(row["D_x_mm"])), y_mm=parameter(float(row["D_y_mm"])))
    result = solve_closure(build_closure_task_from_design(CandidateDesignInput.model_validate(data)))
    assert result.closure_state == row["expected_closure_state"]
    if result.closure_state in {"NO_SOLUTION", "DEGENERATE"}:
        assert result.selected_pose is None and result.candidates == []
    elif result.closure_state == "TWO_SOLUTIONS":
        assert result.selection_status == "BRANCH_AMBIGUOUS"
    else:
        assert result.provenance.branch_resolution == "TANGENT_UNIQUE"


@pytest.mark.parametrize("branch", ["POSITIVE", "NEGATIVE"])
def test_explicit_branch(branch):
    data = payload()
    data["configuration"].update(reference_branch=branch, branch_source_text="Synthetic branch test rule")
    result = solve_closure(build_closure_task_from_design(CandidateDesignInput.model_validate(data)))
    assert result.selected_pose.branch == branch
    assert result.selection_status == "SELECTED"
    assert result.provenance.evidence_status == "PARTIAL"


@pytest.mark.parametrize("branch", ["SAME_SIDE", "OPPOSITE_SIDE", "TANGENT"])
def test_no_assembly_signature_mapping(branch):
    data = payload()
    data["configuration"].update(reference_branch=branch, branch_source_text="test")
    with pytest.raises(ValueError):
        CandidateDesignInput.model_validate(data)


@pytest.mark.parametrize("change", ["coordinate_string", "coordinate_bool", "coordinate_inf", "zero_base", "angle_string", "tolerance_string", "missing_source", "missing_branch_source"])
def test_invalid_configuration(change):
    data = payload()
    config = data["configuration"]
    if change.startswith("coordinate_"):
        config["front_link_base"]["x_mm"]["value"] = {
            "coordinate_string": "8", "coordinate_bool": True, "coordinate_inf": float("inf")}[change]
    elif change == "zero_base":
        config["front_link_base"]["x_mm"]["value"] = 0
    elif change == "angle_string":
        config["rear_link_angle_deg"]["value"] = "0"
    elif change == "tolerance_string":
        config["tolerance"]["relative"] = "1e-12"
    elif change == "missing_source":
        config["front_link_base"]["x_mm"].pop("source_text")
    else:
        config["reference_branch"] = "POSITIVE"
    with pytest.raises(ValueError):
        CandidateDesignInput.model_validate(data)


def test_unready_engineering_cannot_adapt():
    data = payload()
    data["case"].update(domain="ENGINEERING_REFERENCE", case_id="ER-001", readiness="NOT_SOLVER_READY")
    data["bounds"]["domain"] = "ENGINEERING_REFERENCE"
    with pytest.raises(ValueError, match="NOT_SOLVER_READY"):
        build_closure_task_from_design(CandidateDesignInput.model_validate(data))


def test_adapter_revalidates_mutated_input():
    candidate = CandidateDesignInput.model_validate(payload())
    candidate.design.rear_link_length_mm.value = -1
    with pytest.raises(ValueError):
        build_closure_task_from_design(candidate)


def test_near_zero_positive_is_not_arbitrarily_clamped():
    data = payload()
    name = DESIGN_VARIABLE_ORDER[0]
    data["design"][name] = parameter(1e-15)
    data["bounds"][name]["lower"] = parameter(1e-16)
    task = build_closure_task_from_design(CandidateDesignInput.model_validate(data))
    assert task.rear_link_length_mm.value == 1e-15


def test_extreme_numerical_failure_is_not_no_solution():
    data = payload()
    for name in DESIGN_VARIABLE_ORDER:
        data["design"][name] = parameter(1e308)
        data["bounds"][name]["upper"] = parameter(1.1e308)
    with pytest.raises(ArithmeticError, match="arithmetic capacity"):
        build_closure_task_from_design(CandidateDesignInput.model_validate(data))
