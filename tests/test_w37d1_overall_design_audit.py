from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w37/W37D1_overall_design_system_audit.md"
REGISTRY = ROOT / "docs/evidence/formulas/W34D2_Formula_Registry.csv"
CALC_ROUTER = ROOT / "app/routers/calc.py"
RECORDS = ROOT / "app/services/calculation_records.py"
TRANSFER = ROOT / "web/src/utils/designTransfer.js"


def test_w37d1_audit_document_exists_and_freezes_scope():
    text = DOC.read_text(encoding="utf-8")

    assert "W37-D1 Overall Design System Audit" in text
    assert "OverallSupportDesign" in text
    assert "hs.designTransfer.v1" in text
    assert "hs.overallDesign.v1" in text
    assert "canopy_len" in text
    assert "Ks" in text
    assert "eta" in text


def test_required_resistance_core_is_not_yet_wired_into_calc_router():
    text = CALC_ROUTER.read_text(encoding="utf-8")

    assert "required_resistance" not in text
    assert "/q-need" in text
    assert "/column-design" in text
    assert "/push-jack-design" in text


def test_registry_has_no_jack_or_valve_formula_ids_yet():
    with REGISTRY.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    ids = {row["formula_id"] for row in rows}

    assert not any(x.startswith("F-JACK-") for x in ids)
    assert not any(x.startswith("F-VALVE-") for x in ids)


def test_calculation_record_scope_remains_column_design_only():
    text = RECORDS.read_text(encoding="utf-8")

    assert 'ALLOWED_CALC_TYPES = {"column_design"}' in text


def test_design_transfer_remains_the_existing_lightweight_contract():
    text = TRANSFER.read_text(encoding="utf-8")

    assert 'hs.designTransfer.v1' in text
    assert '"selected_support"' in text
    assert '"calculated_requirement"' in text
    assert "hs.overallDesign.v1" not in text
