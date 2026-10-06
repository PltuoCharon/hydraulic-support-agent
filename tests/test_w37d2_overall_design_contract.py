from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w37/W37D2_overall_design_contract.md"
EXAMPLE = ROOT / "docs/evidence/w37/overall_design_v1.example.json"
TRANSFER = ROOT / "web/src/utils/designTransfer.js"


def test_w37d2_contract_freezes_identity_and_origin_types():
    text = DOC.read_text(encoding="utf-8")

    assert "hs.overallDesign.v1" in text

    for value in (
        "RETRIEVED",
        "CALCULATED",
        "USER_INPUT",
        "AI_PROPOSED",
    ):
        assert value in text


def test_w37d2_keeps_origin_and_evidence_status_separate():
    text = DOC.read_text(encoding="utf-8")

    assert "VERIFIED" in text
    assert "PARTIAL" in text
    assert "EVIDENCE_GAP" in text
    assert "NOT_APPLICABLE" in text

    assert "origin and engineering/evidence status are independent" in text


def test_w37d2_preserves_geometry_semantics():
    text = DOC.read_text(encoding="utf-8")

    assert "support_length_parameter_m" in text
    assert "control_width_m means verified Bc" in text
    assert "Historical canopy_len shall not become top_beam.length automatically" in text


def test_w37d2_preserves_ks_eta_boundary():
    text = DOC.read_text(encoding="utf-8")

    assert "Ks is not historical column eta" in text
    assert "eta is not Ks" in text


def test_example_has_required_top_level_sections():
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    assert data["version"] == 1

    required = {
        "metadata",
        "working_condition",
        "reference_support",
        "support_requirement",
        "overall_parameters",
        "hydraulic_components",
        "linkage",
        "structure",
        "analyses",
        "provenance",
        "status",
    }

    assert required.issubset(data)


def test_unimplemented_modules_are_explicit_not_fabricated():
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    assert data["hydraulic_components"]["valve"]["status"] == "NOT_IMPLEMENTED"
    assert data["hydraulic_components"]["pipeline"]["status"] == "NOT_IMPLEMENTED"
    assert data["hydraulic_components"]["pump_station"]["status"] == "NOT_IMPLEMENTED"
    assert data["linkage"]["status"] == "NOT_IMPLEMENTED"
    assert data["structure"]["status"] == "NOT_IMPLEMENTED"
    assert data["analyses"]["status"] == "NOT_IMPLEMENTED"


def test_existing_design_transfer_contract_is_not_replaced():
    text = TRANSFER.read_text(encoding="utf-8")

    assert 'hs.designTransfer.v1' in text
    assert 'hs.overallDesign.v1' not in text
