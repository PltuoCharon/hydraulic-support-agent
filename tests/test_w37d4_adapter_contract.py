from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w37/W37D4_adapter_contract.md"


def text():
    return DOC.read_text(encoding="utf-8")


def test_adapter_contract_exists():
    s = text()

    assert "W37-D4 OverallSupportDesign Adapter Contract" in s
    assert "not an engineering calculation layer" in s


def test_adapter_forbids_recalculation_and_fabrication():
    s = text()

    assert "recalculate engineering values" in s
    assert "invent missing values" in s
    assert "introduce engineering defaults" in s


def test_qneed_formula_mapping_is_frozen():
    s = text()

    for formula_id in (
        "F-QN-001",
        "F-QN-002",
        "F-QN-003",
        "F-QN-004",
    ):
        assert formula_id in s

    assert "project controlling required support intensity" in s


def test_resistance_semantics_are_frozen():
    s = text()

    assert "F-QN-005" in s
    assert "F-QN-006" in s
    assert "F-QN-007" in s

    assert "Ks shall not be mapped to historical column eta" in s
    assert "shall not derive Bc from historical canopy_len" in s


def test_column_semantics_are_frozen():
    s = text()

    assert "F-COL-001" in s
    assert "F-COL-002" in s
    assert "F-COL-003" in s

    assert "whole-support calculated capacity" in s
    assert "shall not be labelled single-column theoretical thrust" in s


def test_eta_remains_evidence_gap():
    s = text()

    assert "eta: USER_INPUT + EVIDENCE_GAP" in s
    assert "Successful column calculation does not upgrade eta to VERIFIED" in s


def test_push_jack_does_not_gain_fake_traceability():
    s = text()

    assert "shall not create F-JACK Formula IDs" in s
    assert "shall not create a push-jack Calculation Record" in s
    assert "mt_t94_verified" in s


def test_adapter_must_consume_results_not_call_calculation_core():
    s = text()

    assert "must consume result dictionaries" in s
    assert "must not call the engineering calculation cores internally" in s


def test_d4_evidence_mapping_does_not_overclaim_verification():
    s = text()

    assert "origin = CALCULATED" in s
    assert "evidence_status = PARTIAL" in s
    assert "origin = USER_INPUT" in s
    assert "evidence_status = EVIDENCE_GAP" in s
    assert "shall not mark these design values VERIFIED" in s
