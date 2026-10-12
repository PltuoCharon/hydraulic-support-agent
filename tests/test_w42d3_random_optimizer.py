"""Actual W41 evaluations; any altered sampler/service is explicitly labelled."""

import random

import pytest

from app.models.linkage_evaluation import DesignEvaluationRequest
from app.models.optimization_contract import OptimizationResult, OptimizationRun
from app.services import linkage_evaluation as d4
from app.services import random_optimizer as service
from test_w41d4_evaluation_models import parameter, request_payload
from test_w42d2_optimization_contract import engineering_problem, problem


def search_problem(intervals=((.9, 1.1), (2.9, 3.1), (2.9, 3.1)), d=(3, 0), budget=10, angles=(0, 90)):
    lengths = tuple((lower + upper) / 2 for lower, upper in intervals)
    raw = request_payload(list(angles), lengths=lengths, d=d, objective=True)
    for name, interval in zip(raw["candidate"]["design"], intervals):
        raw["candidate"]["bounds"][name] = dict(lower=parameter(interval[0]), upper=parameter(interval[1]))
    return problem(DesignEvaluationRequest.model_validate(raw), budget=budget)


def test_seed42_budget10_produces_identical_full_runs():
    experiment = search_problem()
    first = service.run_random_search(experiment, random_seed=42, budget=10)
    second = service.run_random_search(experiment, random_seed=42, budget=10)
    assert first == second and first.model_dump_json() == second.model_dump_json()
    assert first.algorithm_name == "RANDOM_SEARCH_V1" and first.random_seed == 42
    assert first.status == "COMPLETED" and first.result.feasible


@pytest.mark.parametrize("budget", [1, 3, 10])
def test_exact_budget_all_candidates_have_unique_ids_and_declared_bounds(budget):
    experiment = search_problem()
    actual = service.run_random_search(experiment, random_seed=42, budget=budget)
    assert actual.candidate_count == actual.budget == actual.result.total_candidates == budget
    assert len(actual.result.candidates) == budget
    assert len({c.candidate_id for c in actual.result.candidates}) == budget
    for candidate in actual.result.candidates:
        for value, bound in zip(candidate.design_vector, experiment.bounds):
            assert bound.lower <= value.value <= bound.upper and value.unit == "mm"


def test_default_budget_uses_problem_budget_and_different_seeds_change_designs():
    experiment = search_problem(budget=3)
    first = service.run_random_search(experiment, random_seed=42)
    second = service.run_random_search(experiment, random_seed=43)
    assert first.candidate_count == 3
    assert first.result.candidates[0].design_vector != second.result.candidates[0].design_vector


def test_real_objectives_are_bound_to_actual_d4_calls(monkeypatch):
    calls = []
    original = d4.evaluate_design

    def observe(request):
        actual = original(request)
        calls.append(actual)
        return actual

    monkeypatch.setattr(d4, "evaluate_design", observe)
    run = service.run_random_search(search_problem(), random_seed=42, budget=10)
    assert len(calls) == 10
    for candidate, actual in zip(run.result.candidates, calls):
        assert candidate.evaluation_record.result == actual
        assert candidate.objective_values[0].value == actual.objective_value
        assert candidate.evaluation_record.request == actual.request
    expected_minimum = min(actual.objective_value for actual in calls)
    assert run.result.objective_vector[0].value == expected_minimum
    assert run.result.best_candidate.objective_values[0].value == expected_minimum


def test_true_no_solution_candidates_are_saved_without_scores_or_best():
    experiment = search_problem(((.9, 1.1), (.4, .5), (.4, .5)))
    run = service.run_random_search(experiment, random_seed=42, budget=10)
    assert run.candidate_count == run.result.failed_candidates == 10
    assert run.status == "COMPLETED" and not run.result.feasible
    assert run.result.best_candidate is None and run.result.objective_vector == ()
    for candidate in run.result.candidates:
        assert candidate.evaluation_status == "FAILED" and not candidate.ranking_eligible
        assert candidate.objective_values == ()
        assert candidate.constraint_violations[0].status == "NO_SOLUTION"
        assert candidate.constraint_violations[0].violation_value is None
        assert candidate.evaluation_record.result.closure_result.closure_state == "NO_SOLUTION"


def test_real_arithmetic_capacity_failures_are_preserved_not_scored():
    # Actual D3 capacity guard, not an injected numerical exception.
    experiment = search_problem(((1e155, 1.1e155),) * 3)
    run = service.run_random_search(experiment, random_seed=42, budget=3)
    assert run.result.failed_candidates == 3 and run.result.best_candidate is None
    for candidate in run.result.candidates:
        assert candidate.constraint_violations[0].status == "NUMERICAL_ERROR"
        assert candidate.evaluation_record.error.exception_type == "ArithmeticError"
        assert candidate.objective_values == ()


def test_real_finite_zero_objective_is_not_discarded():
    # Same rounded Cx at two distinct tiny angles; discrete synthetic metric only.
    experiment = search_problem(angles=(0, 1e-16))
    run = service.run_random_search(experiment, random_seed=42, budget=3)
    assert run.result.best_candidate is not None and run.result.feasible
    assert run.result.objective_vector[0].value == 0.0
    assert run.result.best_candidate.evaluation_record.result.objective_value == 0.0


def test_true_degenerate_geometry_with_fixed_sampler_is_evaluated_by_w41(monkeypatch):
    # Force an exact B=D pose, not a fabricated solver result or objective.
    experiment = search_problem(d=(1, 0))
    fixed = dict(zip(experiment.variable_names, (1.0, 3.0, 3.0)))
    monkeypatch.setattr(service, "_sample_design", lambda problem, rng: fixed.copy())
    run = service.run_random_search(experiment, random_seed=42, budget=3)
    assert run.result.failed_candidates == 3 and run.result.best_candidate is None
    for candidate in run.result.candidates:
        assert candidate.constraint_violations[0].status == "DEGENERATE"
        assert candidate.evaluation_record.result.closure_result.closure_state == "DEGENERATE"
        assert candidate.objective_values == ()


@pytest.mark.parametrize("bad_value,expected", [("bad-numeric-input", "INVALID_INPUT"), (2.0, "OUT_OF_RANGE")])
def test_injected_invalid_or_outside_sample_is_recorded_then_batch_continues(monkeypatch, bad_value, expected):
    experiment = search_problem()
    original = service._sample_design
    calls = 0

    def altered(problem, rng):
        nonlocal calls
        calls += 1
        values = original(problem, rng)
        if calls == 1:
            values[problem.variable_names[0]] = bad_value
        return values

    monkeypatch.setattr(service, "_sample_design", altered)
    run = service.run_random_search(experiment, random_seed=42, budget=3)
    assert calls == 3 and run.candidate_count == 3
    failed, *good = run.result.candidates
    assert failed.evaluation_status == "FAILED" and failed.constraint_violations[0].status == expected
    assert failed.objective_values == () and not failed.ranking_eligible
    assert run.result.failed_candidates == 1
    assert all(c.ranking_eligible for c in good)
    assert run.result.best_candidate in good and run.result.best_candidate != failed
    if expected == "OUT_OF_RANGE":
        assert failed.constraint_violations[0].violation_value == pytest.approx(.9)
        assert failed.evaluation_record is None
    else:
        assert failed.design_vector is None and failed.evaluation_record.error.code == "INVALID_INPUT"


def test_injected_internal_value_error_does_not_score_or_abort_later_candidates(monkeypatch):
    original = d4.evaluate_design
    calls = 0

    def altered(request):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ValueError("explicit injected service failure")
        return original(request)

    monkeypatch.setattr(d4, "evaluate_design", altered)
    run = service.run_random_search(search_problem(), random_seed=42, budget=3)
    failed = run.result.candidates[0]
    assert failed.constraint_violations[0].status == "SERVICE_ERROR"
    assert failed.objective_values == () and run.result.failed_candidates == 1
    assert run.result.best_candidate.candidate_id != failed.candidate_id


def test_problem_and_global_rng_remain_unchanged():
    experiment = search_problem()
    before = experiment.model_dump()
    global_state = random.getstate()
    service.run_random_search(experiment, random_seed=42, budget=10)
    assert experiment.model_dump() == before and random.getstate() == global_state


def test_result_and_run_json_roundtrip():
    run = service.run_random_search(search_problem(), random_seed=42, budget=10)
    assert OptimizationResult.model_validate_json(run.result.model_dump_json()) == run.result
    assert OptimizationRun.model_validate_json(run.model_dump_json()) == run


def test_engineering_problem_is_not_sampled_or_evaluated(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("engineering scope must not execute")
    monkeypatch.setattr(service, "_sample_design", forbidden)
    monkeypatch.setattr(service.w41, "evaluate_candidate_safely", forbidden)
    run = service.run_random_search(engineering_problem(), random_seed=42, budget=3)
    assert run.status == "NOT_RUN" and run.candidate_count == 0 and run.result is None


@pytest.mark.parametrize("changes", [dict(budget=0), dict(budget=11), dict(budget=True), dict(budget=1.5),
                                     dict(random_seed=None), dict(random_seed=True), dict(random_seed=-1),
                                     dict(run_id="invalid id")])
def test_invalid_run_metadata_rejected_before_sampling(monkeypatch, changes):
    def forbidden(*args):
        raise AssertionError("invalid metadata must not sample")
    monkeypatch.setattr(service, "_sample_design", forbidden)
    with pytest.raises(ValueError): service.run_random_search(search_problem(), **changes)


@pytest.mark.parametrize("signal", [KeyboardInterrupt(), SystemExit(2), MemoryError()])
def test_injected_termination_signals_propagate(monkeypatch, signal):
    def fail(request):
        raise signal
    monkeypatch.setattr(d4, "evaluate_design", fail)
    with pytest.raises(type(signal)) as caught:
        service.run_random_search(search_problem(), random_seed=42, budget=3)
    assert caught.value is signal
