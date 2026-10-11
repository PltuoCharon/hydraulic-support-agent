import pytest

from app.models.linkage_evaluation import DesignEvaluationRequest, DesignEvaluationResult
from app.models.linkage_optimization import DESIGN_VARIABLE_ORDER
from app.services.linkage_evaluation import evaluate_design


def parameter(value, unit="mm"):
    return dict(value=value, unit=unit, origin="USER_INPUT", evidence_status="PARTIAL",
                source_text="Explicit synthetic mathematical fixture")


def request_payload(angles=None, branch="POSITIVE", lengths=(5, 5, 5), d=(8, 0), objective=False):
    case = dict(domain="SYNTHETIC_MATH", case_id="SM-001", readiness="READY", source_text="Synthetic fixture")
    candidate = dict(case=case.copy(), design={n: parameter(v) for n, v in zip(DESIGN_VARIABLE_ORDER, lengths)},
                     bounds=dict(domain="SYNTHETIC_MATH", **{n: dict(lower=parameter(1e-16), upper=parameter(20)) for n in DESIGN_VARIABLE_ORDER}),
                     configuration=dict(front_link_base=dict(x_mm=parameter(d[0]), y_mm=parameter(d[1])),
                                        rear_link_angle_deg=parameter(angles[0] if angles else 0, "degree"),
                                        reference_branch=branch, branch_source_text="Synthetic branch rule",
                                        tolerance=dict(absolute_mm=1e-9, relative=1e-12)))
    plan = dict(mode="SINGLE_POSE_SELECTED", source_text="Synthetic single pose")
    if angles is not None:
        plan = dict(mode="FULL_SAMPLED_REGULAR_MOTION", direction="INCREASING",
                    angle_samples_deg=[parameter(v, "degree") for v in angles], source_text="Fixed synthetic angle samples")
    return dict(case=case, candidate=candidate, plan=plan,
                objective=dict(name="SAMPLED_C_X_RANGE") if objective else None)


@pytest.mark.parametrize("change", ["missing_candidate", "missing_plan", "missing_objective", "different_case", "cross_domain", "engineering_ready", "relabel", "unsupported_objective", "single_objective", "wrong_direction", "one_angle", "duplicate_angle", "nonmonotonic", "missing_branch", "first_mismatch", "string_angle", "bool_angle", "inf_angle", "unit_angle", "blank_source"])
def test_invalid_requests(change):
    data = request_payload([0, 5])
    if change == "missing_candidate": data["candidate"] = None
    elif change == "missing_plan": data["plan"] = None
    elif change == "missing_objective": del data["objective"]
    elif change == "different_case": data["case"] = {**data["case"], "case_id": "SM-002"}
    elif change == "cross_domain": data["candidate"]["bounds"]["domain"] = "ENGINEERING_REFERENCE"
    elif change == "engineering_ready": data["case"] = {**data["case"], "domain": "ENGINEERING_REFERENCE", "case_id": "ER-001"}
    elif change == "relabel": data["case"]["case_id"] = "ER-001"
    elif change == "unsupported_objective": data["objective"] = dict(name="T_DISPLACEMENT")
    elif change == "single_objective": data["plan"] = dict(mode="SINGLE_POSE_SELECTED", source_text="test"); data["objective"] = dict(name="SAMPLED_C_X_RANGE")
    elif change == "wrong_direction": data["plan"]["direction"] = "DECREASING"
    elif change == "one_angle": data["plan"]["angle_samples_deg"].pop()
    elif change == "duplicate_angle": data["plan"]["angle_samples_deg"][1]["value"] = 0
    elif change == "nonmonotonic": data["plan"]["angle_samples_deg"].append(parameter(2, "degree"))
    elif change == "missing_branch": data["candidate"]["configuration"]["reference_branch"] = None
    elif change == "first_mismatch": data["candidate"]["configuration"]["rear_link_angle_deg"]["value"] = 1
    elif change == "blank_source": data["plan"]["source_text"] = " "
    else:
        angle = data["plan"]["angle_samples_deg"][1]
        if change == "unit_angle": angle["unit"] = "radian"
        else: angle["value"] = {"string_angle": "5", "bool_angle": True, "inf_angle": float("inf")}[change]
    with pytest.raises(ValueError): DesignEvaluationRequest.model_validate(data)


@pytest.mark.parametrize("direction,angles", [("INCREASING", [0, 5]), ("DECREASING", [5, 0])])
def test_valid_plans(direction, angles):
    data = request_payload(angles)
    data["plan"]["direction"] = direction
    DesignEvaluationRequest.model_validate(data)


@pytest.mark.parametrize("change", ["readiness", "execution", "feasibility", "constraint", "objective_status", "objective_value", "motion_missing", "metric_wrong", "request_count", "angles_wrong"])
def test_result_invariants(change):
    result = evaluate_design(DesignEvaluationRequest.model_validate(request_payload([0, 5], objective=True)))
    data = result.model_dump(mode="python")
    if change == "readiness": data["case_readiness"] = "NOT_SOLVER_READY"
    elif change == "execution": data["execution_status"] = "NOT_RUN"
    elif change == "feasibility": data["feasibility_status"] = "INFEASIBLE"
    elif change == "constraint": data["constraints"][0]["status"] = "FAIL"
    elif change == "objective_status": data["objective_status"] = "NOT_EVALUABLE"
    elif change == "objective_value": data["objective_value"] = 123.0
    elif change == "motion_missing": data["motion_result"] = None
    elif change == "metric_wrong": data["metrics"][0]["value"] = 123.0
    elif change == "request_count": data["motion_result"]["requested_angle_count"] = 3
    else: data["request"]["plan"]["angle_samples_deg"][1]["value"] = 6
    with pytest.raises(ValueError): DesignEvaluationResult.model_validate(data)


@pytest.mark.parametrize("change", ["objective", "closure", "feasibility", "constraint", "metric"])
def test_unready_result_cannot_claim_computation(change):
    request = DesignEvaluationRequest(case=dict(domain="ENGINEERING_REFERENCE", case_id="ER-001",
                                                readiness="NOT_SOLVER_READY", source_text="Evidence gap"), objective=None)
    data = evaluate_design(request).model_dump()
    if change == "objective": data["objective_value"] = 0.0
    elif change == "closure": data["closure_result"] = evaluate_design(DesignEvaluationRequest.model_validate(request_payload())).closure_result.model_dump()
    elif change == "feasibility": data["feasibility_status"] = "FEASIBLE"
    elif change == "constraint": data["constraints"][0]["status"] = "PASS"
    else: data["metrics"] = [dict(name="SAMPLED_C_X_RANGE", unit="mm", value=0.0)]
    with pytest.raises(ValueError): DesignEvaluationResult.model_validate(data)


def test_request_duplicate_json_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        DesignEvaluationRequest.model_validate_json('{"objective":null,"objective":null}')


@pytest.mark.parametrize("field,value", [("direction", "MAXIMIZE"), ("unit", "m")])
def test_objective_contract(field, value):
    data = request_payload([0, 5], objective=True)
    data["objective"][field] = value
    with pytest.raises(ValueError): DesignEvaluationRequest.model_validate(data)


def test_result_rejects_wrong_failure_index():
    data = evaluate_design(DesignEvaluationRequest.model_validate(request_payload([0, 120], objective=True))).model_dump()
    data["constraints"][0]["sample_index"] = 0
    with pytest.raises(ValueError, match="index"): DesignEvaluationResult.model_validate(data)
