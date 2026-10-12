"""
W42-D6 Pareto ranking models.

Only ranking evidence.
No optimization algorithm.
"""

from typing import Literal

from pydantic import BaseModel, Field


class RankingModel(BaseModel):
    model_config = {
        "frozen": True
    }


class RankedCandidate(RankingModel):

    candidate_id: str = Field(
        pattern=r"^[A-Za-z0-9_.-]{1,128}$"
    )

    objective_values: tuple[float, ...]

    feasible: bool

    rank: int = Field(
        ge=0
    )

    dominance_count: int = Field(
        ge=0
    )

    source: Literal[
        "W42_D6_PARETO"
    ] = "W42_D6_PARETO"



class ParetoFront(RankingModel):

    candidates: tuple[RankedCandidate, ...]

    total_candidates: int = Field(
        ge=0
    )

    feasible_candidates: int = Field(
        ge=0
    )
