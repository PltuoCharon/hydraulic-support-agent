"""
W42-D7 experiment history service.

Immutable history storage.
"""

from app.models.optimization_experiment import (
    OptimizationExperiment,
    OptimizationIteration,
    OptimizationSnapshot,
)



class OptimizationHistory:

    def __init__(self):

        self._experiments = {}

        self._iterations = {}

        self._snapshots = {}



    def add_experiment(
        self,
        experiment: OptimizationExperiment,
    ):

        if experiment.experiment_id in self._experiments:
            raise ValueError(
                "experiment already exists"
            )

        self._experiments[
            experiment.experiment_id
        ] = experiment



    def add_iteration(
        self,
        iteration: OptimizationIteration,
    ):

        self._iterations.setdefault(
            iteration.experiment_id,
            []
        ).append(iteration)



    def save_snapshot(
        self,
        snapshot: OptimizationSnapshot,
    ):

        self._snapshots[
            snapshot.experiment_id
        ] = snapshot



    def get_iterations(
        self,
        experiment_id: str,
    ):

        return tuple(
            self._iterations.get(
                experiment_id,
                []
            )
        )



    def get_snapshot(
        self,
        experiment_id: str,
    ):

        return self._snapshots.get(
            experiment_id
        )
