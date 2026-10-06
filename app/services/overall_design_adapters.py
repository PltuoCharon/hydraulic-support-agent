"""W37-D4 adapters from existing engineering results to OverallSupportDesign.

Boundary:
- consume already-computed result dictionaries
- do not call engineering calculation cores
- do not recalculate values
- do not invent missing engineering values
"""

from typing import Any

from app.models.overall_design import (
    EngineeringParameter,
    OverallSupportDesign,
)


def _require_keys(
    result: dict[str, Any],
    *keys: str,
) -> None:
    missing = [
        key
        for key in keys
        if key not in result
    ]

    if missing:
        raise ValueError(
            "adapter result missing required fields: "
            + ", ".join(missing)
        )


def _append_unique(
    target: list,
    values,
) -> None:
    for value in values:
        if value is None:
            continue

        if value not in target:
            target.append(value)


def _append_provenance(
    design: OverallSupportDesign,
    *,
    source_text: str | None = None,
    formula_ids: list[str] | None = None,
    note: str | None = None,
) -> None:
    if source_text:
        _append_unique(
            design.provenance.source_texts,
            [source_text],
        )

    if formula_ids:
        _append_unique(
            design.provenance.formula_ids,
            formula_ids,
        )

    if note:
        _append_unique(
            design.provenance.notes,
            [note],
        )


def _calculated_parameter(
    *,
    value: Any,
    unit: str | None,
    formula_id: str,
    source_text: str | None = None,
    note: str | None = None,
) -> EngineeringParameter:
    return EngineeringParameter(
        value=value,
        unit=unit,
        origin="CALCULATED",
        evidence_status="PARTIAL",
        source_text=source_text,
        formula_ids=[formula_id],
        note=note,
    )


def apply_q_need_result(
    design: OverallSupportDesign,
    result: dict[str, Any],
) -> OverallSupportDesign:
    """Map an already-computed q_need result into OverallSupportDesign."""

    _require_keys(
        result,
        "p1_mpa",
        "p2_mpa",
        "p3_mpa",
        "q_need_mpa",
        "governing",
    )

    source = result.get("source")
    rule = result.get("rule")

    req = design.support_requirement

    req.p1_mpa = _calculated_parameter(
        value=result["p1_mpa"],
        unit="MPa",
        formula_id="F-QN-001",
        source_text=source,
    )

    req.p2_mpa = _calculated_parameter(
        value=result["p2_mpa"],
        unit="MPa",
        formula_id="F-QN-002",
        source_text=source,
    )

    req.p3_mpa = _calculated_parameter(
        value=result["p3_mpa"],
        unit="MPa",
        formula_id="F-QN-003",
        source_text=source,
    )

    req.required_support_intensity_mpa = _calculated_parameter(
        value=result["q_need_mpa"],
        unit="MPa",
        formula_id="F-QN-004",
        source_text=source,
        note=rule,
    )

    req.governing_method = result["governing"]

    _append_provenance(
        design,
        source_text=source,
        formula_ids=[
            "F-QN-001",
            "F-QN-002",
            "F-QN-003",
            "F-QN-004",
        ],
        note=rule,
    )

    return design


def apply_required_resistance_result(
    design: OverallSupportDesign,
    result: dict[str, Any],
) -> OverallSupportDesign:
    """Map an already-computed required-resistance result."""

    _require_keys(
        result,
        "control_area_m2",
        "base_resistance_kn",
        "required_working_resistance_kn",
        "support_efficiency",
    )

    source = result.get("source")
    note = result.get("note")

    req = design.support_requirement

    req.control_area_m2 = _calculated_parameter(
        value=result["control_area_m2"],
        unit="m²",
        formula_id="F-QN-005",
        source_text=source,
    )

    req.base_resistance_kn = _calculated_parameter(
        value=result["base_resistance_kn"],
        unit="kN",
        formula_id="F-QN-006",
        source_text=source,
    )

    req.required_working_resistance_kn = _calculated_parameter(
        value=result["required_working_resistance_kn"],
        unit="kN",
        formula_id="F-QN-007",
        source_text=source,
        note=note,
    )

    req.support_efficiency_ks = EngineeringParameter(
        value=result["support_efficiency"],
        unit=None,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
        source_text=source,
        note=(
            "显式支撑效率 Ks；当前 Adapter 不具有该输入的"
            "独立参数级来源证明；Ks 不等同于 eta"
        ),
    )

    _append_provenance(
        design,
        source_text=source,
        formula_ids=[
            "F-QN-005",
            "F-QN-006",
            "F-QN-007",
        ],
        note=note,
    )

    return design


def _input_parameter(
    *,
    value: Any,
    unit: str | None = None,
    origin: str = "USER_INPUT",
    evidence_status: str = "PARTIAL",
    source_text: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """Build a structured input trace without changing the input value."""

    return EngineeringParameter(
        value=value,
        unit=unit,
        origin=origin,
        evidence_status=evidence_status,
        source_text=source_text,
        note=note,
    ).model_dump(mode="json")


def apply_column_design_result(
    design: OverallSupportDesign,
    result: dict[str, Any],
    *,
    p_kn_trace: EngineeringParameter | None = None,
    p_set_kn_trace: EngineeringParameter | None = None,
) -> OverallSupportDesign:
    """Map an already-computed column-design result."""

    _require_keys(
        result,
        "d_calc_mm",
        "d_std_mm",
        "p_actual_kn",
        "inputs",
    )

    inputs = result["inputs"]

    _require_keys(
        inputs,
        "p_kn",
        "n",
        "p_mpa",
        "eta",
    )

    source = result.get("source")

    formula_ids = [
        "F-COL-001",
        "F-COL-002",
    ]

    if "setting_ratio_pct" in result:
        formula_ids.append("F-COL-003")

    record_ids = []

    record_id = result.get("record_id")

    if record_id is not None:
        record_ids.append(record_id)

    column = design.hydraulic_components.columns

    if column is None:
        from app.models.overall_design import ColumnDesign

        column = ColumnDesign()
        design.hydraulic_components.columns = column

    column.d_calc_mm = _calculated_parameter(
        value=result["d_calc_mm"],
        unit="mm",
        formula_id="F-COL-001",
        source_text=source,
    )

    column.d_std_mm = EngineeringParameter(
        value=result["d_std_mm"],
        unit="mm",
        origin="CALCULATED",
        evidence_status="PARTIAL",
        source_text=source,
        formula_ids=["F-COL-001"],
        note="按当前项目标准缸径系列向上圆整后的候选缸径",
    )

    column.p_actual_kn = _calculated_parameter(
        value=result["p_actual_kn"],
        unit="kN",
        formula_id="F-COL-002",
        source_text=source,
        note=(
            "候选标准缸径下，按承载立柱根数 n 与历史修正系数 eta "
            "计算的整架计算承载力"
        ),
    )

    if "setting_ratio_pct" in result:
        column.setting_ratio_pct = _calculated_parameter(
            value=result["setting_ratio_pct"],
            unit="%",
            formula_id="F-COL-003",
            source_text=source,
        )

    if "setting_ok" in result:
        column.setting_ok = EngineeringParameter(
            value=result["setting_ok"],
            unit=None,
            origin="CALCULATED",
            evidence_status="PARTIAL",
            source_text=source,
            formula_ids=["F-COL-003"],
        )

    if p_kn_trace is not None:
        column.inputs["p_kn"] = p_kn_trace.model_dump(
            mode="json"
        )
    else:
        column.inputs["p_kn"] = _input_parameter(
            value=inputs["p_kn"],
            unit="kN",
            note="当前 Adapter 未收到独立上游 provenance",
        )

    column.inputs["n"] = _input_parameter(
        value=inputs["n"],
        unit=None,
    )

    column.inputs["p_mpa"] = _input_parameter(
        value=inputs["p_mpa"],
        unit="MPa",
    )

    column.inputs["eta"] = _input_parameter(
        value=inputs["eta"],
        unit=None,
        origin="USER_INPUT",
        evidence_status="EVIDENCE_GAP",
        note=(
            "历史立柱修正系数；物理口径待核；"
            "不得解释为液压效率、机械效率或 Ks"
        ),
    )

    if "p_set_kn" in inputs and inputs["p_set_kn"] is not None:
        if p_set_kn_trace is not None:
            column.inputs["p_set_kn"] = (
                p_set_kn_trace.model_dump(mode="json")
            )
        else:
            column.inputs["p_set_kn"] = _input_parameter(
                value=inputs["p_set_kn"],
                unit="kN",
            )

    column.formula_ids = formula_ids
    column.calculation_record_ids = record_ids
    column.source_text = source
    column.status = "PARTIAL"

    _append_provenance(
        design,
        source_text=source,
        formula_ids=formula_ids,
    )

    if record_ids:
        _append_unique(
            design.provenance.calculation_record_ids,
            record_ids,
        )

    return design


def apply_push_jack_result(
    design: OverallSupportDesign,
    result: dict[str, Any],
) -> OverallSupportDesign:
    """Map an already-computed push-jack design result."""

    _require_keys(
        result,
        "push_required_kn",
        "pressure_mpa",
        "bore_calc_mm",
        "bore_candidate_mm",
        "push_actual_kn",
        "push_ok",
        "mt_t94_verified",
    )

    from app.models.overall_design import PushJackDesign

    jack = PushJackDesign(
        status="PARTIAL",
        mt_t94_verified=result["mt_t94_verified"],
    )

    jack.push_required_kn = EngineeringParameter(
        value=result["push_required_kn"],
        unit="kN",
        origin="USER_INPUT",
        evidence_status="PARTIAL",
    )

    jack.pressure_mpa = EngineeringParameter(
        value=result["pressure_mpa"],
        unit="MPa",
        origin="USER_INPUT",
        evidence_status="PARTIAL",
    )

    jack.bore_calc_mm = EngineeringParameter(
        value=result["bore_calc_mm"],
        unit="mm",
        origin="CALCULATED",
        evidence_status="PARTIAL",
        note="由既有推移千斤顶计算核心输出；D4 Adapter 不重新计算",
    )

    jack.bore_candidate_mm = EngineeringParameter(
        value=result["bore_candidate_mm"],
        unit="mm",
        origin="CALCULATED",
        evidence_status="PARTIAL",
        note=(
            "当前项目候选缸径；不得表示为已独立验证的 MT/T 94 合规结果"
        ),
    )

    jack.push_actual_kn = EngineeringParameter(
        value=result["push_actual_kn"],
        unit="kN",
        origin="CALCULATED",
        evidence_status="PARTIAL",
    )

    jack.push_ok = EngineeringParameter(
        value=result["push_ok"],
        unit=None,
        origin="CALCULATED",
        evidence_status="PARTIAL",
    )

    if "rod_mm" in result:
        jack.rod_mm = EngineeringParameter(
            value=result["rod_mm"],
            unit="mm",
            origin="USER_INPUT",
            evidence_status="PARTIAL",
        )

    if "pull_required_kn" in result:
        jack.pull_required_kn = EngineeringParameter(
            value=result["pull_required_kn"],
            unit="kN",
            origin="USER_INPUT",
            evidence_status="PARTIAL",
        )

    if "pull_actual_kn" in result:
        jack.pull_actual_kn = EngineeringParameter(
            value=result["pull_actual_kn"],
            unit="kN",
            origin="CALCULATED",
            evidence_status="PARTIAL",
        )

    if "pull_ok" in result:
        jack.pull_ok = EngineeringParameter(
            value=result["pull_ok"],
            unit=None,
            origin="CALCULATED",
            evidence_status="PARTIAL",
        )

    if "stroke_mm" in result:
        jack.stroke_mm = EngineeringParameter(
            value=result["stroke_mm"],
            unit="mm",
            origin="USER_INPUT",
            evidence_status="PARTIAL",
            note="显式工程输入；当前不参与力学反算",
        )

    jack.formula_ids = []
    jack.calculation_record_ids = []

    jack.note = (
        "W36/W37 当前未建立 F-JACK Formula ID，"
        "未建立 push-jack Calculation Record；"
        "mt_t94_verified 原样保留"
    )

    design.hydraulic_components.push_jack = jack

    return design
