from pydantic import ValidationError
from datetime import datetime

import pytest


from app.models.optimization_experiment import (
    OptimizationExperiment,
    OptimizationIteration,
    OptimizationSnapshot,
)


from app.services.optimization_history import (
    OptimizationHistory,
)



def experiment():

    return OptimizationExperiment(
        experiment_id="exp1",
        problem_id="problem1",
        algorithm_name="RANDOM_SEARCH_V1",
        random_seed=1,
        budget=10,
        status="CREATED",
        created_time=datetime.utcnow(),
    )



def test_create_experiment():

    history = OptimizationHistory()

    history.add_experiment(
        experiment()
    )



def test_duplicate_experiment_rejected():

    history = OptimizationHistory()

    e = experiment()

    history.add_experiment(e)

    with pytest.raises(ValueError):

        history.add_experiment(e)



def test_iteration_history():

    history = OptimizationHistory()

    history.add_iteration(
        OptimizationIteration(
            experiment_id="exp1",
            iteration=0,
            candidate_id="c1",
            objective_values=(1.0,),
            feasible=True,
            rank=0,
        )
    )


    assert len(
        history.get_iterations("exp1")
    ) == 1



def test_snapshot_save():

    history = OptimizationHistory()


    snapshot = OptimizationSnapshot(
        experiment_id="exp1",
        total_candidates=10,
        failed_candidates=2,
        best_candidate_id="c1",
        pareto_candidate_ids=("c1",),
        created_time=datetime.utcnow(),
    )


    history.save_snapshot(snapshot)


    assert (
        history
        .get_snapshot("exp1")
        .best_candidate_id
        ==
        "c1"
    )



def test_snapshot_immutable():

    snapshot = OptimizationSnapshot(
        experiment_id="exp1",
        total_candidates=1,
        failed_candidates=0,
        best_candidate_id="c1",
        pareto_candidate_ids=("c1",),
        created_time=datetime.utcnow(),
    )

    with pytest.raises(ValidationError):
        snapshot.best_candidate_id = "c2"

