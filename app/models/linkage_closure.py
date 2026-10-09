"""W39-D2 strongly typed four-bar closure models.

Boundary:
- data contract and validation only
- no point-B calculation
- no circle-intersection calculation
- no branch-selection algorithm
- no trajectory solving
- no optimization
"""

from math import isfinite
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from app.models.linkage_geometry import (
    DegreeParameter,
    EngineeringPoint2D,
    MillimetreParameter,
    NormalizedOriginPoint,
)
from app.models.overall_design import StrictModel


ClosureMultiplicity = Literal[
    "NO_SOLUTION",
    "TANGENT",
    "TWO_SOLUTIONS",
    "DEGENERATE",
]

CandidateBranch = Literal[
    "POSITIVE",
    "NEGATIVE",
    "TANGENT",
]

ReferenceBranch = Literal[
    "POSITIVE",
    "NEGATIVE",
]

SelectionStatus = Literal[
    "SELECTED",
    "BRANCH_AMBIGUOUS",
    "NOT_APPLICABLE",
]

BranchResolution = Literal[
    "REFERENCE_POSE",
    "TANGENT_UNIQUE",
    "NONE",
]


class NumericalTolerance(StrictModel):
    """Scale-aware numerical tolerance infrastructure."""

    absolute_mm: float
    relative: float

    @model_validator(mode="after")
    def validate_tolerance(self) -> Self:
        for name, value in (
            ("absolute_mm", self.absolute_mm),
            ("relative", self.relative),
        ):
            if not isfinite(value):
                raise ValueError(
                    f"{name} must be finite"
                )

            if value <= 0:
                raise ValueError(
                    f"{name} must be greater than zero"
                )

        return self


def _validate_finite_parameter(
    parameter,
    *,
    name: str,
    positive: bool = False,
) -> None:
    value = parameter.value

    if not isfinite(value):
        raise ValueError(
            f"{name} must be finite"
        )

    if positive and value <= 0:
        raise ValueError(
            f"{name} must be greater than zero"
        )


def _validate_solved_coordinate_parameter(
    parameter,
    *,
    name: str,
) -> None:
    _validate_finite_parameter(
        parameter,
        name=name,
    )

    if parameter.origin != "CALCULATED":
        raise ValueError(
            f"{name} must have origin CALCULATED"
        )

    if parameter.evidence_status != "PARTIAL":
        raise ValueError(
            f"{name} must have evidence_status PARTIAL"
        )

    if parameter.formula_ids:
        raise ValueError(
            f"{name} must not claim Formula IDs"
        )

    if parameter.calculation_record_ids:
        raise ValueError(
            f"{name} must not claim Calculation Record IDs"
        )


def _validate_solved_point(
    point: EngineeringPoint2D,
    *,
    name: str,
) -> None:
    _validate_solved_coordinate_parameter(
        point.x_mm,
        name=f"{name}.x_mm",
    )

    _validate_solved_coordinate_parameter(
        point.y_mm,
        name=f"{name}.y_mm",
    )


class ClosureSolverInput(StrictModel):
    """Explicit input for one hs.linkageClosure.v1 solver task."""

    version: Literal[1] = 1

    rear_link_base: NormalizedOriginPoint = Field(
        default_factory=NormalizedOriginPoint
    )

    front_link_base: EngineeringPoint2D

    rear_link_length_mm: MillimetreParameter
    shield_beam_effective_length_mm: MillimetreParameter
    front_link_length_mm: MillimetreParameter
    base_pivot_spacing_mm: MillimetreParameter

    rear_link_angle_deg: DegreeParameter

    reference_branch: ReferenceBranch | None = None

    tolerance: NumericalTolerance

    @model_validator(mode="after")
    def validate_solver_input(self) -> Self:
        for name, parameter in (
            (
                "rear_link_length_mm",
                self.rear_link_length_mm,
            ),
            (
                "shield_beam_effective_length_mm",
                self.shield_beam_effective_length_mm,
            ),
            (
                "front_link_length_mm",
                self.front_link_length_mm,
            ),
            (
                "base_pivot_spacing_mm",
                self.base_pivot_spacing_mm,
            ),
        ):
            _validate_finite_parameter(
                parameter,
                name=name,
                positive=True,
            )

        _validate_finite_parameter(
            self.rear_link_angle_deg,
            name="rear_link_angle_deg",
        )

        _validate_finite_parameter(
            self.front_link_base.x_mm,
            name="front_link_base.x_mm",
        )

        _validate_finite_parameter(
            self.front_link_base.y_mm,
            name="front_link_base.y_mm",
        )

        return self


class ClosureCandidate(StrictModel):
    """One mathematically valid C candidate."""

    point_c: EngineeringPoint2D
    branch: CandidateBranch

    note: str | None = None

    @model_validator(mode="after")
    def validate_candidate_provenance(self) -> Self:
        _validate_solved_point(
            self.point_c,
            name="point_c",
        )
        return self


class ClosureSelectedPose(StrictModel):
    """One selected deterministic four-bar pose."""

    rear_link_shield: EngineeringPoint2D
    front_link_shield: EngineeringPoint2D

    rear_link_angle_deg: DegreeParameter

    branch: CandidateBranch

    @model_validator(mode="after")
    def validate_pose_provenance(self) -> Self:
        _validate_solved_point(
            self.rear_link_shield,
            name="rear_link_shield",
        )

        _validate_solved_point(
            self.front_link_shield,
            name="front_link_shield",
        )

        _validate_finite_parameter(
            self.rear_link_angle_deg,
            name="rear_link_angle_deg",
        )

        return self


class ClosureSolverProvenance(StrictModel):
    """Current W39 closure-solver evidence boundary."""

    engine: Literal[
        "W39_DETERMINISTIC_FOUR_BAR_CLOSURE"
    ] = "W39_DETERMINISTIC_FOUR_BAR_CLOSURE"

    evidence_status: Literal["PARTIAL"] = "PARTIAL"

    formula_ids: list[str] = Field(
        default_factory=list
    )

    calculation_record_ids: list[int] = Field(
        default_factory=list
    )

    branch_resolution: BranchResolution = "NONE"

    note: str | None = None

    @model_validator(mode="after")
    def validate_current_traceability(self) -> Self:
        if self.formula_ids:
            raise ValueError(
                "W39 closure solver must not claim Formula IDs"
            )

        if self.calculation_record_ids:
            raise ValueError(
                "W39 closure solver must not claim "
                "Calculation Record IDs"
            )

        return self


class ClosureResult(StrictModel):
    """Strongly typed hs.linkageClosure.v1 result."""

    version: Literal[1] = 1

    closure_state: ClosureMultiplicity
    selection_status: SelectionStatus

    rear_link_shield: EngineeringPoint2D

    candidates: list[ClosureCandidate] = Field(
        default_factory=list
    )

    selected_pose: ClosureSelectedPose | None = None

    provenance: ClosureSolverProvenance = Field(
        default_factory=ClosureSolverProvenance
    )

    note: str | None = None

    @model_validator(mode="after")
    def validate_result_invariants(self) -> Self:
        _validate_solved_point(
            self.rear_link_shield,
            name="rear_link_shield",
        )

        state = self.closure_state
        status = self.selection_status
        resolution = self.provenance.branch_resolution

        if self.selected_pose is not None:
            if (
                self.selected_pose.rear_link_shield
                != self.rear_link_shield
            ):
                raise ValueError(
                    "selected_pose rear_link_shield must "
                    "match ClosureResult rear_link_shield"
                )

        if state == "NO_SOLUTION":
            if self.candidates:
                raise ValueError(
                    "NO_SOLUTION must have no candidates"
                )

            if status != "NOT_APPLICABLE":
                raise ValueError(
                    "NO_SOLUTION selection_status "
                    "must be NOT_APPLICABLE"
                )

            if self.selected_pose is not None:
                raise ValueError(
                    "NO_SOLUTION must not have selected_pose"
                )

            if resolution != "NONE":
                raise ValueError(
                    "NO_SOLUTION branch_resolution must be NONE"
                )

            return self

        if state == "DEGENERATE":
            if self.candidates:
                raise ValueError(
                    "DEGENERATE must have no candidates"
                )

            if status != "NOT_APPLICABLE":
                raise ValueError(
                    "DEGENERATE selection_status "
                    "must be NOT_APPLICABLE"
                )

            if self.selected_pose is not None:
                raise ValueError(
                    "DEGENERATE must not have selected_pose"
                )

            if resolution != "NONE":
                raise ValueError(
                    "DEGENERATE branch_resolution must be NONE"
                )

            return self

        if state == "TANGENT":
            if len(self.candidates) != 1:
                raise ValueError(
                    "TANGENT must have exactly one candidate"
                )

            if self.candidates[0].branch != "TANGENT":
                raise ValueError(
                    "TANGENT candidate branch must be TANGENT"
                )

            if status != "SELECTED":
                raise ValueError(
                    "TANGENT selection_status must be SELECTED"
                )

            if self.selected_pose is None:
                raise ValueError(
                    "TANGENT must have selected_pose"
                )

            if self.selected_pose.branch != "TANGENT":
                raise ValueError(
                    "TANGENT selected pose branch "
                    "must be TANGENT"
                )

            if (
                self.selected_pose.front_link_shield
                != self.candidates[0].point_c
            ):
                raise ValueError(
                    "TANGENT selected pose must match "
                    "the sole closure candidate"
                )

            if resolution != "TANGENT_UNIQUE":
                raise ValueError(
                    "TANGENT branch_resolution "
                    "must be TANGENT_UNIQUE"
                )

            return self

        if state == "TWO_SOLUTIONS":
            if len(self.candidates) != 2:
                raise ValueError(
                    "TWO_SOLUTIONS must have exactly "
                    "two candidates"
                )

            branches = {
                candidate.branch
                for candidate in self.candidates
            }

            if branches != {
                "POSITIVE",
                "NEGATIVE",
            }:
                raise ValueError(
                    "TWO_SOLUTIONS candidate branches "
                    "must be exactly POSITIVE and NEGATIVE"
                )

            if status == "BRANCH_AMBIGUOUS":
                if self.selected_pose is not None:
                    raise ValueError(
                        "BRANCH_AMBIGUOUS must not have "
                        "selected_pose"
                    )

                if resolution != "NONE":
                    raise ValueError(
                        "BRANCH_AMBIGUOUS branch_resolution "
                        "must be NONE"
                    )

                return self

            if status == "SELECTED":
                if self.selected_pose is None:
                    raise ValueError(
                        "SELECTED requires selected_pose"
                    )

                if self.selected_pose.branch not in {
                    "POSITIVE",
                    "NEGATIVE",
                }:
                    raise ValueError(
                        "TWO_SOLUTIONS selected pose branch "
                        "must be POSITIVE or NEGATIVE"
                    )

                candidate_branches = {
                    candidate.branch
                    for candidate in self.candidates
                }

                if (
                    self.selected_pose.branch
                    not in candidate_branches
                ):
                    raise ValueError(
                        "selected pose branch must match "
                        "one closure candidate"
                    )

                selected_candidate = next(
                    candidate
                    for candidate in self.candidates
                    if (
                        candidate.branch
                        == self.selected_pose.branch
                    )
                )

                if (
                    self.selected_pose.front_link_shield
                    != selected_candidate.point_c
                ):
                    raise ValueError(
                        "selected pose coordinates must "
                        "match the selected closure candidate"
                    )

                if resolution != "REFERENCE_POSE":
                    raise ValueError(
                        "selected TWO_SOLUTIONS result requires "
                        "REFERENCE_POSE branch resolution"
                    )

                return self

            raise ValueError(
                "TWO_SOLUTIONS selection_status must be "
                "SELECTED or BRANCH_AMBIGUOUS"
            )

        raise ValueError(
            f"unsupported closure_state: {state}"
        )


def validate_closure_solver_input(
    payload: dict[str, Any],
) -> ClosureSolverInput:
    """Validate hs.linkageClosure.v1 solver input."""

    return ClosureSolverInput.model_validate(payload)


def validate_closure_result(
    payload: dict[str, Any],
) -> ClosureResult:
    """Validate hs.linkageClosure.v1 solver result."""

    return ClosureResult.model_validate(payload)


def serialize_closure_result(
    result: ClosureResult,
) -> dict[str, Any]:
    """Serialize a closure result to JSON-compatible data."""

    return result.model_dump(mode="json")
