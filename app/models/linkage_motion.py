"""W40-D2 strongly typed continuous four-bar motion models.

Boundary:
- typed one-direction motion-segment data only
- no angle-sweep execution
- no support-height solving
- no top-beam propagation
- no beam-tip trajectory
- no optimization
"""

from __future__ import annotations

import math
from typing import Literal

from pydantic import Field, model_validator

from app.models.linkage_closure import (
    ClosureResult,
    ClosureSolverInput,
    ReferenceBranch,
)
from app.models.linkage_geometry import (
    DegreeParameter,
)
from app.models.overall_design import (
    StrictModel,
)


MotionDirection = Literal[
    "INCREASING",
    "DECREASING",
]

MotionTermination = Literal[
    "COMPLETED",
    "TANGENT_BOUNDARY",
    "NO_SOLUTION_BOUNDARY",
    "DEGENERATE_BOUNDARY",
]


class MotionSweepInput(StrictModel):
    """One explicit one-direction angle sweep."""

    version: Literal[1] = 1

    reference_task: ClosureSolverInput

    direction: MotionDirection

    angle_samples_deg: list[DegreeParameter] = Field(
        min_length=2
    )

    @model_validator(mode="after")
    def validate_sweep_semantics(
        self,
    ) -> "MotionSweepInput":
        branch = self.reference_task.reference_branch

        if branch not in {
            "POSITIVE",
            "NEGATIVE",
        }:
            raise ValueError(
                "continuous motion requires a non-null "
                "POSITIVE or NEGATIVE reference branch"
            )

        reference_angle = float(
            self.reference_task
            .rear_link_angle_deg
            .value
        )

        if not math.isfinite(reference_angle):
            raise ValueError(
                "reference rear-link angle must be finite"
            )

        values = []

        for index, angle in enumerate(
            self.angle_samples_deg
        ):
            value = float(angle.value)

            if not math.isfinite(value):
                raise ValueError(
                    "motion angle samples must be finite: "
                    f"index={index}"
                )

            values.append(value)

        if values[0] != reference_angle:
            raise ValueError(
                "first motion angle must equal "
                "the reference rear-link angle"
            )

        for previous, current in zip(
            values,
            values[1:],
        ):
            if self.direction == "INCREASING":
                if not current > previous:
                    raise ValueError(
                        "INCREASING motion angles must be "
                        "strictly increasing"
                    )

            elif self.direction == "DECREASING":
                if not current < previous:
                    raise ValueError(
                        "DECREASING motion angles must be "
                        "strictly decreasing"
                    )

        return self


class MotionSample(StrictModel):
    """One attempted angle sample and its complete W39 result."""

    version: Literal[1] = 1

    sample_index: int = Field(
        ge=0
    )

    requested_angle_deg: DegreeParameter

    closure_result: ClosureResult

    @model_validator(mode="after")
    def validate_sample(
        self,
    ) -> "MotionSample":
        value = float(
            self.requested_angle_deg.value
        )

        if not math.isfinite(value):
            raise ValueError(
                "requested motion angle must be finite"
            )

        return self


class MotionSweepProvenance(StrictModel):
    """Frozen provenance for deterministic W40 sequence construction."""

    engine: Literal[
        "W40_BRANCH_PRESERVING_ANGLE_SWEEP"
    ] = "W40_BRANCH_PRESERVING_ANGLE_SWEEP"

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
    ) -> "MotionSweepProvenance":
        if self.formula_ids:
            raise ValueError(
                "W40 motion provenance must not "
                "invent Formula Registry IDs"
            )

        if self.calculation_record_ids:
            raise ValueError(
                "W40 motion provenance must not "
                "invent Calculation Record IDs"
            )

        return self


class MotionSegmentResult(StrictModel):
    """One validated contiguous one-direction motion segment."""

    version: Literal[1] = 1

    direction: MotionDirection

    reference_branch: ReferenceBranch

    reference_angle_deg: DegreeParameter

    requested_angle_count: int = Field(
        gt=0
    )

    samples: list[MotionSample] = Field(
        min_length=1
    )

    termination: MotionTermination

    provenance: MotionSweepProvenance = Field(
        default_factory=MotionSweepProvenance
    )

    @staticmethod
    def _is_normal_selected_sample(
        sample: MotionSample,
        reference_branch: ReferenceBranch,
    ) -> bool:
        result = sample.closure_result

        return (
            result.closure_state
            == "TWO_SOLUTIONS"
            and result.selection_status
            == "SELECTED"
            and result.selected_pose is not None
            and result.selected_pose.branch
            == reference_branch
            and (
                result.provenance.branch_resolution
                == "REFERENCE_POSE"
            )
        )

    @staticmethod
    def _is_tangent_boundary(
        sample: MotionSample,
    ) -> bool:
        result = sample.closure_result

        return (
            result.closure_state
            == "TANGENT"
            and result.selection_status
            == "SELECTED"
            and result.selected_pose is not None
            and result.selected_pose.branch
            == "TANGENT"
            and (
                result.provenance.branch_resolution
                == "TANGENT_UNIQUE"
            )
        )

    @staticmethod
    def _is_no_solution_boundary(
        sample: MotionSample,
    ) -> bool:
        result = sample.closure_result

        return (
            result.closure_state
            == "NO_SOLUTION"
            and result.selected_pose is None
        )

    @staticmethod
    def _is_degenerate_boundary(
        sample: MotionSample,
    ) -> bool:
        result = sample.closure_result

        return (
            result.closure_state
            == "DEGENERATE"
            and result.selected_pose is None
        )

    @model_validator(mode="after")
    def validate_segment(
        self,
    ) -> "MotionSegmentResult":
        if self.reference_branch not in {
            "POSITIVE",
            "NEGATIVE",
        }:
            raise ValueError(
                "motion segment reference branch must be "
                "POSITIVE or NEGATIVE"
            )

        reference_angle = float(
            self.reference_angle_deg.value
        )

        if not math.isfinite(reference_angle):
            raise ValueError(
                "motion segment reference angle must be finite"
            )

        if len(self.samples) > self.requested_angle_count:
            raise ValueError(
                "processed sample count cannot exceed "
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
                "motion sample indexes must be contiguous "
                "from zero"
            )

        values = [
            float(
                sample.requested_angle_deg.value
            )
            for sample in self.samples
        ]

        if values[0] != reference_angle:
            raise ValueError(
                "first motion sample must equal "
                "the segment reference angle"
            )

        for previous, current in zip(
            values,
            values[1:],
        ):
            if self.direction == "INCREASING":
                if not current > previous:
                    raise ValueError(
                        "INCREASING result samples must "
                        "remain strictly increasing"
                    )

            elif self.direction == "DECREASING":
                if not current < previous:
                    raise ValueError(
                        "DECREASING result samples must "
                        "remain strictly decreasing"
                    )

        first = self.samples[0]

        if not self._is_normal_selected_sample(
            first,
            self.reference_branch,
        ):
            raise ValueError(
                "first motion sample must be a selected "
                "TWO_SOLUTIONS reference pose"
            )

        # No ambiguous TWO_SOLUTIONS sample may enter
        # a valid continuous segment.
        for sample in self.samples:
            result = sample.closure_result

            if (
                result.closure_state
                == "TWO_SOLUTIONS"
                and result.selection_status
                == "BRANCH_AMBIGUOUS"
            ):
                raise ValueError(
                    "ambiguous TWO_SOLUTIONS is invalid "
                    "inside a motion segment"
                )

            if (
                result.closure_state
                == "TWO_SOLUTIONS"
                and not self._is_normal_selected_sample(
                    sample,
                    self.reference_branch,
                )
            ):
                raise ValueError(
                    "selected TWO_SOLUTIONS sample violates "
                    "the frozen motion reference branch"
                )

        if self.termination == "COMPLETED":
            if len(self.samples) != self.requested_angle_count:
                raise ValueError(
                    "COMPLETED motion must process every "
                    "requested angle"
                )

            if not all(
                self._is_normal_selected_sample(
                    sample,
                    self.reference_branch,
                )
                for sample in self.samples
            ):
                raise ValueError(
                    "COMPLETED motion may contain only "
                    "selected TWO_SOLUTIONS samples"
                )

            return self

        final = self.samples[-1]
        preceding = self.samples[:-1]

        if not all(
            self._is_normal_selected_sample(
                sample,
                self.reference_branch,
            )
            for sample in preceding
        ):
            raise ValueError(
                "all samples before a motion boundary "
                "must be selected TWO_SOLUTIONS poses"
            )

        if self.termination == "TANGENT_BOUNDARY":
            if not self._is_tangent_boundary(
                final
            ):
                raise ValueError(
                    "TANGENT_BOUNDARY requires a final "
                    "TANGENT sample"
                )

        elif self.termination == "NO_SOLUTION_BOUNDARY":
            if not self._is_no_solution_boundary(
                final
            ):
                raise ValueError(
                    "NO_SOLUTION_BOUNDARY requires a final "
                    "NO_SOLUTION sample"
                )

        elif self.termination == "DEGENERATE_BOUNDARY":
            if not self._is_degenerate_boundary(
                final
            ):
                raise ValueError(
                    "DEGENERATE_BOUNDARY requires a final "
                    "DEGENERATE sample"
                )

        return self
