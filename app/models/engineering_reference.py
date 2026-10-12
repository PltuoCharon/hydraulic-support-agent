"""
W43-D2 engineering reference layer models.

Evidence isolation contract.
No engineering parameter fabrication.
"""

from datetime import datetime
from math import isfinite
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


class _ReferenceContract(BaseModel):

    model_config = {
        "frozen": True
    }


class EngineeringReference(_ReferenceContract):

    reference_id: str = Field(
        pattern=r"^[A-Za-z0-9_.-]{1,128}$"
    )

    name: str = Field(
        min_length=1,
        max_length=256
    )

    source_type: Literal[
        "SYNTHETIC_MATH",
        "ENGINEERING_REFERENCE",
        "EXTERNAL_DATA"
    ]

    verification_level: Literal[
        "UNKNOWN",
        "MODEL_ONLY",
        "DATA_SUPPORTED",
        "ENGINEERING_VERIFIED"
    ]

    description: str = Field(
        min_length=1
    )

    created_time: datetime


class EngineeringParameter(_ReferenceContract):

    name: str = Field(
        min_length=1,
        max_length=128
    )

    value: float

    unit: str = Field(
        min_length=1
    )

    source_reference: str = Field(
        min_length=1
    )

    verified: bool

    @model_validator(mode="after")
    def finite(self) -> Self:
        if not isfinite(self.value):
            raise ValueError("parameter value must be finite")
        return self
