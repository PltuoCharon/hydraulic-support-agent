from pathlib import Path

from app.models.overall_design import (
    EngineeringParameter,
    OverallSupportDesign,
)
from app.services.overall_design_report import (
    build_overall_design_summary,
    render_overall_design_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "app/services/overall_design_report.py"
CONTRACT = (
    ROOT
    / "docs/evidence/w37/W37D5_overall_design_report_contract.md"
)


def p(
    value,
    unit,
    origin,
    evidence,
    formula_ids=None,
):
    return EngineeringParameter(
        value=value,
        unit=unit,
        origin=origin,
        evidence_status=evidence,
        formula_ids=formula_ids or [],
    )


def test_report_contract_preserves_three_parameter_levels():
    text = CONTRACT.read_text(encoding="utf-8")

    assert "reference value" in text
    assert "requirement value" in text
    assert "design value" in text

    assert (
        "shall not automatically copy or promote"
        in text
    )


def test_summary_keeps_reference_requirement_and_design_separate():
    design = OverallSupportDesign()

    design.reference_support.working_resistance_kn = p(
        12000,
        "kN",
        "RETRIEVED",
        "PARTIAL",
    )

    design.support_requirement.required_working_resistance_kn = p(
        8750,
        "kN",
        "CALCULATED",
        "PARTIAL",
        ["F-QN-007"],
    )

    design.overall_parameters.design_working_resistance_kn = p(
        9000,
        "kN",
        "USER_INPUT",
        "PARTIAL",
    )

    result = build_overall_design_summary(design)

    values = result["parameter_comparison"][
        "working_resistance_kn"
    ]

    assert values["reference"]["value"] == 12000
    assert values["requirement"]["value"] == 8750
    assert values["design"]["value"] == 9000


def test_requirement_is_not_auto_promoted_to_design_value():
    design = OverallSupportDesign()

    design.support_requirement.required_working_resistance_kn = p(
        8750,
        "kN",
        "CALCULATED",
        "PARTIAL",
        ["F-QN-007"],
    )

    result = build_overall_design_summary(design)

    values = result["parameter_comparison"][
        "working_resistance_kn"
    ]

    assert values["requirement"]["value"] == 8750
    assert values["design"] is None


def test_report_preserves_parameter_traceability():
    design = OverallSupportDesign()

    design.support_requirement.required_working_resistance_kn = (
        EngineeringParameter(
            value=8750,
            unit="kN",
            origin="CALCULATED",
            evidence_status="PARTIAL",
            source_text="test source",
            formula_ids=["F-QN-007"],
            calculation_record_ids=[12],
        )
    )

    text = render_overall_design_markdown(design)

    assert "8750 kN" in text
    assert "CALCULATED" in text
    assert "PARTIAL" in text
    assert "F-QN-007" in text
    assert "12" in text


def test_report_keeps_support_length_parameter_semantic():
    design = OverallSupportDesign()

    design.reference_support.support_length_parameter_m = p(
        5.2,
        "m",
        "RETRIEVED",
        "PARTIAL",
    )

    text = render_overall_design_markdown(design)

    assert "支护长度参数" in text
    assert "顶梁长度" not in text
    assert "控顶距" not in text


def test_unimplemented_future_modules_remain_visible():
    design = OverallSupportDesign()

    result = build_overall_design_summary(design)

    assert (
        result["hydraulic_components"]["valve"]["status"]
        == "NOT_IMPLEMENTED"
    )

    assert (
        result["future_modules"]["linkage"]
        == "NOT_IMPLEMENTED"
    )

    assert (
        result["future_modules"]["structure"]
        == "NOT_IMPLEMENTED"
    )

    assert (
        result["future_modules"]["analyses"]
        == "NOT_IMPLEMENTED"
    )


def test_report_module_does_not_import_calculation_cores():
    text = REPORT.read_text(encoding="utf-8")

    assert "from app.services.calc" not in text
    assert "import app.services.calc" not in text


def test_empty_design_report_is_still_readable():
    design = OverallSupportDesign()

    text = render_overall_design_markdown(design)

    assert "# 液压支架总体设计方案" in text
    assert "未确定" in text
    assert "NOT_IMPLEMENTED" in text
