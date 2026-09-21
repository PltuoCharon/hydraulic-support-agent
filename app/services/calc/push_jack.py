"""W36-D3 推移千斤顶第一版参数设计服务。

边界：
- 复用 HydraulicCylinder 基础原语
- 不自动生成活塞杆直径
- 不自动生成行程
- 不提供默认工作压力
- 不引入 eta
- 不假定推输送机/移架对应哪个油腔
- 当前候选缸径不宣称 MT/T94 已验证
"""

from app.services.calc.hydraulic_cylinder import (
    bore_for_push_force,
    pull_force,
    push_force,
    round_up_standard_bore,
)


def _positive(value, name):
    if value is None or value <= 0:
        raise ValueError(f"{name}必须大于0")
    return value


def push_jack_design(
    *,
    push_required_kn,
    pressure_mpa,
    rod_mm=None,
    pull_required_kn=None,
    stroke_mm=None,
):
    """推移千斤顶第一版参数化设计。

    push_required_kn:
        无杆腔推力设计需求，kN。

    pressure_mpa:
        显式工作压力，MPa。

    rod_mm:
        可选，用户给定活塞杆直径，mm。

    pull_required_kn:
        可选，杆腔拉力校核需求，kN。

    stroke_mm:
        可选，仅作为显式工程输入保存，不参与力学反算。
    """
    _positive(push_required_kn, "无杆腔推力需求")
    _positive(pressure_mpa, "工作压力")

    if pull_required_kn is not None:
        _positive(pull_required_kn, "杆腔拉力需求")

        if rod_mm is None:
            raise ValueError(
                "提供杆腔拉力需求时必须同时提供活塞杆直径"
            )

    if stroke_mm is not None:
        _positive(stroke_mm, "行程")

    bore_calc_mm = bore_for_push_force(
        push_required_kn,
        pressure_mpa,
    )

    bore_candidate_mm = round_up_standard_bore(
        bore_calc_mm
    )

    push_actual_kn = push_force(
        bore_candidate_mm,
        pressure_mpa,
    )

    out = {
        "push_required_kn": push_required_kn,
        "pressure_mpa": pressure_mpa,
        "bore_calc_mm": round(bore_calc_mm, 1),
        "bore_candidate_mm": bore_candidate_mm,
        "push_actual_kn": round(push_actual_kn, 1),
        "push_ok": push_actual_kn >= push_required_kn,
        "mt_t94_verified": False,
    }

    if stroke_mm is not None:
        out["stroke_mm"] = stroke_mm
        out["stroke_origin"] = "user_input"

    if rod_mm is not None:
        _positive(rod_mm, "活塞杆直径")

        if rod_mm >= bore_candidate_mm:
            raise ValueError(
                "活塞杆直径必须小于候选缸径"
            )

        pull_actual_kn = pull_force(
            bore_candidate_mm,
            rod_mm,
            pressure_mpa,
        )

        out["rod_mm"] = rod_mm
        out["pull_actual_kn"] = round(
            pull_actual_kn,
            1,
        )

        if pull_required_kn is not None:
            out["pull_required_kn"] = (
                pull_required_kn
            )
            out["pull_ok"] = (
                pull_actual_kn
                >= pull_required_kn
            )

    return out
