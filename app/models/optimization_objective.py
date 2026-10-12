"""
W42-D5 Objective and Constraint Framework.

Optimization infrastructure only.
Not engineering optimization.
"""

from math import isfinite
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ObjectiveDefinition(BaseModel):

    model_config = ConfigDict(
        frozen=True
    )

    objective_id: str = Field(
        min_length=1
    )

    name: str

    direction: Literal[
        "MINIMIZE",
        "MAXIMIZE",
    ]

    unit: str

    description: str



class ObjectiveValue(BaseModel):

    model_config = ConfigDict(
        frozen=True
    )

    objective_id: str

    value: float

    unit: str

    source: str


    @field_validator("value")
    @classmethod
    def validate_value(cls, value):

        if not isfinite(value):
            raise ValueError(
                "objective value must be finite"
            )

        return value



class ConstraintDefinition(BaseModel):

    model_config = ConfigDict(
        frozen=True
    )

    constraint_id: str

    name: str

    constraint_type: Literal[
        "HARD",
        "SOFT",
    ]

    description: str



class ConstraintEvaluation(BaseModel):

    model_config = ConfigDict(
        frozen=True
    )

    constraint_id: str

    status: Literal[
        "PASS",
        "FAIL",
        "UNKNOWN",
    ]

    violation_value: float | None

    unit: str

    source: str



class OptimizationScore(BaseModel):

    model_config = ConfigDict(
        frozen=True
    )

    feasible: bool

    objective_values: tuple[
        ObjectiveValue,
        ...
    ]

    constraint_status: tuple[
        ConstraintEvaluation,
        ...
    ]

    score_source: str
