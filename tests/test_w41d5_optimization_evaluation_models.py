import pytest

from app.models.linkage_optimization_evaluation import (
    CandidateEvaluationRecord, EvaluationError, SamplingCoverage, TimeoutCapability,
)
from test_w41d4_evaluation_models import request_payload
from test_w41d5_optimization_evaluation_service import record


@pytest.mark.parametrize("change", ["ranking", "computed", "outcome", "comparison", "coverage",
                                    "request", "both", "neither", "violation", "source", "timeout"])
def test_record_rejects_fabricated_claims(change):
    data = record(request_payload([0, 5], objective=True)).model_dump(mode="python")
    if change == "ranking": data["ranking_eligible"] = False
    elif change == "computed": data["objective_computed"] = False
    elif change == "outcome": data["outcome"] = "NO_SOLUTION"
    elif change == "comparison": data["comparison_status"] = "INCOMPATIBLE"
    elif change == "coverage": data["coverage"]["regular_selected_count"] = 1
    elif change == "request": data["request"] = None
    elif change == "both":
        data["error"] = dict(code="SERVICE_ERROR", stage="EVALUATOR_EXECUTION",
                             exception_type="ValueError", diagnostic="INTERNAL_EVALUATION_EXCEPTION")
    elif change == "neither": data["result"] = None
    elif change == "violation": data["constraint_violation_value"] = 0
    elif change == "source": data["source_assessment"] = "ENGINEERING_VERIFIED"
    else: data["outcome"] = "TIMEOUT"
    with pytest.raises(ValueError): CandidateEvaluationRecord.model_validate(data)


@pytest.mark.parametrize("field,value", [("status", "IMPLEMENTED"), ("can_interrupt", True)])
def test_timeout_capability_cannot_claim_execution(field, value):
    with pytest.raises(ValueError): TimeoutCapability.model_validate({field: value})


def test_timeout_cannot_be_error_record():
    with pytest.raises(ValueError):
        EvaluationError(code="TIMEOUT", stage="EVALUATOR_EXECUTION", exception_type="TimeoutError",
                        diagnostic="INTERNAL_EVALUATION_EXCEPTION")


@pytest.mark.parametrize("data", [
    dict(requested_count=2, recorded_count=1, regular_selected_count=2, recorded_ratio=.5),
    dict(requested_count=2, recorded_count=3, regular_selected_count=1, recorded_ratio=1.0),
    dict(requested_count=2, recorded_count=1, regular_selected_count=1, recorded_ratio=1.0),
    dict(requested_count=2, recorded_count=None, regular_selected_count=None, recorded_ratio=0.0),
    dict(requested_count=2, recorded_count=1, regular_selected_count=None, recorded_ratio=.5),
    dict(requested_count=True),
])
def test_coverage_rejects_inconsistent_or_coerced_counts(data):
    with pytest.raises(ValueError): SamplingCoverage.model_validate(data)


def test_error_stage_prevents_internal_value_error_becoming_invalid_input():
    with pytest.raises(ValueError):
        EvaluationError(code="INVALID_INPUT", stage="EVALUATOR_EXECUTION", exception_type="ValueError",
                        diagnostic="INPUT_VALIDATION_FAILED")


@pytest.mark.parametrize("change", ["zero_objective", "ranking", "fake_request", "coverage"])
def test_input_failure_cannot_acquire_score_or_snapshot(change):
    data = record({"bad": "input"}, comparison=False).model_dump(mode="python")
    if change == "zero_objective": data["objective_value"] = 0.0
    elif change == "ranking": data["ranking_eligible"] = True
    elif change == "fake_request": data["request"] = request_payload([0, 5], objective=True)
    else: data["coverage"] = dict(requested_count=2, recorded_count=0, regular_selected_count=0, recorded_ratio=0.0)
    with pytest.raises(ValueError): CandidateEvaluationRecord.model_validate(data)
