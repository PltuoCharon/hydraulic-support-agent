from pathlib import Path

import pytest

from app.models.overall_design import OverallSupportDesign
from app.services.overall_design_adapters import (
    apply_q_need_result,
    apply_required_resistance_result,
)


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "app/services/overall_design_adapters.py"


def test_q_need_adapter_copies_existing_values():
    design = OverallSupportDesign()

    result = {
        "p1_mpa": 0.90,
        "p2_mpa": 0.70,
        "p3_mpa": 0.82,
        "q_need_mpa": 0.90,
        "governing": "p1",
        "rule": "三式并算取最大值",
        "source": "test source",
    }

    returned = apply_q_need_result(
        design,
        result,
    )

    assert returned is design

    req = design.support_requirement

    assert req.p1_mpa.value == 0.90
    assert req.p2_mpa.value == 0.70
    assert req.p3_mpa.value == 0.82

    assert (
        req.required_support_intensity_mpa.value
        == 0.90
    )

    assert req.governing_method == "p1"


def test_q_need_adapter_attaches_formula_trace_without_verified_overclaim():
    design = OverallSupportDesign()

    apply_q_need_result(
        design,
        {
            "p1_mpa": 0.90,
            "p2_mpa": 0.70,
            "p3_mpa": 0.82,
            "q_need_mpa": 0.90,
            "governing": "p1",
            "source": "source",
        },
    )

    req = design.support_requirement

    assert req.p1_mpa.formula_ids == ["F-QN-001"]

    assert (
        req.required_support_intensity_mpa.formula_ids
        == ["F-QN-004"]
    )

    assert (
        req.required_support_intensity_mpa.origin
        == "CALCULATED"
    )

    assert (
        req.required_support_intensity_mpa.evidence_status
        == "PARTIAL"
    )


def test_q_need_adapter_rejects_missing_required_output():
    design = OverallSupportDesign()

    with pytest.raises(ValueError):
        apply_q_need_result(
            design,
            {
                "p1_mpa": 0.90,
            },
        )


def test_resistance_adapter_copies_existing_values():
    design = OverallSupportDesign()

    result = {
        "control_area_m2": 8.75,
        "base_resistance_kn": 7875.0,
        "required_working_resistance_kn": 8750.0,
        "support_efficiency": 0.90,
        "formula_ids": [
            "F-QN-005",
            "F-QN-006",
            "F-QN-007",
        ],
        "source": "KA/T 554-1996 Appendix D",
        "note": "Bc explicit; Ks != eta",
    }

    returned = apply_required_resistance_result(
        design,
        result,
    )

    assert returned is design

    req = design.support_requirement

    assert req.control_area_m2.value == 8.75
    assert req.base_resistance_kn.value == 7875.0

    assert (
        req.required_working_resistance_kn.value
        == 8750.0
    )


def test_resistance_adapter_preserves_ks_as_user_input_evidence_gap():
    design = OverallSupportDesign()

    apply_required_resistance_result(
        design,
        {
            "control_area_m2": 8.75,
            "base_resistance_kn": 7875.0,
            "required_working_resistance_kn": 8750.0,
            "support_efficiency": 0.90,
        },
    )

    ks = (
        design.support_requirement
        .support_efficiency_ks
    )

    assert ks.value == 0.90
    assert ks.origin == "USER_INPUT"
    assert ks.evidence_status == "EVIDENCE_GAP"
    assert ks.formula_ids == []


def test_resistance_outputs_are_calculated_partial():
    design = OverallSupportDesign()

    apply_required_resistance_result(
        design,
        {
            "control_area_m2": 8.75,
            "base_resistance_kn": 7875.0,
            "required_working_resistance_kn": 8750.0,
            "support_efficiency": 0.90,
        },
    )

    req = design.support_requirement

    assert req.control_area_m2.origin == "CALCULATED"
    assert req.control_area_m2.evidence_status == "PARTIAL"

    assert (
        req.required_working_resistance_kn.formula_ids
        == ["F-QN-007"]
    )


def test_provenance_is_deduplicated():
    design = OverallSupportDesign()

    result = {
        "p1_mpa": 0.90,
        "p2_mpa": 0.70,
        "p3_mpa": 0.82,
        "q_need_mpa": 0.90,
        "governing": "p1",
        "source": "same source",
    }

    apply_q_need_result(design, result)
    apply_q_need_result(design, result)

    assert (
        design.provenance.source_texts
        == ["same source"]
    )

    assert (
        design.provenance.formula_ids.count(
            "F-QN-001"
        )
        == 1
    )


def test_adapter_module_does_not_import_engineering_cores():
    text = ADAPTER.read_text(encoding="utf-8")

    assert "from app.services.calc" not in text
    assert "import app.services.calc" not in text


def test_column_adapter_maps_existing_result_without_recalculation():
    from app.services.overall_design_adapters import (
        apply_column_design_result,
    )

    design = OverallSupportDesign()

    result = {
        "d_calc_mm": 301.2,
        "d_std_mm": 320,
        "p_actual_kn": 9626.9,
        "inputs": {
            "p_kn": 9000,
            "n": 4,
            "p_mpa": 31.5,
            "eta": 0.95,
        },
        "source": "column source",
        "record_id": 123,
    }

    apply_column_design_result(
        design,
        result,
    )

    column = design.hydraulic_components.columns

    assert column.d_calc_mm.value == 301.2
    assert column.d_std_mm.value == 320
    assert column.p_actual_kn.value == 9626.9

    assert column.formula_ids == [
        "F-COL-001",
        "F-COL-002",
    ]

    assert column.calculation_record_ids == [123]

    assert (
        design.provenance.calculation_record_ids
        == [123]
    )


def test_column_adapter_preserves_eta_evidence_gap():
    from app.services.overall_design_adapters import (
        apply_column_design_result,
    )

    design = OverallSupportDesign()

    apply_column_design_result(
        design,
        {
            "d_calc_mm": 301.2,
            "d_std_mm": 320,
            "p_actual_kn": 9626.9,
            "inputs": {
                "p_kn": 9000,
                "n": 4,
                "p_mpa": 31.5,
                "eta": 0.95,
            },
        },
    )

    eta = (
        design.hydraulic_components
        .columns.inputs["eta"]
    )

    assert eta["value"] == 0.95
    assert eta["origin"] == "USER_INPUT"
    assert eta["evidence_status"] == "EVIDENCE_GAP"


def test_column_adapter_adds_setting_ratio_formula_only_when_present():
    from app.services.overall_design_adapters import (
        apply_column_design_result,
    )

    design = OverallSupportDesign()

    apply_column_design_result(
        design,
        {
            "d_calc_mm": 301.2,
            "d_std_mm": 320,
            "p_actual_kn": 9626.9,
            "setting_ratio_pct": 70.0,
            "setting_ok": True,
            "inputs": {
                "p_kn": 9000,
                "n": 4,
                "p_mpa": 31.5,
                "eta": 0.95,
                "p_set_kn": 6300,
            },
        },
    )

    column = design.hydraulic_components.columns

    assert "F-COL-003" in column.formula_ids
    assert column.setting_ratio_pct.value == 70.0
    assert column.setting_ok.value is True


def test_column_adapter_can_preserve_upstream_working_resistance_trace():
    from app.models.overall_design import EngineeringParameter
    from app.services.overall_design_adapters import (
        apply_column_design_result,
    )

    design = OverallSupportDesign()

    upstream = EngineeringParameter(
        value=9000,
        unit="kN",
        origin="CALCULATED",
        evidence_status="PARTIAL",
        formula_ids=["F-QN-007"],
    )

    apply_column_design_result(
        design,
        {
            "d_calc_mm": 301.2,
            "d_std_mm": 320,
            "p_actual_kn": 9626.9,
            "inputs": {
                "p_kn": 9000,
                "n": 4,
                "p_mpa": 31.5,
                "eta": 0.95,
            },
        },
        p_kn_trace=upstream,
    )

    p_kn = (
        design.hydraulic_components
        .columns.inputs["p_kn"]
    )

    assert p_kn["origin"] == "CALCULATED"
    assert p_kn["formula_ids"] == ["F-QN-007"]


def test_push_jack_adapter_maps_existing_result():
    from app.services.overall_design_adapters import (
        apply_push_jack_result,
    )

    design = OverallSupportDesign()

    apply_push_jack_result(
        design,
        {
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
            "bore_calc_mm": 110.1,
            "bore_candidate_mm": 125,
            "push_actual_kn": 386.6,
            "push_ok": True,
            "mt_t94_verified": False,
            "rod_mm": 70,
            "pull_required_kn": 250,
            "pull_actual_kn": 265.3,
            "pull_ok": True,
            "stroke_mm": 800,
        },
    )

    jack = design.hydraulic_components.push_jack

    assert jack.bore_candidate_mm.value == 125
    assert jack.push_actual_kn.value == 386.6
    assert jack.push_ok.value is True
    assert jack.pull_actual_kn.value == 265.3
    assert jack.stroke_mm.value == 800


def test_push_jack_adapter_preserves_no_formula_id_and_no_record():
    from app.services.overall_design_adapters import (
        apply_push_jack_result,
    )

    design = OverallSupportDesign()

    apply_push_jack_result(
        design,
        {
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
            "bore_calc_mm": 110.1,
            "bore_candidate_mm": 125,
            "push_actual_kn": 386.6,
            "push_ok": True,
            "mt_t94_verified": False,
        },
    )

    jack = design.hydraulic_components.push_jack

    assert jack.formula_ids == []
    assert jack.calculation_record_ids == []
    assert jack.mt_t94_verified is False


def test_push_jack_adapter_does_not_invent_optional_inputs():
    from app.services.overall_design_adapters import (
        apply_push_jack_result,
    )

    design = OverallSupportDesign()

    apply_push_jack_result(
        design,
        {
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
            "bore_calc_mm": 110.1,
            "bore_candidate_mm": 125,
            "push_actual_kn": 386.6,
            "push_ok": True,
            "mt_t94_verified": False,
        },
    )

    jack = design.hydraulic_components.push_jack

    assert jack.rod_mm is None
    assert jack.pull_required_kn is None
    assert jack.pull_actual_kn is None
    assert jack.pull_ok is None
    assert jack.stroke_mm is None


def test_d4_implementation_closeout_preserves_boundaries():
    doc = (
        ROOT
        / "docs/evidence/w37/W37D4_adapter_implementation.md"
    ).read_text(encoding="utf-8")

    assert "no F-JACK Formula ID" in doc
    assert "Ks is not eta" in doc
    assert "Bc is not inferred from canopy_len" in doc
    assert "eta remains:" in doc
    assert "not independent physical or manufacturing validation" in doc
