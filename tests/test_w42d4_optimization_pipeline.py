"""Pipeline tests with real W41 math; explicitly labelled service fault injection."""

import pytest

from app.models.optimization_contract import ConstraintViolation, OptimizationCandidate, VariableValue
from app.models.optimization_pipeline import OptimizationEvaluationRecord, OptimizationPipelineResult
from app.services import linkage_evaluation as d4
from app.services import linkage_optimization_evaluation as w41
from app.services.optimization_pipeline import OptimizationEvaluationPipeline
from app.services.random_optimizer import run_random_search
from test_w42d2_optimization_contract import engineering_problem
from test_w42d3_random_optimizer import search_problem


def pending(experiment=None, candidate_id="candidate-1", lengths=(1, 3, 3)):
    experiment = experiment or search_problem()
    return OptimizationCandidate(
        candidate_id=candidate_id, problem=experiment,
        design_vector=tuple(VariableValue(variable_name=n, value=v, unit="mm",
                            source="Explicit pipeline synthetic design") for n, v in zip(experiment.variable_names, lengths)),
        evaluation_status="NOT_EVALUATED",
    )


def mixed_candidates():
    experiment = search_problem(((.9, 1.1), (.4, 3.1), (.4, 3.1)))
    return [pending(experiment, "good"), pending(experiment, "bad", (1, .5, .5))]


def test_single_pending_candidate_calls_actual_w41_evaluator(monkeypatch):
    calls = []
    original = d4.evaluate_design

    def observe(request):
        result = original(request)
        calls.append(result)
        return result

    monkeypatch.setattr(d4, "evaluate_design", observe)
    candidate = pending()
    record = OptimizationEvaluationPipeline().evaluate_candidate(candidate)
    assert len(calls) == 1
    assert record.evaluated_candidate.evaluation_record.result == calls[0]
    assert record.objective_values[0].value == pytest.approx(.306225774829855)
    assert record.evaluation_status == "SUCCESS" and record.feasible
    assert record.source == "W41_EVALUATOR" and record.request_mode == "DESIGN_VECTOR"
    assert record.failure_reason is None and record.violations == ()
    assert candidate.evaluation_status == "NOT_EVALUATED" and candidate.objective_values == ()


def test_multiple_candidates_counts_and_failure_cannot_be_best():
    candidates = mixed_candidates()
    pipeline = OptimizationEvaluationPipeline()
    result = pipeline.evaluate_candidates(candidates)
    assert result.total_candidates == result.evaluated_candidates == 2
    assert result.successful_candidates == result.failed_candidates == 1
    assert result.best_candidate_id == "good"
    assert result.best_objective == result.records[0].objective_values[0]
    failed = result.records[1]
    assert failed.evaluation_status == "FAILED" and not failed.feasible
    assert failed.objective_values == ()
    assert failed.violations[0].status == "NO_SOLUTION"
    assert failed.violations[0].violation_value is None
    assert failed.failure_reason.startswith("NO_SOLUTION:")
    assert pipeline.select_best_candidate(reversed(result.records)).candidate_id == "good"


def test_all_real_failures_have_no_best():
    candidates = mixed_candidates()
    problem = candidates[0].problem
    result = OptimizationEvaluationPipeline().evaluate_candidates([
        candidates[1], pending(problem, "bad-2", (1, .45, .5)),
    ])
    assert result.total_candidates == result.evaluated_candidates == result.failed_candidates == 2
    assert result.successful_candidates == 0
    assert result.best_candidate_id is None and result.best_objective is None
    assert all(r.failure_reason and not r.objective_values for r in result.records)


def test_true_degenerate_pose_retains_failure_reason():
    candidate = pending(search_problem(d=(1, 0)))
    record = OptimizationEvaluationPipeline().evaluate_candidate(candidate)
    assert record.evaluated_candidate.evaluation_record.result.closure_result.closure_state == "DEGENERATE"
    assert record.violations[0].status == "DEGENERATE"
    assert record.failure_reason.startswith("DEGENERATE:") and not record.feasible


def test_result_and_record_json_roundtrip():
    result = OptimizationEvaluationPipeline().evaluate_candidates(mixed_candidates())
    assert OptimizationPipelineResult.model_validate_json(result.model_dump_json()) == result
    for record in result.records:
        assert OptimizationEvaluationRecord.model_validate_json(record.model_dump_json()) == record


def test_input_list_and_candidate_snapshots_are_unchanged():
    candidates = mixed_candidates()
    identities = [id(c) for c in candidates]
    before = [c.model_dump() for c in candidates]
    result = OptimizationEvaluationPipeline().evaluate_candidates(candidates)
    assert [id(c) for c in candidates] == identities
    assert [c.model_dump() for c in candidates] == before
    result.records[0].evaluated_candidate.evaluation_record.request.candidate.design.rear_link_length_mm.value = 8
    assert [c.model_dump() for c in candidates] == before


def test_random_search_candidates_enter_pipeline_and_are_really_reevaluated(monkeypatch):
    run = run_random_search(search_problem(), random_seed=42, budget=10)
    before = run.model_dump_json()
    original = d4.evaluate_design
    calls = []

    def observe(request):
        actual = original(request)
        calls.append(actual)
        return actual

    monkeypatch.setattr(d4, "evaluate_design", observe)
    result = OptimizationEvaluationPipeline().evaluate_candidates(list(run.result.candidates))
    assert len(calls) == result.evaluated_candidates == 10
    assert result.successful_candidates == 10 and result.failed_candidates == 0
    assert result.best_candidate_id == run.result.best_candidate.candidate_id
    assert result.best_objective == run.result.objective_vector[0]
    assert run.model_dump_json() == before
    for record, original_candidate, actual in zip(result.records, run.result.candidates, calls):
        assert record.request_mode == "REPLAY"
        assert record.evaluated_candidate.evaluation_record.request == original_candidate.evaluation_record.request
        assert record.evaluated_candidate.evaluation_record.result == actual
        assert record.objective_values == original_candidate.objective_values


def test_missing_original_invalid_design_is_not_fabricated_or_reason_discarded():
    experiment = search_problem()
    previous = w41.evaluate_candidate_safely("invalid", {}, experiment.comparison_contract)
    candidate = OptimizationCandidate.from_w41(experiment, previous)
    record = OptimizationEvaluationPipeline().evaluate_candidate(candidate)
    assert record.request_mode == "MISSING_DESIGN" and record.evaluation_status == "FAILED"
    assert record.input_candidate.evaluation_record == previous
    assert record.evaluated_candidate.design_vector is None and record.objective_values == ()
    assert record.violations[0].status == "INVALID_INPUT" and record.failure_reason


def test_original_out_of_range_reason_survives_new_w41_validation():
    experiment = search_problem()
    vector = tuple(VariableValue(variable_name=n, value=2.0 if i == 0 else 3.0,
                                unit="mm", source="Explicit outside synthetic candidate")
                   for i, n in enumerate(experiment.variable_names))
    violation = ConstraintViolation(constraint_name=experiment.variable_names[0], status="OUT_OF_RANGE",
                                    violation_value=2.0 - experiment.bounds[0].upper,
                                    unit="mm", source="DECLARED_BOUNDS")
    candidate = OptimizationCandidate(candidate_id="outside", problem=experiment, design_vector=vector,
                                      evaluation_status="FAILED", constraint_violations=(violation,))
    record = OptimizationEvaluationPipeline().evaluate_candidate(candidate)
    assert record.source == "W41_EVALUATOR" and not record.feasible
    assert [v.status for v in record.violations] == ["OUT_OF_RANGE", "INVALID_INPUT"]
    assert record.input_candidate.constraint_violations == (violation,)
    assert record.evaluated_candidate.evaluation_record.error.code == "INVALID_INPUT"
    assert record.objective_values == ()


def test_injected_internal_error_is_recorded_and_later_candidate_runs(monkeypatch):
    original = d4.evaluate_design
    calls = 0

    def fail_once(request):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ValueError("private injected diagnostic")
        return original(request)

    monkeypatch.setattr(d4, "evaluate_design", fail_once)
    experiment = search_problem()
    result = OptimizationEvaluationPipeline().evaluate_candidates([pending(experiment, "first"), pending(experiment, "second")])
    assert result.failed_candidates == result.successful_candidates == 1
    assert result.best_candidate_id == "second"
    assert result.records[0].violations[0].status == "SERVICE_ERROR"
    assert "private injected diagnostic" not in result.model_dump_json()


def test_historical_transient_failure_kept_but_new_actual_success_is_used(monkeypatch):
    run = run_random_search(search_problem(), random_seed=42, budget=1)
    raw = run.result.candidates[0].evaluation_record.request
    with monkeypatch.context() as context:
        def fail(request):
            raise RuntimeError("explicit historical service fault")
        context.setattr(d4, "evaluate_design", fail)
        previous = w41.evaluate_candidate_safely("retry", raw, run.problem.comparison_contract)
    failed = OptimizationCandidate.from_w41(run.problem, previous)
    record = OptimizationEvaluationPipeline().evaluate_candidate(failed)
    assert record.input_candidate.evaluation_status == "FAILED"
    assert record.input_candidate.evaluation_record.error.code == "SERVICE_ERROR"
    assert record.evaluation_status == "SUCCESS" and record.feasible
    assert record.failure_reason is None and record.violations == ()


def test_real_zero_objective_can_be_selected():
    run = run_random_search(search_problem(angles=(0, 1e-16)), random_seed=42, budget=2)
    result = OptimizationEvaluationPipeline().evaluate_candidates(run.result.candidates)
    assert result.best_objective.value == 0.0
    assert result.best_candidate_id == run.result.candidates[0].candidate_id


def test_empty_batch_has_zero_counts_and_no_best():
    result = OptimizationEvaluationPipeline().evaluate_candidates([])
    assert (result.total_candidates, result.evaluated_candidates, result.successful_candidates, result.failed_candidates) == (0, 0, 0, 0)
    assert result.records == () and result.best_candidate_id is None and result.best_objective is None


@pytest.mark.parametrize("change", ["duplicate", "different_problem", "different_plan", "over_budget"])
def test_bad_batch_metadata_rejected_before_w41_call(monkeypatch, change):
    experiment = search_problem(budget=2)
    candidates = [pending(experiment, "one"), pending(experiment, "two")]
    if change == "duplicate": candidates[1] = candidates[0]
    elif change == "different_problem":
        different = experiment.model_copy(update={"problem_id": "other"})
        candidates[1] = pending(different, "two")
    elif change == "different_plan": candidates[1] = pending(search_problem(angles=(0, 45)), "two")
    else: candidates.append(pending(experiment, "three"))
    def forbidden(*args):
        raise AssertionError("invalid batch must not call evaluator")
    monkeypatch.setattr(w41, "evaluate_candidate_safely", forbidden)
    with pytest.raises(ValueError): OptimizationEvaluationPipeline().evaluate_candidates(candidates)


@pytest.mark.parametrize("change", ["total", "evaluated", "success", "failed", "best_id", "best_value"])
def test_aggregate_model_rejects_false_counts_or_best(change):
    data = OptimizationEvaluationPipeline().evaluate_candidates(mixed_candidates()).model_dump()
    if change == "total": data["total_candidates"] = 3
    elif change == "evaluated": data["evaluated_candidates"] = 1
    elif change == "success": data["successful_candidates"] = 2
    elif change == "failed": data["failed_candidates"] = 0
    elif change == "best_id": data["best_candidate_id"] = "bad"
    else: data["best_objective"]["value"] = 0.0
    with pytest.raises(ValueError): OptimizationPipelineResult.model_validate(data)


@pytest.mark.parametrize("change", ["status", "feasible", "source", "objective", "reason", "mode"])
def test_record_model_rejects_unbacked_claims(change):
    data = OptimizationEvaluationPipeline().evaluate_candidate(pending()).model_dump()
    if change == "status": data["evaluation_status"] = "FAILED"
    elif change == "feasible": data["feasible"] = False
    elif change == "source": data["source"] = "ENGINEERING_VERIFIED"
    elif change == "objective": data["objective_values"][0]["value"] = 0.0
    elif change == "reason": data["failure_reason"] = "invented"
    else: data["request_mode"] = "REPLAY"
    with pytest.raises(ValueError): OptimizationEvaluationRecord.model_validate(data)


def test_engineering_stays_failed_at_w41_gate_and_never_solves(monkeypatch):
    experiment = engineering_problem()
    raw = dict(case=dict(case_id="ER-001", domain="ENGINEERING_REFERENCE", readiness="NOT_SOLVER_READY",
                         source_text="No engineering geometry"), objective=None)
    candidate = OptimizationCandidate.from_w41(experiment, w41.evaluate_candidate_safely("engineering", raw))
    def forbidden(*args):
        raise AssertionError("engineering must not solve")
    monkeypatch.setattr(d4, "solve_closure", forbidden)
    monkeypatch.setattr(d4, "sweep_rear_link_angles", forbidden)
    result = OptimizationEvaluationPipeline().evaluate_candidates([candidate])
    record = result.records[0]
    assert record.evaluation_status == "FAILED" and record.failure_reason.startswith("NOT_SOLVER_READY:")
    assert record.evaluated_candidate.evaluation_record.result.execution_status == "NOT_RUN"
    assert not record.feasible and result.best_candidate_id is None
    assert not record.evaluated_candidate.problem.engineering_verified


@pytest.mark.parametrize("signal", [KeyboardInterrupt(), SystemExit(2), MemoryError()])
def test_injected_termination_signals_propagate(monkeypatch, signal):
    def fail(request):
        raise signal
    monkeypatch.setattr(d4, "evaluate_design", fail)
    with pytest.raises(type(signal)) as caught:
        OptimizationEvaluationPipeline().evaluate_candidate(pending())
    assert caught.value is signal
