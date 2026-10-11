import json

import pytest
from pydantic import ValidationError

from app.models.linkage_optimization import (
    CandidateDesignInput, DESIGN_VARIABLE_ORDER, DesignCase,
    FourBarDesignVector,
)


def parameter(value, unit="mm"):
    return dict(value=value, unit=unit, origin="USER_INPUT",
                evidence_status="PARTIAL", source_text="Synthetic test fixture only")


def payload():
    return dict(
        case=dict(domain="SYNTHETIC_MATH", case_id="SM-001", readiness="READY",
                  source_text="W39 synthetic benchmark"),
        design={name: parameter(5) for name in DESIGN_VARIABLE_ORDER},
        bounds=dict(domain="SYNTHETIC_MATH", **{
            name: dict(lower=parameter(0.1), upper=parameter(20))
            for name in DESIGN_VARIABLE_ORDER}),
        configuration=dict(front_link_base=dict(x_mm=parameter(8), y_mm=parameter(0)),
                           rear_link_angle_deg=parameter(0, "degree"),
                           reference_branch=None,
                           tolerance=dict(absolute_mm=1e-9, relative=1e-12)),
    )


def test_order_units_and_provenance_round_trip():
    candidate = CandidateDesignInput.model_validate(payload())
    assert candidate.design.as_vector() == (5, 5, 5)
    assert tuple(FourBarDesignVector.model_fields) == DESIGN_VARIABLE_ORDER
    assert candidate.design.rear_link_length_mm.unit == "mm"
    assert candidate.design.rear_link_length_mm.origin == "USER_INPUT"
    assert candidate.design.rear_link_length_mm.evidence_status == "PARTIAL"
    assert CandidateDesignInput.from_json(candidate.model_dump_json()) == candidate


@pytest.mark.parametrize("value", [None, True, False, "5", 0, -1, float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("name", DESIGN_VARIABLE_ORDER)
def test_bad_lengths(name, value):
    data = payload()
    data["design"][name]["value"] = value
    with pytest.raises((ValidationError, ValueError)):
        CandidateDesignInput.model_validate(data)


@pytest.mark.parametrize("change", ["missing", "extra", "unit", "source", "origin", "evidence"])
def test_vector_contract_rejection(change):
    data = payload()["design"]
    if change == "missing":
        del data[DESIGN_VARIABLE_ORDER[0]]
    elif change == "extra":
        data["AB"] = parameter(5)
    else:
        key, value = {"unit": ("unit", "m"), "source": ("source_text", " "),
                      "origin": ("origin", "UNKNOWN"),
                      "evidence": ("evidence_status", "READY")}[change]
        data[DESIGN_VARIABLE_ORDER[0]][key] = value
    with pytest.raises(ValueError):
        FourBarDesignVector.model_validate(data)


def test_duplicate_json_rejected():
    data = json.dumps(payload()["design"])
    duplicate = data[:-1] + ', "rear_link_length_mm": ' + json.dumps(parameter(6)) + '}'
    with pytest.raises(ValueError, match="duplicate"):
        FourBarDesignVector.from_json(duplicate)


@pytest.mark.parametrize("lower,upper,value", [(5, 5, 5), (6, 5, 5), (0, 5, 3), (1, 4, 5), (6, 9, 5), ("1", 9, 5)])
def test_bounds_rejection(lower, upper, value):
    data = payload()
    name = DESIGN_VARIABLE_ORDER[0]
    data["bounds"][name] = dict(lower=parameter(lower), upper=parameter(upper))
    data["design"][name] = parameter(value)
    with pytest.raises(ValueError):
        CandidateDesignInput.model_validate(data)


@pytest.mark.parametrize("value", [0.1, 20])
def test_inclusive_bounds(value):
    data = payload()
    data["design"][DESIGN_VARIABLE_ORDER[0]] = parameter(value)
    CandidateDesignInput.model_validate(data)


@pytest.mark.parametrize("change", ["ready", "verified", "relabel", "mixed"])
def test_engineering_gate(change):
    data = payload()
    data["case"].update(domain="ENGINEERING_REFERENCE", case_id="ER-001", readiness="NOT_SOLVER_READY")
    data["bounds"]["domain"] = "ENGINEERING_REFERENCE"
    if change == "ready":
        data["case"]["readiness"] = "READY"
    elif change == "verified":
        data["case"]["engineering_verified"] = True
    elif change == "relabel":
        data["case"]["domain"] = "SYNTHETIC_MATH"
    else:
        data["bounds"]["domain"] = "SYNTHETIC_MATH"
    with pytest.raises(ValueError):
        CandidateDesignInput.model_validate(data)


def test_unready_engineering_record_needs_no_geometry():
    case = DesignCase(domain="ENGINEERING_REFERENCE", case_id="ER-001",
                      readiness="NOT_SOLVER_READY", source_text="W39 evidence gap")
    assert not case.engineering_verified
    assert "design" not in case.model_dump()


def test_missing_unit_rejected():
    data = payload()
    data["design"][DESIGN_VARIABLE_ORDER[0]].pop("unit")
    with pytest.raises(ValueError, match="unit"):
        CandidateDesignInput.model_validate(data)


def test_standard_json_entrypoint_rejects_duplicates():
    with pytest.raises(ValueError, match="duplicate"):
        DesignCase.model_validate_json('{"domain":"SYNTHETIC_MATH","domain":"ENGINEERING_REFERENCE"}')


def test_preconstructed_parameter_is_revalidated():
    from app.models.linkage_geometry import MillimetreParameter
    data = payload()
    item = MillimetreParameter(**parameter(5))
    item.value = True
    data["design"][DESIGN_VARIABLE_ORDER[0]] = item
    with pytest.raises(ValueError):
        CandidateDesignInput.model_validate(data)
