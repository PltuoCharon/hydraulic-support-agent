"""Seeded random-search framework baseline over W41 synthetic evaluations."""

from math import isfinite
from random import Random

from app.models.optimization_contract import (
    ConstraintViolation, OptimizationCandidate, OptimizationProblem,
    OptimizationResult, OptimizationRun, VariableValue,
)
from app.services import linkage_optimization_evaluation as w41


def _sample_design(problem: OptimizationProblem, rng: Random) -> dict[str, float]:
    return {b.variable_name: rng.uniform(b.lower, b.upper) for b in problem.bounds}


def _source(problem: OptimizationProblem, name: str, seed: int) -> str:
    bound = next(b for b in problem.bounds if b.variable_name == name)
    return f"RANDOM_SEARCH_V1 synthetic sample; seed={seed}; declared bound source: {bound.source}"


def _out_of_range_candidate(problem, candidate_id, values, seed):
    """Keep genuine bound exceedances; invalid types go to W41 validation."""
    try:
        if any(type(values[n]) not in (int, float) or not isfinite(values[n]) or values[n] <= 0
               for n in problem.variable_names):
            return None
    except OverflowError:
        return None
    violations = []
    for bound in problem.bounds:
        value = values[bound.variable_name]
        excess = max(bound.lower - value, value - bound.upper, 0.0)
        if excess > 0:
            violations.append(ConstraintViolation(
                constraint_name=bound.variable_name, status="OUT_OF_RANGE",
                violation_value=excess, unit="mm", source="DECLARED_BOUNDS",
            ))
    if not violations:
        return None
    vector = tuple(VariableValue(variable_name=n, value=values[n], unit="mm",
                                  source=_source(problem, n, seed)) for n in problem.variable_names)
    return OptimizationCandidate(
        candidate_id=candidate_id, problem=problem, design_vector=vector,
        evaluation_status="FAILED", constraint_violations=tuple(violations),
    )


def _evaluation_request(problem, comparison, values, seed):
    # Preserve all evaluation conditions and provenance; only AB/BC/CD change.
    return dict(
        case=comparison.case.model_dump(mode="python"),
        candidate=dict(
            case=comparison.case.model_dump(mode="python"),
            design={n: dict(
                value=values[n], unit="mm", origin="CALCULATED", evidence_status="PARTIAL",
                source_text=_source(problem, n, seed), formula_ids=[], calculation_record_ids=[],
            ) for n in problem.variable_names},
            bounds=comparison.bounds.model_dump(mode="python"),
            configuration=comparison.configuration.model_dump(mode="python"),
        ),
        plan=comparison.plan.model_dump(mode="python"),
        objective=comparison.objective.model_dump(mode="python"),
    )


def run_random_search(
    problem: OptimizationProblem, *, random_seed: int = 0, budget: int | None = None,
    run_id: str = "random-search-v1",
) -> OptimizationRun:
    """Return an immutable run with its result and every attempted candidate.

    The budget counts candidate attempts, including validation failures, not W39
    calls or elapsed time. Same problem/seed/budget/run_id produces identical data
    in the same execution environment. Engineering problems return NOT_RUN.
    """
    problem = OptimizationProblem.model_validate(problem)
    if type(random_seed) is not int or random_seed < 0:
        raise ValueError("random_seed must be a nonnegative integer")
    count = problem.evaluation_budget if budget is None else budget
    run_metadata = dict(
        run_id=run_id, problem=problem, algorithm_name="RANDOM_SEARCH_V1",
        random_seed=random_seed, budget=count,
    )
    if problem.domain != "SYNTHETIC_MATH" or problem.readiness != "READY":
        return OptimizationRun(**run_metadata, candidate_count=0, status="NOT_RUN")
    # Reject invalid budgets/identifiers before sampling or invoking W41.
    OptimizationRun(**run_metadata, candidate_count=0, status="NOT_STARTED")
    comparison = problem.comparison_contract
    rng = Random(random_seed)  # Never seed or consume the process-global RNG.
    candidates = []
    best = None
    for index in range(count):
        candidate_id = f"rs-{index + 1:06d}"
        values = _sample_design(problem, rng)
        candidate = _out_of_range_candidate(problem, candidate_id, values, random_seed)
        if candidate is None:
            record = w41.evaluate_candidate_safely(
                candidate_id, _evaluation_request(problem, comparison, values, random_seed), comparison,
            )
            candidate = OptimizationCandidate.from_w41(problem, record)
        candidates.append(candidate)
        if candidate.ranking_eligible and (
            best is None or candidate.objective_values[0].value < best.objective_values[0].value
        ):
            best = candidate
    result = OptimizationResult(
        problem=problem, candidates=tuple(candidates), best_candidate=best,
        objective_vector=best.objective_values if best is not None else (),
        feasible=best is not None, total_candidates=len(candidates),
        failed_candidates=sum(not c.ranking_eligible for c in candidates),
    )
    return OptimizationRun(**run_metadata, candidate_count=len(candidates), status="COMPLETED", result=result)
