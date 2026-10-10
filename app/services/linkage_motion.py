"""W40-D3 deterministic branch-preserving linkage motion sweep.

Boundary:
- one explicit rear-link-angle sample at a time
- reuse W39 solve_closure(...)
- preserve one frozen engineering branch
- stop at first mathematical boundary
- no support-height solving
- no top-beam propagation
- no interpolation
- no optimization
"""

from __future__ import annotations

from app.models.linkage_closure import (
    ClosureResult,
    ClosureSolverInput,
    ReferenceBranch,
)
from app.models.linkage_geometry import (
    DegreeParameter,
)
from app.models.linkage_motion import (
    MotionSample,
    MotionSegmentResult,
    MotionSweepInput,
    MotionSweepProvenance,
)
from app.services.linkage_closure import (
    solve_closure,
)


def _build_closure_task(
    *,
    reference_task: ClosureSolverInput,
    angle: DegreeParameter,
) -> ClosureSolverInput:
    """Build one fully validated W39 task for one requested angle."""

    payload = reference_task.model_dump(
        mode="python"
    )

    payload["rear_link_angle_deg"] = (
        angle.model_dump(
            mode="python"
        )
    )

    # Intentionally use full model validation instead of
    # model_copy(update=...), because Pydantic update copies
    # do not revalidate updated field values.
    return ClosureSolverInput.model_validate(
        payload
    )


def _require_normal_selected_result(
    *,
    result: ClosureResult,
    reference_branch: ReferenceBranch,
    context: str,
) -> None:
    """Require one ordinary branch-preserving TWO_SOLUTIONS pose."""

    if (
        result.closure_state
        == "TWO_SOLUTIONS"
        and result.selection_status
        == "BRANCH_AMBIGUOUS"
    ):
        raise ValueError(
            f"{context}: ambiguous TWO_SOLUTIONS "
            "is invalid in a continuous motion segment"
        )

    if result.closure_state != "TWO_SOLUTIONS":
        raise ValueError(
            f"{context}: expected a selected "
            "TWO_SOLUTIONS pose"
        )

    if result.selection_status != "SELECTED":
        raise ValueError(
            f"{context}: TWO_SOLUTIONS result "
            "must be SELECTED"
        )

    if result.selected_pose is None:
        raise ValueError(
            f"{context}: selected TWO_SOLUTIONS "
            "result requires selected_pose"
        )

    if (
        result.selected_pose.branch
        != reference_branch
    ):
        raise ValueError(
            f"{context}: selected TWO_SOLUTIONS "
            "branch does not match the frozen "
            "reference branch"
        )

    if (
        result.provenance.branch_resolution
        != "REFERENCE_POSE"
    ):
        raise ValueError(
            f"{context}: selected TWO_SOLUTIONS "
            "result requires REFERENCE_POSE "
            "branch resolution"
        )


def _validate_tangent_result(
    result: ClosureResult,
) -> None:
    """Defensively validate W39 tangent semantics."""

    if result.selection_status != "SELECTED":
        raise ValueError(
            "TANGENT boundary must be SELECTED"
        )

    if result.selected_pose is None:
        raise ValueError(
            "TANGENT boundary requires selected_pose"
        )

    if result.selected_pose.branch != "TANGENT":
        raise ValueError(
            "TANGENT boundary requires TANGENT branch"
        )

    if (
        result.provenance.branch_resolution
        != "TANGENT_UNIQUE"
    ):
        raise ValueError(
            "TANGENT boundary requires "
            "TANGENT_UNIQUE resolution"
        )


def _validate_no_solution_result(
    result: ClosureResult,
) -> None:
    """Defensively validate W39 no-solution semantics."""

    if result.selected_pose is not None:
        raise ValueError(
            "NO_SOLUTION boundary cannot have "
            "a selected pose"
        )


def _validate_degenerate_result(
    result: ClosureResult,
) -> None:
    """Defensively validate W39 degenerate semantics."""

    if result.selected_pose is not None:
        raise ValueError(
            "DEGENERATE boundary cannot have "
            "a selected pose"
        )


def sweep_rear_link_angles(
    sweep: MotionSweepInput,
) -> MotionSegmentResult:
    """Solve one contiguous branch-preserving rear-link-angle segment."""

    before = sweep.model_dump(
        mode="json"
    )

    reference_branch = (
        sweep.reference_task.reference_branch
    )

    if reference_branch not in {
        "POSITIVE",
        "NEGATIVE",
    }:
        # MotionSweepInput already enforces this.
        # Keep the service boundary explicit as well.
        raise ValueError(
            "continuous motion requires a frozen "
            "POSITIVE or NEGATIVE reference branch"
        )

    samples: list[MotionSample] = []

    termination = "COMPLETED"

    for index, requested_angle in enumerate(
        sweep.angle_samples_deg
    ):
        task = _build_closure_task(
            reference_task=sweep.reference_task,
            angle=requested_angle,
        )

        result = solve_closure(
            task
        )

        if index == 0:
            _require_normal_selected_result(
                result=result,
                reference_branch=reference_branch,
                context="first solved sample",
            )

            samples.append(
                MotionSample(
                    sample_index=index,
                    requested_angle_deg=(
                        requested_angle.model_copy(
                            deep=True
                        )
                    ),
                    closure_result=result,
                )
            )

            continue

        if result.closure_state == "TWO_SOLUTIONS":
            _require_normal_selected_result(
                result=result,
                reference_branch=reference_branch,
                context=(
                    f"motion sample {index}"
                ),
            )

            samples.append(
                MotionSample(
                    sample_index=index,
                    requested_angle_deg=(
                        requested_angle.model_copy(
                            deep=True
                        )
                    ),
                    closure_result=result,
                )
            )

            continue

        if result.closure_state == "TANGENT":
            _validate_tangent_result(
                result
            )

            samples.append(
                MotionSample(
                    sample_index=index,
                    requested_angle_deg=(
                        requested_angle.model_copy(
                            deep=True
                        )
                    ),
                    closure_result=result,
                )
            )

            termination = "TANGENT_BOUNDARY"
            break

        if result.closure_state == "NO_SOLUTION":
            _validate_no_solution_result(
                result
            )

            samples.append(
                MotionSample(
                    sample_index=index,
                    requested_angle_deg=(
                        requested_angle.model_copy(
                            deep=True
                        )
                    ),
                    closure_result=result,
                )
            )

            termination = "NO_SOLUTION_BOUNDARY"
            break

        if result.closure_state == "DEGENERATE":
            _validate_degenerate_result(
                result
            )

            samples.append(
                MotionSample(
                    sample_index=index,
                    requested_angle_deg=(
                        requested_angle.model_copy(
                            deep=True
                        )
                    ),
                    closure_result=result,
                )
            )

            termination = "DEGENERATE_BOUNDARY"
            break

        raise ValueError(
            "unsupported W39 closure state in "
            "continuous motion sweep"
        )

    motion_result = MotionSegmentResult(
        direction=sweep.direction,
        reference_branch=reference_branch,
        reference_angle_deg=(
            sweep.reference_task
            .rear_link_angle_deg
            .model_copy(
                deep=True
            )
        ),
        requested_angle_count=len(
            sweep.angle_samples_deg
        ),
        samples=samples,
        termination=termination,
        provenance=MotionSweepProvenance(),
    )

    after = sweep.model_dump(
        mode="json"
    )

    if after != before:
        raise RuntimeError(
            "W40-D3 sweep mutated MotionSweepInput"
        )

    return motion_result
