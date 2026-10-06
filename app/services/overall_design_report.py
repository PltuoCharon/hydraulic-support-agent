"""W37-D5 readable summary/report for OverallSupportDesign.

Boundary:
- consumes OverallSupportDesign only
- no engineering calculations
- no database persistence
- no API/UI side effects
"""

from typing import Any

from app.models.overall_design import (
    EngineeringParameter,
    OverallSupportDesign,
)


def parameter_snapshot(
    parameter: EngineeringParameter | None,
) -> dict[str, Any] | None:
    if parameter is None:
        return None

    return parameter.model_dump(mode="json")


def _component_status(component) -> str | None:
    if component is None:
        return None

    return component.status


def build_overall_design_summary(
    design: OverallSupportDesign,
) -> dict[str, Any]:
    """Build a structured, calculation-free design summary."""

    column = design.hydraulic_components.columns
    jack = design.hydraulic_components.push_jack

    return {
        "version": design.version,
        "metadata": design.metadata.model_dump(mode="json"),
        "parameter_comparison": {
            "working_resistance_kn": {
                "reference": parameter_snapshot(
                    design.reference_support.working_resistance_kn
                ),
                "requirement": parameter_snapshot(
                    design.support_requirement
                    .required_working_resistance_kn
                ),
                "design": parameter_snapshot(
                    design.overall_parameters
                    .design_working_resistance_kn
                ),
            },
            "support_intensity_mpa": {
                "reference": parameter_snapshot(
                    design.reference_support.reference_intensity
                ),
                "requirement": parameter_snapshot(
                    design.support_requirement
                    .required_support_intensity_mpa
                ),
                "design": parameter_snapshot(
                    design.overall_parameters
                    .design_support_intensity_mpa
                ),
            },
            "height_min_m": {
                "reference": parameter_snapshot(
                    design.reference_support.height_min_m
                ),
                "design": parameter_snapshot(
                    design.overall_parameters.design_height_min_m
                ),
            },
            "height_max_m": {
                "reference": parameter_snapshot(
                    design.reference_support.height_max_m
                ),
                "design": parameter_snapshot(
                    design.overall_parameters.design_height_max_m
                ),
            },
            "center_distance_m": {
                "reference": parameter_snapshot(
                    design.reference_support.center_distance_m
                ),
                "design": parameter_snapshot(
                    design.overall_parameters.center_distance_m
                ),
            },
            "support_length_parameter_m": {
                "reference": parameter_snapshot(
                    design.reference_support
                    .support_length_parameter_m
                ),
            },
        },
        "hydraulic_components": {
            "columns": None if column is None else {
                "status": column.status,
                "d_calc_mm": parameter_snapshot(
                    column.d_calc_mm
                ),
                "d_std_mm": parameter_snapshot(
                    column.d_std_mm
                ),
                "p_actual_kn": parameter_snapshot(
                    column.p_actual_kn
                ),
                "setting_ratio_pct": parameter_snapshot(
                    column.setting_ratio_pct
                ),
                "setting_ok": parameter_snapshot(
                    column.setting_ok
                ),
                "inputs": column.inputs,
                "formula_ids": list(column.formula_ids),
                "calculation_record_ids": list(
                    column.calculation_record_ids
                ),
            },
            "push_jack": None if jack is None else {
                "status": jack.status,
                "bore_candidate_mm": parameter_snapshot(
                    jack.bore_candidate_mm
                ),
                "push_actual_kn": parameter_snapshot(
                    jack.push_actual_kn
                ),
                "pull_actual_kn": parameter_snapshot(
                    jack.pull_actual_kn
                ),
                "stroke_mm": parameter_snapshot(
                    jack.stroke_mm
                ),
                "mt_t94_verified": jack.mt_t94_verified,
                "formula_ids": list(jack.formula_ids),
                "calculation_record_ids": list(
                    jack.calculation_record_ids
                ),
            },
            "valve": {
                "status": (
                    design.hydraulic_components
                    .valve.status
                ),
            },
            "pipeline": {
                "status": (
                    design.hydraulic_components
                    .pipeline.status
                ),
            },
            "pump_station": {
                "status": (
                    design.hydraulic_components
                    .pump_station.status
                ),
            },
        },
        "future_modules": {
            "linkage": _component_status(
                design.linkage
            ),
            "structure": _component_status(
                design.structure
            ),
            "analyses": _component_status(
                design.analyses
            ),
        },
        "provenance": design.provenance.model_dump(
            mode="json"
        ),
        "status": design.status,
    }


def _format_parameter(
    parameter: EngineeringParameter | None,
) -> str:
    if parameter is None:
        return "未确定"

    value = parameter.value
    unit = parameter.unit or ""

    value_text = (
        f"{value} {unit}".strip()
    )

    formula_text = (
        ", ".join(parameter.formula_ids)
        if parameter.formula_ids
        else "—"
    )

    record_text = (
        ", ".join(
            str(x)
            for x in parameter.calculation_record_ids
        )
        if parameter.calculation_record_ids
        else "—"
    )

    return (
        f"{value_text}"
        f"；来源={parameter.origin}"
        f"；证据={parameter.evidence_status}"
        f"；公式={formula_text}"
        f"；计算记录={record_text}"
    )


def render_overall_design_markdown(
    design: OverallSupportDesign,
) -> str:
    """Render a human-readable engineering summary."""

    ref = design.reference_support
    req = design.support_requirement
    overall = design.overall_parameters

    lines = [
        "# 液压支架总体设计方案",
        "",
        f"- 设计名称：{design.metadata.design_name}",
        f"- 契约版本：hs.overallDesign.v{design.version}",
        f"- 总体状态：{design.status}",
        "",
        "## 总体参数对比",
        "",
        "| 参数 | 历史/参考值 | 工况需求值 | 当前设计值 |",
        "|---|---|---|---|",
        (
            "| 工作阻力 | "
            + _format_parameter(ref.working_resistance_kn)
            + " | "
            + _format_parameter(
                req.required_working_resistance_kn
            )
            + " | "
            + _format_parameter(
                overall.design_working_resistance_kn
            )
            + " |"
        ),
        (
            "| 支护强度 | "
            + _format_parameter(ref.reference_intensity)
            + " | "
            + _format_parameter(
                req.required_support_intensity_mpa
            )
            + " | "
            + _format_parameter(
                overall.design_support_intensity_mpa
            )
            + " |"
        ),
        (
            "| 最低设计高度 | "
            + _format_parameter(ref.height_min_m)
            + " | — | "
            + _format_parameter(
                overall.design_height_min_m
            )
            + " |"
        ),
        (
            "| 最高设计高度 | "
            + _format_parameter(ref.height_max_m)
            + " | — | "
            + _format_parameter(
                overall.design_height_max_m
            )
            + " |"
        ),
        (
            "| 中心距 | "
            + _format_parameter(ref.center_distance_m)
            + " | — | "
            + _format_parameter(
                overall.center_distance_m
            )
            + " |"
        ),
        (
            "| 支护长度参数 | "
            + _format_parameter(
                ref.support_length_parameter_m
            )
            + " | — | 未确定 |"
        ),
        "",
        "## 液压部件",
        "",
    ]

    column = design.hydraulic_components.columns

    if column is None:
        lines.append("- 立柱：未进入总体设计对象")
    else:
        lines.extend([
            f"- 立柱状态：{column.status}",
            (
                "- 计算缸径："
                + _format_parameter(column.d_calc_mm)
            ),
            (
                "- 候选标准缸径："
                + _format_parameter(column.d_std_mm)
            ),
            (
                "- 整架计算承载力："
                + _format_parameter(column.p_actual_kn)
            ),
        ])

        eta = column.inputs.get("eta")

        if eta is not None:
            lines.append(
                "- η 输入证据状态："
                + str(eta.get("evidence_status", "—"))
            )

    jack = design.hydraulic_components.push_jack

    if jack is None:
        lines.append("- 推移千斤顶：未进入总体设计对象")
    else:
        lines.extend([
            f"- 推移千斤顶状态：{jack.status}",
            (
                "- 候选缸径："
                + _format_parameter(
                    jack.bore_candidate_mm
                )
            ),
            (
                "- 无杆腔理论推力："
                + _format_parameter(
                    jack.push_actual_kn
                )
            ),
            (
                "- MT/T 94 独立验证："
                + str(jack.mt_t94_verified)
            ),
        ])

    lines.extend([
        "",
        "## 后续模块状态",
        "",
        (
            "- Valve："
            + design.hydraulic_components.valve.status
        ),
        (
            "- Pipeline："
            + design.hydraulic_components.pipeline.status
        ),
        (
            "- Pump Station："
            + design.hydraulic_components.pump_station.status
        ),
        "- 四连杆机构：" + design.linkage.status,
        "- 结构模型：" + design.structure.status,
        "- 工程分析：" + design.analyses.status,
    ])

    return "\n".join(lines) + "\n"
