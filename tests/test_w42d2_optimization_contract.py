"""Experiment contracts using actual synthetic W41 records; no GA/PSO engine."""

import json

import pytest
from pydantic import ValidationError

from app.models.linkage_evaluation import DesignEvaluationRequest
from app.models.linkage_optimization import DESIGN_VARIABLE_ORDER
from app.models.linkage_optimization_evaluation import ComparisonContract
from app.models.optimization_contract import (
    ConstraintViolation, ObjectiveValue, OptimizationCandidate, OptimizationProblem,
    OptimizationResult, OptimizationRun, VariableBounds, VariableValue,
)
from app.services.linkage_optimization_evaluation import evaluate_candidates
from test_w41d4_evaluation_models import request_payload


def request(angles=(0, 90), lengths=(1, 3, 3), d=(3, 0)):
    return DesignEvaluationRequest.model_validate(request_payload(list(angles), lengths=lengths, d=d, objective=True))


def problem(reference=None, budget=10):
    reference = reference or request()
    return OptimizationProblem(
        problem_id="synthetic-1", case_id=reference.case.case_id,
        domain="SYNTHETIC_MATH", readiness="READY", variable_names=DESIGN_VARIABLE_ORDER,
        bounds=tuple(VariableBounds(variable_name=n,
                     lower=getattr(reference.candidate.bounds, n).lower.value,
                     upper=getattr(reference.candidate.bounds, n).upper.value,
                     unit="mm", source="Explicit synthetic W41 bounds") for n in DESIGN_VARIABLE_ORDER),
        objective_names=("SAMPLED_C_X_RANGE",), objective_units=("mm",),
        constraints=("FULL_REGULAR_SAMPLES",), evaluation_budget=budget,
        comparison_contract_json=ComparisonContract.from_request(reference).model_dump_json(),
    )


def candidate(experiment=None, actual=None, candidate_id="candidate-1"):
    experiment = experiment or problem()
    actual = actual or request()
    record = evaluate_candidates([(candidate_id, actual)], experiment.comparison_contract)[0]
    return OptimizationCandidate.from_w41(experiment, record)


def result(experiment=None, candidates=None):
    experiment = experiment or problem()
    candidates = candidates if candidates is not None else (candidate(experiment),)
    eligible = [c for c in candidates if c.ranking_eligible]
    best = min(eligible, key=lambda c: c.objective_values[0].value) if eligible else None
    return OptimizationResult(
        problem=experiment, candidates=candidates, best_candidate=best,
        objective_vector=best.objective_values if best else (), feasible=best is not None,
        total_candidates=len(candidates), failed_candidates=sum(not c.ranking_eligible for c in candidates),
    )


def test_all_five_contract_models_create_with_actual_evaluation():
    experiment = problem()
    actual = candidate(experiment)
    summary = result(experiment, (actual,))
    run = OptimizationRun(run_id="run-1", problem=experiment, algorithm_name="MANUAL",
                          random_seed=0, budget=10, candidate_count=1, status="COMPLETED", result=summary)
    assert summary.feasible and summary.best_candidate == actual and run.result == summary
    assert actual.evaluation_record.result.objective_value == pytest.approx(.306225774829855)
    assert actual.objective_values[0].unit == "mm"


@pytest.mark.parametrize("change", ["missing_unit", "wrong_unit", "missing_source", "blank_source",
                                    "infinite", "nan", "reversed", "numeric_string", "boolean"])
def test_bound_unit_source_and_numeric_fields_are_strict(change):
    data = dict(variable_name=DESIGN_VARIABLE_ORDER[0], lower=1.0, upper=20.0, unit="mm", source="Synthetic")
    if change == "missing_unit": del data["unit"]
    elif change == "wrong_unit": data["unit"] = "m"
    elif change == "missing_source": del data["source"]
    elif change == "blank_source": data["source"] = " "
    elif change == "infinite": data["upper"] = float("inf")
    elif change == "nan": data["upper"] = float("nan")
    elif change == "reversed": data["upper"] = .5
    elif change == "numeric_string": data["lower"] = "1"
    else: data["lower"] = True
    with pytest.raises(ValueError): VariableBounds.model_validate(data)


@pytest.mark.parametrize("change", ["extra_variable", "variable_order", "bounds_order", "missing_bounds",
                                    "different_bounds", "missing_units", "extra_objective", "extra_constraint",
                                    "missing_comparison", "budget_bool", "budget_zero", "verified", "verified_zero", "version_bool"])
def test_problem_rejects_unsupported_or_incomplete_conditions(change):
    data = problem().model_dump()
    if change == "extra_variable": data["variable_names"] += ("support_height_mm",)
    elif change == "variable_order": data["variable_names"] = tuple(reversed(data["variable_names"]))
    elif change == "bounds_order": data["bounds"] = tuple(reversed(data["bounds"]))
    elif change == "missing_bounds": data["bounds"] = ()
    elif change == "different_bounds": data["bounds"][0]["upper"] = 21.0
    elif change == "missing_units": data["objective_units"] = ()
    elif change == "extra_objective": data["objective_names"] += ("T_DISPLACEMENT",)
    elif change == "extra_constraint": data["constraints"] += ("INTERFERENCE",)
    elif change == "missing_comparison": data["comparison_contract_json"] = None
    elif change == "budget_bool": data["evaluation_budget"] = True
    elif change == "budget_zero": data["evaluation_budget"] = 0
    elif change == "verified": data["engineering_verified"] = True
    elif change == "verified_zero": data["engineering_verified"] = 0
    else: data["version"] = True
    with pytest.raises(ValueError): OptimizationProblem.model_validate(data)


@pytest.mark.parametrize("state,lengths,d", [
    ("NO_SOLUTION", (1, .5, .5), (3, 0)),
    ("DEGENERATE", (1, 3, 3), (1, 0)),
])
def test_real_mathematical_failure_keeps_undefined_violation_and_cannot_be_best(state, lengths, d):
    reference = request(d=d)
    experiment = problem(reference)
    failed = candidate(experiment, request(lengths=lengths, d=d))
    assert failed.evaluation_status == "FAILED" and failed.objective_values == ()
    assert failed.constraint_violations[0].status == state
    assert failed.constraint_violations[0].violation_value is None
    assert failed.constraint_violations[0].unit is None
    assert not failed.ranking_eligible
    empty_best = result(experiment, (failed,))
    assert empty_best.best_candidate is None and not empty_best.feasible
    data = empty_best.model_dump()
    data["best_candidate"] = failed.model_dump()
    data["feasible"] = True
    with pytest.raises(ValueError): OptimizationResult.model_validate(data)


def test_actual_invalid_input_record_has_no_fabricated_design_or_objective():
    experiment = problem()
    record = evaluate_candidates([("invalid", {})], experiment.comparison_contract)[0]
    actual = OptimizationCandidate.from_w41(experiment, record)
    assert actual.design_vector is None and actual.objective_values == ()
    assert actual.constraint_violations[0].status == "INVALID_INPUT"
    assert actual.constraint_violations[0].violation_value is None
    assert result(experiment, (actual,)).failed_candidates == 1


def test_out_of_range_has_only_real_bound_exceedance_not_a_score():
    experiment = problem()
    vector = tuple(VariableValue(variable_name=n, value=21.0 if i == 0 else 3.0,
                                unit="mm", source="Explicit synthetic candidate")
                   for i, n in enumerate(DESIGN_VARIABLE_ORDER))
    violation = ConstraintViolation(constraint_name=DESIGN_VARIABLE_ORDER[0], status="OUT_OF_RANGE",
                                    violation_value=1.0, unit="mm", source="DECLARED_BOUNDS")
    actual = OptimizationCandidate(candidate_id="outside", problem=experiment, design_vector=vector,
                                    evaluation_status="FAILED", constraint_violations=(violation,))
    assert not actual.ranking_eligible and actual.objective_values == ()
    assert not result(experiment, (actual,)).feasible
    data = actual.model_dump()
    data["constraint_violations"][0]["violation_value"] = 2.0
    with pytest.raises(ValueError): OptimizationCandidate.model_validate(data)


@pytest.mark.parametrize("state", ["INVALID_INPUT", "NO_SOLUTION", "DEGENERATE"])
def test_failure_magnitude_cannot_be_invented(state):
    with pytest.raises(ValueError):
        ConstraintViolation(constraint_name="FULL_REGULAR_SAMPLES", status=state,
                            violation_value=0.0, unit="mm", source="W41_D5_RECORD")


def test_unevaluated_candidate_cannot_claim_objectives_or_be_best():
    experiment = problem()
    evaluated = candidate(experiment)
    pending = OptimizationCandidate(candidate_id="pending", problem=experiment,
                                     design_vector=evaluated.design_vector, evaluation_status="NOT_EVALUATED")
    assert not pending.ranking_eligible
    data = pending.model_dump()
    data["objective_values"] = evaluated.objective_values
    with pytest.raises(ValueError): OptimizationCandidate.model_validate(data)
    with pytest.raises(ValueError): result(experiment, (pending,))


@pytest.mark.parametrize("change", ["missing_evidence", "fake_objective", "fake_design", "fake_id", "fake_status"])
def test_candidate_requires_matching_actual_w41_evidence(change):
    data = candidate().model_dump()
    if change == "missing_evidence": data["evaluation_record_json"] = None
    elif change == "fake_objective": data["objective_values"][0]["value"] = 0.0
    elif change == "fake_design": data["design_vector"][0]["value"] = 2.0
    elif change == "fake_id": data["candidate_id"] = "different"
    else: data["evaluation_status"] = "FAILED"
    with pytest.raises(ValueError): OptimizationCandidate.model_validate(data)


def test_failed_candidate_cannot_acquire_zero_objective():
    experiment = problem()
    failed = candidate(experiment, request(lengths=(1, .5, .5)))
    data = failed.model_dump()
    data["objective_values"] = (dict(objective_name="SAMPLED_C_X_RANGE", value=0.0, unit="mm"),)
    with pytest.raises(ValueError): OptimizationCandidate.model_validate(data)


def test_real_zero_objective_is_allowed_when_evaluated():
    reference = request((0, 1e-16))
    experiment = problem(reference)
    actual = candidate(experiment, reference)
    assert actual.objective_values[0].value == 0.0 and actual.ranking_eligible
    assert result(experiment, (actual,)).feasible


def test_different_condition_cannot_enter_same_problem():
    experiment = problem()
    actual = request((0, 45))
    record = evaluate_candidates([("different", actual)], experiment.comparison_contract)[0]
    assert not record.ranking_eligible
    with pytest.raises(ValueError): OptimizationCandidate.from_w41(experiment, record)


def test_result_best_is_minimum_of_recorded_eligible_candidates():
    experiment = problem()
    values = (candidate(experiment, request(), "one"), candidate(experiment, request(lengths=(1, 2, 3)), "two"))
    actual = result(experiment, values)
    assert actual.best_candidate.objective_values[0].value == min(c.objective_values[0].value for c in values)
    worse = max(values, key=lambda c: c.objective_values[0].value)
    assert worse.objective_values[0].value > actual.objective_vector[0].value
    data = actual.model_dump()
    data["best_candidate"] = worse.model_dump()
    data["objective_vector"] = tuple(o.model_dump() for o in worse.objective_values)
    with pytest.raises(ValueError): OptimizationResult.model_validate(data)


@pytest.mark.parametrize("change", ["total", "failed", "duplicate", "budget"])
def test_result_counts_are_not_free_claims(change):
    data = result().model_dump()
    if change == "total": data["total_candidates"] = 2
    elif change == "failed": data["failed_candidates"] = 1
    elif change == "duplicate":
        data["candidates"] += data["candidates"]
        data["total_candidates"] = 2
    else:
        data["problem"]["evaluation_budget"] = 0
    with pytest.raises(ValueError): OptimizationResult.model_validate(data)


def test_roundtrip_for_all_five_models():
    experiment = problem()
    actual = candidate(experiment)
    summary = result(experiment, (actual,))
    run = OptimizationRun(run_id="roundtrip", problem=experiment, algorithm_name="MANUAL",
                          random_seed=None, budget=10, candidate_count=1, status="COMPLETED", result=summary)
    failure = ConstraintViolation(constraint_name="INPUT_VALIDATION", status="INVALID_INPUT",
                                  violation_value=None, unit=None, source="W41_D5_RECORD")
    for model in (experiment, actual, failure, summary, run):
        assert type(model).model_validate_json(model.model_dump_json()) == model


def test_nested_inputs_and_exposed_w41_snapshots_are_immutable_or_independent():
    reference = request()
    experiment = problem(reference)
    record = evaluate_candidates([("immutable", reference)], experiment.comparison_contract)[0]
    actual = OptimizationCandidate.from_w41(experiment, record)
    before = actual.model_dump_json()
    reference.candidate.design.rear_link_length_mm.value = 7
    record.request.candidate.design.rear_link_length_mm.value = 8
    actual.evaluation_record.request.candidate.design.rear_link_length_mm.value = 9
    experiment.comparison_contract.plan.source_text = "changed external accessor"
    assert actual.model_dump_json() == before
    with pytest.raises(ValidationError): actual.candidate_id = "changed"
    with pytest.raises(ValidationError): actual.design_vector[0].value = 10.0
    with pytest.raises(ValidationError): actual.problem.bounds[0].upper = 100.0
    assert isinstance(actual.design_vector, tuple) and isinstance(actual.problem.bounds, tuple)


def engineering_problem():
    return OptimizationProblem(problem_id="engineering-pending", case_id="ER-001",
        domain="ENGINEERING_REFERENCE", readiness="NOT_SOLVER_READY", variable_names=DESIGN_VARIABLE_ORDER,
        bounds=(), objective_names=(), objective_units=(), constraints=(), evaluation_budget=10,
        comparison_contract_json=None)


def test_engineering_reference_remains_descriptive_and_not_run():
    experiment = engineering_problem()
    assert not experiment.engineering_verified and not experiment.bounds
    raw = dict(case=dict(domain="ENGINEERING_REFERENCE", case_id="ER-001", readiness="NOT_SOLVER_READY",
                         source_text="Missing engineering data"), objective=None)
    record = evaluate_candidates([("er", raw)])[0]
    actual = OptimizationCandidate.from_w41(experiment, record)
    assert actual.evaluation_status == "NOT_SOLVER_READY" and actual.design_vector is None
    assert not result(experiment, (actual,)).feasible
    run = OptimizationRun(run_id="er", problem=experiment, algorithm_name="UNSPECIFIED",
                          random_seed=None, budget=10, candidate_count=0, status="NOT_RUN")
    assert run.result is None
    data = run.model_dump()
    data["status"] = "RUNNING"
    with pytest.raises(ValueError): OptimizationRun.model_validate(data)


@pytest.mark.parametrize("change", ["ready", "relabel", "verified"])
def test_engineering_cannot_be_promoted(change):
    data = engineering_problem().model_dump()
    if change == "ready": data["readiness"] = "READY"
    elif change == "relabel": data["domain"] = "SYNTHETIC_MATH"
    else: data["engineering_verified"] = True
    with pytest.raises(ValueError): OptimizationProblem.model_validate(data)


@pytest.mark.parametrize("algorithm", ["GA", "PSO"])
def test_algorithm_names_are_only_unstarted_metadata(algorithm):
    actual = OptimizationRun(run_id="metadata", problem=problem(), algorithm_name=algorithm,
                             random_seed=42, budget=10, candidate_count=0, status="NOT_STARTED")
    assert actual.algorithm_name == algorithm and actual.result is None


@pytest.mark.parametrize("change", ["budget", "count", "completed_without_result", "seed_bool", "negative_seed", "unstarted_count"])
def test_run_invariants(change):
    data = dict(run_id="run", problem=problem(), algorithm_name="MANUAL", random_seed=0,
                budget=10, candidate_count=0, status="NOT_STARTED")
    if change == "budget": data["budget"] = 11
    elif change == "count": data["candidate_count"] = 11
    elif change == "completed_without_result": data["status"] = "COMPLETED"
    elif change == "seed_bool": data["random_seed"] = True
    elif change == "negative_seed": data["random_seed"] = -1
    else: data["candidate_count"] = 1
    with pytest.raises(ValueError): OptimizationRun.model_validate(data)


def test_updated_copy_bypass_is_revalidated_when_saved_as_result():
    experiment = problem()
    original = candidate(experiment)
    corrupted = original.model_copy(update={"objective_values": (ObjectiveValue(
        objective_name="SAMPLED_C_X_RANGE", value=0.0, unit="mm"),)})
    with pytest.raises(ValueError): result(experiment, (corrupted,))


def test_canonical_snapshot_encoding_preserves_equivalent_json():
    data = problem().model_dump()
    data["comparison_contract_json"] = json.dumps(json.loads(data["comparison_contract_json"]), indent=2)
    assert OptimizationProblem.model_validate(data) == problem()


def test_caller_lists_are_copied_without_mutating_the_input():
    data = json.loads(problem().model_dump_json())
    before = json.dumps(data, sort_keys=True)
    actual = OptimizationProblem.model_validate(data)
    assert json.dumps(data, sort_keys=True) == before
    assert isinstance(data["bounds"], list) and isinstance(actual.bounds, tuple)
    data["bounds"][0]["upper"] = 99.0
    data["variable_names"].append("support_height_mm")
    assert actual.bounds[0].upper == 20.0 and actual.variable_names == DESIGN_VARIABLE_ORDER
