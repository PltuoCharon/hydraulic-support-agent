"""Adapt W41 synthetic candidates without changing W38/W39/W40 algorithms."""

from math import hypot, isfinite

from app.models.linkage_closure import ClosureSolverInput
from app.models.linkage_geometry import MillimetreParameter
from app.models.linkage_optimization import CandidateDesignInput, DESIGN_VARIABLE_ORDER


def build_closure_task_from_design(candidate: CandidateDesignInput) -> ClosureSolverInput:
    # Revalidate even mutable/model_construct inputs; never trust update copies.
    candidate = CandidateDesignInput.model_validate(candidate.model_dump(mode="python"))
    if candidate.case.domain != "SYNTHETIC_MATH" or candidate.case.readiness != "READY":
        raise ValueError("case is NOT_SOLVER_READY for W41 V1 evaluation")
    config = candidate.configuration
    ad = hypot(config.front_link_base.x_mm.value, config.front_link_base.y_mm.value)
    # Guard float arithmetic capacity, not engineering size or feasibility.
    lengths = [getattr(candidate.design, name).value for name in DESIGN_VARIABLE_ORDER]
    scale = max(ad, *lengths)
    if not isfinite((4 * scale) * (4 * scale)):
        raise ArithmeticError("candidate scale exceeds safe W39 float arithmetic capacity")
    spacing = MillimetreParameter(
        value=ad, unit="mm", origin="CALCULATED", evidence_status="PARTIAL",
        source_text="W41-D3 fixed A/D Euclidean spacing; source coordinates retained in candidate",
        formula_ids=[], calculation_record_ids=[],
    )
    return ClosureSolverInput(
        **{name: getattr(candidate.design, name).model_copy(deep=True)
           for name in DESIGN_VARIABLE_ORDER},
        rear_link_base=config.rear_link_base.model_copy(deep=True),
        front_link_base=config.front_link_base.model_copy(deep=True),
        base_pivot_spacing_mm=spacing,
        rear_link_angle_deg=config.rear_link_angle_deg.model_copy(deep=True),
        reference_branch=config.reference_branch,
        tolerance=config.tolerance.model_copy(deep=True),
    )
