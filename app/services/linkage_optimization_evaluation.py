"""Thin W41-D5 batch boundary around the unchanged D4 evaluator."""

import hashlib
import json
import re
from collections.abc import Iterable
from copy import deepcopy

from app.models.linkage_evaluation import AngleSweepPlan, DesignEvaluationRequest, DesignEvaluationResult
from app.models.linkage_optimization_evaluation import (
    CandidateEvaluationRecord, ComparisonContract, EvaluationError, InputTrace,
    comparison_status, mathematical_outcome, sampling_coverage,
)
from app.services import linkage_evaluation


def _trace(raw) -> InputTrace:
    if isinstance(raw, DesignEvaluationRequest):
        kind = "TYPED_REQUEST"
        try:
            data = raw.model_dump(mode="python", warnings=False)
        except (TypeError, ValueError, RecursionError):
            return InputTrace(representation=kind)
    elif isinstance(raw, dict):
        kind, data = "MAPPING", raw
    elif isinstance(raw, str):
        try:
            encoded = raw.encode("utf-8")
        except UnicodeEncodeError:
            # A trace failure must not bypass the formal input validation stage.
            return InputTrace(representation="JSON_TEXT")
        return InputTrace(representation="JSON_TEXT", sha256=hashlib.sha256(encoded).hexdigest())
    else:
        return InputTrace(representation="UNSUPPORTED")
    try:
        encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    except (TypeError, ValueError, RecursionError):
        # Unsupported nested objects have no trustworthy canonical digest.
        return InputTrace(representation=kind)
    return InputTrace(representation=kind, sha256=hashlib.sha256(encoded).hexdigest())


def _error(error: Exception, *, input_stage: bool) -> EvaluationError:
    name = type(error).__name__
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,99}", name):
        name = "Exception"
    if input_stage:
        code, diagnostic = "INVALID_INPUT", "INPUT_VALIDATION_FAILED"
    elif isinstance(error, ArithmeticError):
        code, diagnostic = "NUMERICAL_ERROR", "ARITHMETIC_EXCEPTION_DURING_EVALUATION"
    else:
        code, diagnostic = "SERVICE_ERROR", "INTERNAL_EVALUATION_EXCEPTION"
    # Never persist str(error), traceback, validation input values or raw payload.
    return EvaluationError(
        code=code, stage="INPUT_VALIDATION" if input_stage else "EVALUATOR_EXECUTION",
        exception_type=name, diagnostic=diagnostic,
    )


def evaluate_candidate_safely(
    candidate_id: str, raw_request,
    comparison_contract: ComparisonContract | None = None,
) -> CandidateEvaluationRecord:
    """Record candidate-local exceptions. Invalid caller metadata still raises.

    Accepted input: dict, JSON text (duplicate keys rejected), or typed request.
    No timeout is enforced. BaseException termination signals always propagate.
    """
    if not isinstance(candidate_id, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", candidate_id):
        raise ValueError("candidate_id must be a non-sensitive identifier")
    contract = (ComparisonContract.model_validate(comparison_contract.model_dump(mode="python"))
                if comparison_contract is not None else None)
    trace = _trace(raw_request)
    request, result, error = None, None, None
    try:
        if isinstance(raw_request, str):
            request = DesignEvaluationRequest.model_validate_json(raw_request)
        elif isinstance(raw_request, DesignEvaluationRequest):
            request = DesignEvaluationRequest.model_validate(
                raw_request.model_dump(mode="python", warnings=False))
        elif isinstance(raw_request, dict):
            request = DesignEvaluationRequest.model_validate(deepcopy(raw_request))
        else:
            raise TypeError("unsupported request representation")
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        error = _error(exc, input_stage=True)
    if request is not None:
        try:
            # Give D4 a separate object, retaining the independent input snapshot.
            actual = linkage_evaluation.evaluate_design(request.model_copy(deep=True))
            result = DesignEvaluationResult.model_validate(actual.model_dump(mode="python"))
            if result.request != request:
                raise ValueError("evaluator returned a different request")
        except Exception as exc:
            # Internal ValueError/ValidationError are not input failures.
            # Memory exhaustion is not a recoverable candidate-local failure.
            if isinstance(exc, MemoryError):
                raise
            result = None
            error = _error(exc, input_stage=False)
    compared = comparison_status(request, contract)
    computed = result is not None and result.objective_status == "COMPUTED"
    record = CandidateEvaluationRecord(
        candidate_id=candidate_id, input_trace=trace, request=request, result=result, error=error,
        outcome=mathematical_outcome(result) if result is not None else error.code,
        full_motion_infeasible=(result is not None and isinstance(request.plan, AngleSweepPlan)
                                and result.feasibility_status == "INFEASIBLE"),
        objective_computed=computed, comparison_contract=contract, comparison_status=compared,
        ranking_eligible=(computed and result.feasibility_status == "FEASIBLE" and compared == "COMPATIBLE"),
        coverage=sampling_coverage(request, result),
    )
    return CandidateEvaluationRecord.model_validate(record.model_dump(mode="python"))


def evaluate_candidates(
    candidates: Iterable[tuple[str, object]],
    comparison_contract: ComparisonContract | None = None,
) -> list[CandidateEvaluationRecord]:
    """Evaluate in input order; duplicate identifiers and invalid contracts raise."""
    items = list(candidates)
    ids = [candidate_id for candidate_id, _ in items]
    if any(not isinstance(i, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", i) for i in ids):
        raise ValueError("candidate_id must be a non-sensitive identifier")
    if len(set(ids)) != len(ids):
        raise ValueError("batch candidate identifiers must be unique")
    contract = (ComparisonContract.model_validate(comparison_contract.model_dump(mode="python"))
                if comparison_contract is not None else None)
    return [evaluate_candidate_safely(i, raw, contract) for i, raw in items]


def assert_comparison_compatible(records: Iterable[CandidateEvaluationRecord]) -> None:
    """Refuse automatic comparison unless every supplied record is eligible."""
    snapshots = [CandidateEvaluationRecord.model_validate(r.model_dump(mode="python")) for r in records]
    if not snapshots or any(not r.ranking_eligible for r in snapshots):
        raise ValueError("comparison requires eligible records and an explicit contract")
    first = snapshots[0].comparison_contract
    if any(r.comparison_contract != first for r in snapshots[1:]):
        raise ValueError("records use different comparison conditions")
