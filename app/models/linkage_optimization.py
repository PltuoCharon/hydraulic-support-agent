"""W41 candidate design contract; does not replace W38 reference geometry."""

import json
from math import hypot, isfinite
from typing import Literal, Self

from pydantic import Field, model_validator

from app.models.overall_design import StrictModel
from app.models.linkage_geometry import (
    DegreeParameter, EngineeringPoint2D, MillimetreParameter,
    NormalizedOriginPoint,
)
from app.models.linkage_closure import NumericalTolerance, ReferenceBranch

DESIGN_VARIABLE_ORDER = (
    "rear_link_length_mm",
    "shield_beam_effective_length_mm",
    "front_link_length_mm",
)
DesignDomain = Literal["SYNTHETIC_MATH", "ENGINEERING_REFERENCE"]
CaseReadiness = Literal["READY", "NOT_SOLVER_READY"]


def _check_raw(value):
    """Reject implicit numeric coercion before existing nested models parse."""
    if isinstance(value, StrictModel):
        value = value.model_dump(mode="python")
    if isinstance(value, dict):
        if "value" in value and "unit" not in value:
            raise ValueError("explicit parameter unit is required")
        if "engineering_verified" in value and value["engineering_verified"] is not False:
            raise ValueError("V1 engineering_verified must be literal false")
        for key, item in value.items():
            if key in {"value", "absolute_mm", "relative", "x_mm", "y_mm"}:
                if not isinstance(item, (dict, StrictModel)):
                    if type(item) not in (int, float) or not isfinite(item):
                        raise ValueError(f"{key} requires a finite numeric int/float")
            _check_raw(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _check_raw(item)
    return value


def _parameter(parameter, *, positive=False):
    if not isfinite(parameter.value) or (positive and parameter.value <= 0):
        raise ValueError("parameter must be finite and lengths strictly positive")
    if not parameter.source_text or not parameter.source_text.strip():
        raise ValueError("explicit parameter source_text is required")


class CandidateContract(StrictModel):
    @model_validator(mode="before")
    @classmethod
    def reject_coercion(cls, value):
        return _check_raw(value)

    @classmethod
    def model_validate_json(cls, json_data, **kwargs):
        return cls.from_json(json_data, **kwargs)

    @classmethod
    def from_json(cls, payload: str, **kwargs):
        """JSON entrypoint that rejects duplicate keys before they are lost."""
        def unique_pairs(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"duplicate field: {key}")
                result[key] = value
            return result
        return cls.model_validate(json.loads(payload, object_pairs_hook=unique_pairs), **kwargs)


class FourBarDesignVector(CandidateContract):
    rear_link_length_mm: MillimetreParameter
    shield_beam_effective_length_mm: MillimetreParameter
    front_link_length_mm: MillimetreParameter

    @model_validator(mode="after")
    def validate_lengths(self) -> Self:
        for name in DESIGN_VARIABLE_ORDER:
            _parameter(getattr(self, name), positive=True)
        return self

    def as_vector(self) -> tuple[float, float, float]:
        return tuple(getattr(self, name).value for name in DESIGN_VARIABLE_ORDER)


class LengthBounds(CandidateContract):
    lower: MillimetreParameter
    upper: MillimetreParameter

    @model_validator(mode="after")
    def validate_interval(self) -> Self:
        _parameter(self.lower, positive=True)
        _parameter(self.upper, positive=True)
        if self.lower.value >= self.upper.value:
            raise ValueError("bounds require lower < upper")
        return self


class DesignVariableBounds(CandidateContract):
    domain: DesignDomain
    rear_link_length_mm: LengthBounds
    shield_beam_effective_length_mm: LengthBounds
    front_link_length_mm: LengthBounds

    def validate_design(self, design: FourBarDesignVector) -> None:
        for name in DESIGN_VARIABLE_ORDER:
            interval = getattr(self, name)
            if not interval.lower.value <= getattr(design, name).value <= interval.upper.value:
                raise ValueError(f"{name} outside declared bounds")


class DesignCase(CandidateContract):
    domain: DesignDomain
    case_id: str = Field(min_length=1)
    readiness: CaseReadiness
    source_text: str = Field(min_length=1)
    engineering_verified: Literal[False] = False

    @model_validator(mode="after")
    def enforce_domain_gate(self) -> Self:
        if not self.case_id.strip() or not self.source_text.strip():
            raise ValueError("case id and source must not be blank")
        if self.domain == "ENGINEERING_REFERENCE" and self.readiness != "NOT_SOLVER_READY":
            raise ValueError("V1 has no independently verified engineering readiness path")
        if self.case_id.startswith("ER-") and self.domain != "ENGINEERING_REFERENCE":
            raise ValueError("ER cases cannot be relabelled as synthetic")
        if self.case_id.startswith("SM-") and self.domain != "SYNTHETIC_MATH":
            raise ValueError("SM cases cannot be relabelled as engineering")
        return self


class FixedEvaluationConfig(CandidateContract):
    rear_link_base: NormalizedOriginPoint = Field(default_factory=NormalizedOriginPoint)
    front_link_base: EngineeringPoint2D
    rear_link_angle_deg: DegreeParameter
    reference_branch: ReferenceBranch | None  # Explicit null preserves ambiguity.
    tolerance: NumericalTolerance
    declared_base_pivot_spacing_mm: MillimetreParameter | None = None
    branch_source_text: str | None = None

    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        _parameter(self.front_link_base.x_mm)
        _parameter(self.front_link_base.y_mm)
        _parameter(self.rear_link_angle_deg)
        ad = hypot(self.front_link_base.x_mm.value, self.front_link_base.y_mm.value)
        if not isfinite(ad) or ad <= 0:
            raise ValueError("fixed A/D must define a finite positive spacing")
        if self.reference_branch is not None and (
            not self.branch_source_text or not self.branch_source_text.strip()
        ):
            raise ValueError("explicit branch source is required")
        if self.declared_base_pivot_spacing_mm is not None:
            _parameter(self.declared_base_pivot_spacing_mm, positive=True)
            from app.services.linkage_closure import _effective_distance_tolerance
            declared = self.declared_base_pivot_spacing_mm.value
            if abs(ad - declared) > _effective_distance_tolerance(self.tolerance, ad, declared):
                raise ValueError("declared AD is inconsistent with fixed A/D coordinates")
        return self


class CandidateDesignInput(CandidateContract):
    case: DesignCase
    design: FourBarDesignVector
    bounds: DesignVariableBounds
    configuration: FixedEvaluationConfig

    @model_validator(mode="after")
    def validate_domain_and_bounds(self) -> Self:
        if self.case.domain != self.bounds.domain:
            raise ValueError("case and bounds domains must agree")
        self.bounds.validate_design(self.design)
        return self
