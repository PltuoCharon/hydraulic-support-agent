"""
W42-D7 optimization experiment history models.

Only persistence contracts.
No optimization algorithm.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ExperimentModel(BaseModel):

    model_config = {
        "frozen": True
    }



class OptimizationExperiment(ExperimentModel):

    experiment_id: str = Field(
        pattern=r"^[A-Za-z0-9_.-]{1,128}$"
    )

    problem_id: str

    algorithm_name: str

    random_seed: int | None = Field(
        default=None,
        ge=0
    )

    budget: int = Field(
        gt=0
    )

    status: Literal[
        "CREATED",
        "RUNNING",
        "COMPLETED",
        "FAILED"
    ]

    created_time: datetime



class OptimizationIteration(ExperimentModel):

    experiment_id: str

    iteration: int = Field(
        ge=0
    )

    candidate_id: str

    objective_values: tuple[float, ...]

    feasible: bool

    rank: int = Field(
        ge=0
    )



class OptimizationSnapshot(ExperimentModel):

    experiment_id: str

    total_candidates: int = Field(
        ge=0
    )

    failed_candidates: int = Field(
        ge=0
    )

    best_candidate_id: str | None

    pareto_candidate_ids: tuple[str, ...]

    created_time: datetime
