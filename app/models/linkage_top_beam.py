"""W40-D5 strongly typed shield/top-beam joint trajectory models.

Boundary:
- typed rigid shield-body attachment data
- typed propagated E trajectory data
- no propagation execution
- no beam-tip trajectory
- no top-beam orientation solving
- no support-height solving
- no 80 mm validation
"""

from __future__ import annotations

import math
from typing import Literal, Self

from pydantic import Field, model_validator

from app.models.linkage_closure import (
    ClosureMultiplicity,
    ReferenceBranch,
)
from app.models.linkage_geometry import (
    DegreeParameter,
    EngineeringPoint2D,
    MillimetreParameter,
)
from app.models.linkage_motion import (
    MotionDirection,
    MotionTermination,
)
from app.models.overall_design import StrictModel


def _validate_finite_parameter(
    parameter,
    *,
    name: str,
) -> None:
    value = float(parameter.value)

    if not math.isfinite(value):
        raise ValueError(
            f"{name} must be finite"
        )


def _validate_reference_point(
    point: EngineeringPoint2D,
    *,
    name: str,
) -> None:
    _validate_finite_parameter(
        point.x_mm,
        name=f"{name}.x_mm",
    )

    _validate_finite_parameter(
        point.y_mm,
        name=f"{name}.y_mm",
    )


def _validate_calculated_mm(
    parameter: MillimetreParameter,
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


def _validate_calculated_point(
    point: EngineeringPoint2D,
    *,
    name: str,
) -> None:
    _validate_calculated_mm(
        point.x_mm,
        name=f"{name}.x_mm",
    )

    _validate_calculated_mm(
        point.y_mm,
        name=f"{name}.y_mm",
    )


class ShieldTopBeamJointPropagationProvenance(
    StrictModel
):
    """Frozen provenance for W40-D5 rigid propagation."""

    engine: Literal[
        "W40_SHIELD_TOP_BEAM_JOINT_RIGID_PROPAGATION"
    ] = "W40_SHIELD_TOP_BEAM_JOINT_RIGID_PROPAGATION"

    evidence_status: Literal[
        "PARTIAL"
    ] = "PARTIAL"

    formula_ids: list[str] = Field(
        default_factory=list
    )

    calculation_record_ids: list[int] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_no_fabricated_trace(
        self,
    ) -> Self:
        if self.formula_ids:
            raise ValueError(
                "W40-D5 propagation provenance must not "
                "invent Formula Registry IDs"
            )

        if self.calculation_record_ids:
            raise ValueError(
                "W40-D5 propagation provenance must not "
                "invent Calculation Record IDs"
            )

        return self


class ShieldTopBeamJointAttachment(
    StrictModel
):
    """Reference E attachment in the directed shield frame."""

    version: Literal[1] = 1

    reference_rear_link_shield: EngineeringPoint2D
    reference_front_link_shield: EngineeringPoint2D
    reference_joint_center: EngineeringPoint2D

    longitudinal_offset_mm: MillimetreParameter
    normal_offset_mm: MillimetreParameter

    provenance: (
        ShieldTopBeamJointPropagationProvenance
    ) = Field(
        default_factory=(
            ShieldTopBeamJointPropagationProvenance
        )
    )

    @model_validator(mode="after")
    def validate_attachment(
        self,
    ) -> Self:
        _validate_reference_point(
            self.reference_rear_link_shield,
            name="reference_rear_link_shield",
        )

        _validate_reference_point(
            self.reference_front_link_shield,
            name="reference_front_link_shield",
        )

        _validate_reference_point(
            self.reference_joint_center,
            name="reference_joint_center",
        )

        b_x = float(
            self.reference_rear_link_shield.x_mm.value
        )
        b_y = float(
            self.reference_rear_link_shield.y_mm.value
        )

        c_x = float(
            self.reference_front_link_shield.x_mm.value
        )
        c_y = float(
            self.reference_front_link_shield.y_mm.value
        )

        if b_x == c_x and b_y == c_y:
            raise ValueError(
                "reference B/C shield axis must not "
                "have zero length"
            )

        _validate_calculated_mm(
            self.longitudinal_offset_mm,
            name="longitudinal_offset_mm",
        )

        _validate_calculated_mm(
            self.normal_offset_mm,
            name="normal_offset_mm",
        )

        return self


class ShieldTopBeamJointTrajectorySample(
    StrictModel
):
    """One E-trajectory sample aligned with one W40 motion sample."""

    version: Literal[1] = 1

    sample_index: int = Field(
        ge=0
    )

    requested_angle_deg: DegreeParameter

    closure_state: ClosureMultiplicity

    selected_pose_available: bool

    joint_center: EngineeringPoint2D | None = None

    @model_validator(mode="after")
    def validate_sample(
        self,
    ) -> Self:
        _validate_finite_parameter(
            self.requested_angle_deg,
            name="requested_angle_deg",
        )

        if self.selected_pose_available:
            if self.closure_state not in {
                "TWO_SOLUTIONS",
                "TANGENT",
            }:
                raise ValueError(
                    "selected_pose_available=true requires "
                    "TWO_SOLUTIONS or TANGENT"
                )

            if self.joint_center is None:
                raise ValueError(
                    "selected trajectory sample requires "
                    "joint_center"
                )

            _validate_calculated_point(
                self.joint_center,
                name="joint_center",
            )

        else:
            if self.closure_state not in {
                "NO_SOLUTION",
                "DEGENERATE",
            }:
                raise ValueError(
                    "selected_pose_available=false requires "
                    "NO_SOLUTION or DEGENERATE"
                )

            if self.joint_center is not None:
                raise ValueError(
                    "unsolved trajectory sample must not "
                    "contain joint_center"
                )

        return self


class ShieldTopBeamJointTrajectoryResult(
    StrictModel
):
    """One typed E trajectory aligned with one W40 motion segment."""

    version: Literal[1] = 1

    attachment: ShieldTopBeamJointAttachment

    direction: MotionDirection

    reference_branch: ReferenceBranch

    reference_angle_deg: DegreeParameter

    requested_angle_count: int = Field(
        gt=0
    )

    samples: list[
        ShieldTopBeamJointTrajectorySample
    ] = Field(
        min_length=1
    )

    termination: MotionTermination

    provenance: (
        ShieldTopBeamJointPropagationProvenance
    ) = Field(
        default_factory=(
            ShieldTopBeamJointPropagationProvenance
        )
    )

    @staticmethod
    def _is_normal_sample(
        sample: ShieldTopBeamJointTrajectorySample,
    ) -> bool:
        return (
            sample.closure_state
            == "TWO_SOLUTIONS"
            and sample.selected_pose_available
            and sample.joint_center is not None
        )

    @staticmethod
    def _is_tangent_sample(
        sample: ShieldTopBeamJointTrajectorySample,
    ) -> bool:
        return (
            sample.closure_state
            == "TANGENT"
            and sample.selected_pose_available
            and sample.joint_center is not None
        )

    @staticmethod
    def _is_no_solution_sample(
        sample: ShieldTopBeamJointTrajectorySample,
    ) -> bool:
        return (
            sample.closure_state
            == "NO_SOLUTION"
            and not sample.selected_pose_available
            and sample.joint_center is None
        )

    @staticmethod
    def _is_degenerate_sample(
        sample: ShieldTopBeamJointTrajectorySample,
    ) -> bool:
        return (
            sample.closure_state
            == "DEGENERATE"
            and not sample.selected_pose_available
            and sample.joint_center is None
        )

    @model_validator(mode="after")
    def validate_trajectory(
        self,
    ) -> Self:
        if self.reference_branch not in {
            "POSITIVE",
            "NEGATIVE",
        }:
            raise ValueError(
                "trajectory reference branch must be "
                "POSITIVE or NEGATIVE"
            )

        reference_angle = float(
            self.reference_angle_deg.value
        )

        if not math.isfinite(reference_angle):
            raise ValueError(
                "trajectory reference angle must be finite"
            )

        if len(self.samples) > self.requested_angle_count:
            raise ValueError(
                "trajectory sample count cannot exceed "
                "requested angle count"
            )

        expected_indexes = list(
            range(len(self.samples))
        )

        actual_indexes = [
            sample.sample_index
            for sample in self.samples
        ]

        if actual_indexes != expected_indexes:
            raise ValueError(
                "trajectory sample indexes must be "
                "contiguous from zero"
            )

        values = [
            float(
                sample.requested_angle_deg.value
            )
            for sample in self.samples
        ]

        if values[0] != reference_angle:
            raise ValueError(
                "first trajectory sample must equal "
                "the reference angle"
            )

        for previous, current in zip(
            values,
            values[1:],
        ):
            if self.direction == "INCREASING":
                if not current > previous:
                    raise ValueError(
                        "INCREASING trajectory angles "
                        "must remain strictly increasing"
                    )

            elif self.direction == "DECREASING":
                if not current < previous:
                    raise ValueError(
                        "DECREASING trajectory angles "
                        "must remain strictly decreasing"
                    )

        first = self.samples[0]

        if not self._is_normal_sample(
            first
        ):
            raise ValueError(
                "first E trajectory sample must be a "
                "selected TWO_SOLUTIONS reference pose"
            )

        if self.termination == "COMPLETED":
            if len(self.samples) != self.requested_angle_count:
                raise ValueError(
                    "COMPLETED E trajectory must contain "
                    "every processed requested angle"
                )

            if not all(
                self._is_normal_sample(
                    sample
                )
                for sample in self.samples
            ):
                raise ValueError(
                    "COMPLETED E trajectory may contain "
                    "only selected TWO_SOLUTIONS samples"
                )

            return self

        final = self.samples[-1]
        preceding = self.samples[:-1]

        if not all(
            self._is_normal_sample(
                sample
            )
            for sample in preceding
        ):
            raise ValueError(
                "all E trajectory samples before a "
                "boundary must be selected "
                "TWO_SOLUTIONS poses"
            )

        if self.termination == "TANGENT_BOUNDARY":
            if not self._is_tangent_sample(
                final
            ):
                raise ValueError(
                    "TANGENT_BOUNDARY requires a final "
                    "selected TANGENT trajectory sample"
                )

        elif self.termination == "NO_SOLUTION_BOUNDARY":
            if not self._is_no_solution_sample(
                final
            ):
                raise ValueError(
                    "NO_SOLUTION_BOUNDARY requires a final "
                    "NO_SOLUTION trajectory sample"
                )

        elif self.termination == "DEGENERATE_BOUNDARY":
            if not self._is_degenerate_sample(
                final
            ):
                raise ValueError(
                    "DEGENERATE_BOUNDARY requires a final "
                    "DEGENERATE trajectory sample"
                )

        return self
