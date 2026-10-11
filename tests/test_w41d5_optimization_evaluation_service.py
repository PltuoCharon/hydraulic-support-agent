"""Real synthetic W39/W40 cases; injected failures are explicitly named."""

import copy
import hashlib
import json
import math

import pytest

from app.models.linkage_evaluation import DesignEvaluationRequest
from app.models.linkage_optimization_evaluation import CandidateEvaluationRecord, ComparisonContract
from app.services import linkage_evaluation as d4
from app.services import linkage_optimization_evaluation as service
from test_w41d4_evaluation_models import parameter, request_payload


def contract(data):
    return ComparisonContract.from_request(DesignEvaluationRequest.model_validate(data))


def record(data, candidate_id="candidate-1", comparison=True):
    return service.evaluate_candidate_safely(candidate_id, data, contract(data) if comparison else None)


def test_success_and_failure_batch_records_are_independent():
    good = request_payload([0, 5], objective=True)
    bad = request_payload([0, 5], lengths=(5, 1, 1), objective=True)
    records = service.evaluate_candidates([("bad", bad), ("good", good)], contract(good))
    failure, success = records
    assert failure.outcome == "NO_SOLUTION" and failure.error is None
    assert failure.result.objective_value is None and not failure.ranking_eligible
    assert success.outcome == "FEASIBLE" and success.ranking_eligible
    success.request.candidate.design.rear_link_length_mm.value = 6
    assert failure.request.candidate.design.rear_link_length_mm.value == 5
    assert good["candidate"]["design"]["rear_link_length_mm"]["value"] == 5


@pytest.mark.parametrize("lengths,d,branch,outcome", [
    ((5, 1, 1), (8, 0), "POSITIVE", "NO_SOLUTION"),
    ((5, 2, 2), (5, 0), "POSITIVE", "DEGENERATE"),
    ((5, 5, 5), (8, 0), None, "BRANCH_UNRESOLVED"),
    ((5, 1, 2), (8, 0), "POSITIVE", "FEASIBLE"),
])
def test_real_single_pose_semantics(lengths, d, branch, outcome):
    actual = record(request_payload(lengths=lengths, d=d, branch=branch), comparison=False)
    assert actual.outcome == outcome and actual.error is None
    assert actual.result.closure_result is not None
    assert actual.coverage.requested_count == actual.coverage.recorded_count == 1
    assert actual.coverage.recorded_ratio == 1.0
    assert not actual.objective_computed and not actual.ranking_eligible


@pytest.mark.parametrize("bad", ["unit", "missing", "string", "infinite", "overflow_integer", "bounds", "json_duplicate", "unsupported"])
def test_invalid_input_is_recorded_and_next_candidate_runs(bad):
    good = request_payload([0, 5], objective=True)
    data = copy.deepcopy(good)
    if bad == "unit": data["plan"]["angle_samples_deg"][1]["unit"] = "radian"
    elif bad == "missing": del data["objective"]
    elif bad == "string": data["candidate"]["design"]["rear_link_length_mm"]["value"] = "5"
    elif bad == "infinite": data["candidate"]["design"]["rear_link_length_mm"]["value"] = math.inf
    elif bad == "overflow_integer": data["candidate"]["design"]["rear_link_length_mm"]["value"] = 10 ** 400
    elif bad == "bounds": data["candidate"]["design"]["rear_link_length_mm"]["value"] = 100
    elif bad == "json_duplicate": data = '{"objective":null,"objective":null}'
    else: data = []
    failed, successful = service.evaluate_candidates([("bad", data), ("good", good)], contract(good))
    assert failed.outcome == failed.error.code == "INVALID_INPUT"
    assert failed.error.stage == "INPUT_VALIDATION"
    assert failed.request is None and failed.result is None
    assert failed.coverage.recorded_count is None and failed.coverage.recorded_ratio is None
    assert successful.ranking_eligible
    assert CandidateEvaluationRecord.model_validate_json(failed.model_dump_json()) == failed


def test_real_arithmetic_capacity_error():
    # Real existing W41-D3 adapter guard, not injected numerical failure.
    data = request_payload([0, 5], objective=True)
    for name in data["candidate"]["design"]:
        data["candidate"]["design"][name]["value"] = 1e308
        data["candidate"]["bounds"][name]["upper"]["value"] = 1.1e308
    actual = record(data)
    assert actual.outcome == "NUMERICAL_ERROR"
    assert actual.error.exception_type == "ArithmeticError"
    assert actual.error.stage == "EVALUATOR_EXECUTION"
    assert actual.request is not None and actual.result is None
    assert actual.coverage.requested_count == 2
    assert actual.coverage.recorded_count is None


@pytest.mark.parametrize("exception", [ValueError("private-token"), RuntimeError("private-token"),
                                     TimeoutError("private-token")])
def test_injected_internal_exception_is_conservative_and_batch_continues(monkeypatch, exception):
    original = d4.evaluate_design
    calls = 0

    def injected(request):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise exception
        return original(request)

    monkeypatch.setattr(d4, "evaluate_design", injected)
    data = request_payload([0, 5], objective=True)
    failed, successful = service.evaluate_candidates([("bad", data), ("good", data)], contract(data))
    assert failed.outcome == "SERVICE_ERROR"
    assert failed.error.exception_type == type(exception).__name__
    assert failed.request is not None and failed.result is None
    assert failed.coverage.recorded_ratio is None
    assert "private-token" not in failed.model_dump_json()
    assert failed.timeout.status == "NOT_IMPLEMENTED" and not failed.timeout.can_interrupt
    assert successful.ranking_eligible


def test_injected_internal_result_validation_error_is_not_input_error(monkeypatch):
    data = request_payload([0, 5], objective=True)

    def injected(request):
        return original.model_copy(update={"objective_value": 123.0})

    original = d4.evaluate_design(DesignEvaluationRequest.model_validate(data))
    monkeypatch.setattr(d4, "evaluate_design", injected)
    actual = record(data)
    assert actual.outcome == "SERVICE_ERROR" and actual.error.exception_type == "ValidationError"
    assert actual.result is None


@pytest.mark.parametrize("signal", [KeyboardInterrupt(), SystemExit(2), MemoryError()])
def test_injected_process_or_resource_failure_propagates(monkeypatch, signal):
    def injected(request):
        raise signal
    monkeypatch.setattr(d4, "evaluate_design", injected)
    with pytest.raises(type(signal)) as caught:
        record(request_payload([0, 5], objective=True))
    assert caught.value is signal


def test_d4_direct_call_still_propagates_original_exception(monkeypatch):
    error = ValueError("injected solver failure")
    def injected(task):
        raise error
    monkeypatch.setattr(d4, "solve_closure", injected)
    data = request_payload([0, 5], objective=True)
    assert record(data).outcome == "SERVICE_ERROR"
    with pytest.raises(ValueError) as caught:
        d4.evaluate_design(DesignEvaluationRequest.model_validate(data))
    assert caught.value is error


def test_no_objective_or_no_comparison_contract_cannot_rank():
    without_objective = record(request_payload([0, 5]), comparison=False)
    without_contract = record(request_payload([0, 5], objective=True), comparison=False)
    assert without_objective.result.objective_value is None and not without_objective.ranking_eligible
    assert without_contract.objective_computed and not without_contract.ranking_eligible
    for actual in (without_objective, without_contract):
        with pytest.raises(ValueError): service.assert_comparison_compatible([actual])


def test_real_finite_zero_objective_can_compare():
    # Distinct explicit angles whose Cx rounds to the same finite float.
    # This is a discrete synthetic objective, not engineering zero-motion proof.
    actual = record(request_payload([0, 1e-16], objective=True))
    assert actual.result.objective_value == 0.0
    assert actual.objective_computed and actual.ranking_eligible
    service.assert_comparison_compatible([actual])


def test_different_design_lengths_are_compatible():
    first = request_payload([0, 5], objective=True)
    second = request_payload([0, 5], lengths=(5, 6, 5), objective=True)
    records = service.evaluate_candidates([("a", first), ("b", second)], contract(first))
    assert all(r.ranking_eligible for r in records)
    service.assert_comparison_compatible(records)


@pytest.mark.parametrize("change", ["angles", "direction", "branch", "tolerance", "fixed_base", "case", "bounds", "source"])
def test_different_conditions_refuse_comparison(change):
    first = request_payload([0, 5], objective=True)
    other = copy.deepcopy(first)
    config = other["candidate"]["configuration"]
    if change == "angles": other["plan"]["angle_samples_deg"][1]["value"] = 6
    elif change == "direction":
        other["plan"]["direction"] = "DECREASING"
        other["plan"]["angle_samples_deg"][1]["value"] = -5
    elif change == "branch": config["reference_branch"] = "NEGATIVE"
    elif change == "tolerance": config["tolerance"]["relative"] = 1e-11
    elif change == "fixed_base": config["front_link_base"]["x_mm"]["value"] = 7
    elif change == "case":
        other["case"]["case_id"] = other["candidate"]["case"]["case_id"] = "SM-002"
    elif change == "bounds": other["candidate"]["bounds"]["rear_link_length_mm"]["upper"]["value"] = 21
    else: other["plan"]["source_text"] = "different declared source"
    mismatched = service.evaluate_candidate_safely("other", other, contract(first))
    assert mismatched.objective_computed and not mismatched.ranking_eligible
    assert mismatched.comparison_status == "INCOMPATIBLE"
    # Even independently eligible records with separate contracts cannot be compared.
    with pytest.raises(ValueError): service.assert_comparison_compatible([record(first), record(other)])


@pytest.mark.parametrize("boundary", ["TANGENT", "NO_SOLUTION", "DEGENERATE"])
def test_real_early_boundaries_preserve_results_and_coverage(boundary):
    tangent = math.degrees(math.acos(-11 / 80))
    if boundary == "TANGENT": data = request_payload([0, 30, tangent, 120], objective=True)
    elif boundary == "NO_SOLUTION": data = request_payload([0, 30, 120, 130], objective=True)
    else:
        data = request_payload([0, 10, 20], lengths=(5, 2, 2),
                               d=(5 * math.cos(math.radians(10)), 5 * math.sin(math.radians(10))), objective=True)
    actual = record(data)
    assert actual.result == d4.evaluate_design(DesignEvaluationRequest.model_validate(data))
    assert actual.outcome == ("FULL_MOTION_INFEASIBLE" if boundary == "TANGENT" else boundary)
    assert actual.error is None and actual.full_motion_infeasible
    assert actual.coverage.recorded_count == len(actual.result.motion_result.samples)
    assert actual.coverage.regular_selected_count == actual.coverage.recorded_count - 1
    assert actual.coverage.recorded_ratio < 1
    assert actual.result.objective_value is None and actual.result.metrics == []
    assert not actual.ranking_eligible


def test_last_tangent_has_full_recorded_ratio_but_is_infeasible():
    actual = record(request_payload([0, math.degrees(math.acos(-11 / 80))], objective=True))
    assert actual.coverage.recorded_ratio == 1
    assert actual.coverage.regular_selected_count == 1
    assert actual.outcome == "FULL_MOTION_INFEASIBLE" and not actual.ranking_eligible


@pytest.mark.parametrize("lengths,d,outcome", [((5, 1, 1), (8, 0), "NO_SOLUTION"),
                                           ((5, 2, 2), (5, 0), "DEGENERATE"),
                                           ((5, 1, 2), (8, 0), "FULL_MOTION_INFEASIBLE")])
def test_first_pose_failure_records_one_real_attempt(monkeypatch, lengths, d, outcome):
    def forbidden(*args):
        raise AssertionError("W40 must not run")
    monkeypatch.setattr(d4, "sweep_rear_link_angles", forbidden)
    actual = record(request_payload([0, 5, 10], lengths=lengths, d=d, objective=True))
    assert actual.outcome == outcome and actual.result.motion_result is None
    assert actual.coverage.requested_count == 3 and actual.coverage.recorded_count == 1
    assert actual.coverage.regular_selected_count == 0
    assert actual.coverage.recorded_ratio == 1 / 3


def test_er001_no_solver_and_no_source_upgrade(monkeypatch):
    def forbidden(*args):
        raise AssertionError("engineering case must not solve")
    for name in ("build_closure_task_from_design", "solve_closure", "sweep_rear_link_angles"):
        monkeypatch.setattr(d4, name, forbidden)
    data = dict(case=dict(domain="ENGINEERING_REFERENCE", case_id="ER-001",
                          readiness="NOT_SOLVER_READY", source_text="Declared engineering source"), objective=None)
    actual = record(data, comparison=False)
    assert actual.outcome == "NOT_SOLVER_READY" and actual.error is None
    assert actual.result.execution_status == "NOT_RUN"
    assert actual.coverage.recorded_count == actual.coverage.regular_selected_count == 0
    assert actual.coverage.requested_count is None and actual.coverage.recorded_ratio is None
    assert not actual.request.case.engineering_verified
    assert actual.source_assessment == "NOT_INDEPENDENTLY_VERIFIED"


def test_engineering_ready_or_relabel_is_invalid_input():
    for domain, readiness in (("ENGINEERING_REFERENCE", "READY"), ("SYNTHETIC_MATH", "NOT_SOLVER_READY")):
        data = dict(case=dict(domain=domain, case_id="ER-001", readiness=readiness,
                              source_text="Unverified declaration"), objective=None)
        assert record(data, comparison=False).outcome == "INVALID_INPUT"


@pytest.mark.parametrize("representation", ["mapping", "typed", "json"])
def test_input_result_contract_snapshots_and_roundtrip(representation):
    data = request_payload([0, 5], objective=True)
    typed = DesignEvaluationRequest.model_validate(data)
    comparison = contract(data)
    original = d4.evaluate_design(typed)
    raw = {"mapping": data, "typed": typed, "json": json.dumps(data)}[representation]
    actual = service.evaluate_candidate_safely("a", raw, comparison)
    assert actual.result == original
    assert CandidateEvaluationRecord.model_validate_json(actual.model_dump_json()) == actual
    assert actual.input_trace.sha256 is not None
    actual.request.candidate.design.rear_link_length_mm.value = 6
    actual.comparison_contract.plan.source_text = "modified snapshot"
    assert actual.result.request.candidate.design.rear_link_length_mm.value == 5
    assert typed.candidate.design.rear_link_length_mm.value == 5
    assert comparison.plan.source_text != "modified snapshot"
    assert data["candidate"]["design"]["rear_link_length_mm"]["value"] == 5


def test_invalid_input_diagnostics_do_not_persist_secret():
    data = request_payload([0, 5], objective=True)
    data["private-token"] = "do-not-persist"
    actual = record(data, comparison=False)
    serialized = actual.model_dump_json()
    assert actual.outcome == "INVALID_INPUT" and actual.input_trace.sha256 is not None
    assert "private-token" not in serialized and "do-not-persist" not in serialized


def test_duplicate_batch_ids_and_bad_metadata_raise_before_evaluation(monkeypatch):
    def forbidden(*args):
        raise AssertionError("must reject metadata before evaluation")
    monkeypatch.setattr(d4, "evaluate_design", forbidden)
    data = request_payload([0, 5], objective=True)
    with pytest.raises(ValueError): service.evaluate_candidates([("same", data), ("same", data)])
    with pytest.raises(ValueError): service.evaluate_candidates([("valid", data), ("invalid id", data)])


def test_invalid_or_mutated_comparison_contract_is_not_candidate_error():
    data = request_payload([0, 5], objective=True)
    comparison = contract(data)
    comparison.configuration.tolerance.relative = -1
    with pytest.raises(ValueError): service.evaluate_candidate_safely("a", data, comparison)


def test_synthetic_provenance_and_undefined_violation_are_preserved():
    actual = record(request_payload([0, 5], objective=True))
    assert actual.result.closure_result.provenance.branch_resolution == "REFERENCE_POSE"
    assert actual.result.closure_result.provenance.evidence_status == "PARTIAL"
    assert not actual.request.case.engineering_verified
    assert actual.source_assessment == "NOT_INDEPENDENTLY_VERIFIED"
    assert actual.constraint_violation_status == "UNDEFINED"
    assert actual.constraint_violation_value is None


def test_mutated_typed_input_is_independently_revalidated():
    request = DesignEvaluationRequest.model_validate(request_payload([0, 5], objective=True))
    request.candidate.design.rear_link_length_mm.value = -1
    actual = service.evaluate_candidate_safely("mutated", request)
    assert actual.outcome == "INVALID_INPUT" and actual.request is None


def test_mutated_typed_input_does_not_leak_serialization_warning(recwarn, capsys):
    request = DesignEvaluationRequest.model_validate(request_payload([0, 5], objective=True))
    request.candidate.design.rear_link_length_mm.value = "private-token"
    actual = service.evaluate_candidate_safely("mutated", request)
    assert actual.outcome == "INVALID_INPUT"
    assert not recwarn.list
    output = capsys.readouterr()
    assert not output.out and not output.err
    assert "private-token" not in actual.model_dump_json()


def test_injected_external_result_snapshot_is_independent(monkeypatch):
    data = request_payload([0, 5], objective=True)
    external = d4.evaluate_design(DesignEvaluationRequest.model_validate(data))
    monkeypatch.setattr(d4, "evaluate_design", lambda request: external)
    actual = record(data)
    external.request.candidate.design.rear_link_length_mm.value = 7
    assert actual.result.request.candidate.design.rear_link_length_mm.value == 5
    assert actual.request.candidate.design.rear_link_length_mm.value == 5


@pytest.mark.parametrize("surrogate", ["\ud800", "\udfff"])
def test_unencodable_json_trace_does_not_abort_batch(surrogate, capsys, recwarn):
    bad_json = '{"unexpected":"' + surrogate + '","private-token":"do-not-persist"}'
    good = request_payload([0, 5], objective=True)
    failed, later, successful = service.evaluate_candidates([
        ("unicode_bad", bad_json), ("later_invalid", {}), ("valid", good),
    ], contract(good))
    assert failed.outcome == failed.error.code == "INVALID_INPUT"
    assert failed.error.stage == "INPUT_VALIDATION"
    assert failed.input_trace.representation == "JSON_TEXT"
    assert failed.input_trace.sha256 is None
    assert failed.request is None and failed.result is None
    assert later.candidate_id == "later_invalid" and later.outcome == "INVALID_INPUT"
    assert successful.ranking_eligible
    assert successful.result == d4.evaluate_design(DesignEvaluationRequest.model_validate(good))
    serialized = failed.model_dump_json()
    assert bad_json not in serialized and surrogate not in serialized
    assert "private-token" not in serialized and "do-not-persist" not in serialized
    assert "surrogates not allowed" not in serialized
    assert CandidateEvaluationRecord.model_validate_json(serialized) == failed
    output = capsys.readouterr()
    assert not output.out and not output.err and not recwarn.list


def test_normal_utf8_json_trace_preserves_original_sha256():
    data = request_payload([0, 5], objective=True)
    data["plan"]["source_text"] = "正常 UTF-8 来源：液压支架 🛠"
    raw = json.dumps(data, ensure_ascii=False)
    actual = service.evaluate_candidate_safely("utf8", raw, contract(data))
    assert actual.input_trace.representation == "JSON_TEXT"
    assert actual.input_trace.sha256 == hashlib.sha256(raw.encode("utf-8")).hexdigest()
    assert actual.ranking_eligible


@pytest.mark.parametrize("signal", [KeyboardInterrupt(), SystemExit(2), MemoryError()])
def test_json_trace_encoding_does_not_swallow_system_failure(signal):
    class FailingText(str):
        def encode(self, *args, **kwargs):
            raise signal

    with pytest.raises(type(signal)) as caught:
        service.evaluate_candidate_safely("signal", FailingText("{}"))
    assert caught.value is signal
