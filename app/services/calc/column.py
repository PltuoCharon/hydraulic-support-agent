"""立柱缸径反算与校核(W33-D3)

公式: P = n * (pi/4) * D^2 * p * eta  =>  D = sqrt(4P / (n*pi*p*eta))
标准缸径系列: GB/T 2348 液压缸内径系列
初撑力比校核: 初撑力/额定工作阻力 60%~85%(W35-D2 已核标准证据)
诚实边界: 参数化设计计算与校核, 不生成结构设计图样
"""
from app.services.calc.hydraulic_cylinder import (
    STANDARD_BORES,
    bore_for_push_force,
    push_force,
    round_up_standard_bore,
)

SOURCE = ("标准缸径系列: GB/T 2348; " "计算关系: 项目立柱参数化计算式 P=n*(pi/4)*D^2*p*eta; " "eta: 历史立柱修正系数，物理口径待核")


def column_force(d_mm, p_mpa):
    """兼容入口：正算单柱推力(kN)。"""
    if not 40 <= d_mm <= 500:
        raise ValueError(
            f"缸径 {d_mm}mm 超出系列范围 40~500mm"
        )
    if not 5 <= p_mpa <= 50:
        raise ValueError(
            f"立柱工作压力 {p_mpa}MPa 超出常见范围 5~50MPa"
        )

    return round(
        push_force(d_mm, p_mpa),
        1,
    )


def bore_diameter(p_kn, n, p_mpa, eta):
    """反算缸径(mm): D = sqrt(4P/(n*pi*p*eta))"""
    if not 100 <= p_kn <= 50000:
        raise ValueError(f"工作阻力 {p_kn}kN 超出常见范围 100~50000kN")
    if not 1 <= n <= 8:
        raise ValueError(f"立柱根数 {n} 超出常见范围 1~8")
    if not 5 <= p_mpa <= 50:
        raise ValueError(f"立柱工作压力 {p_mpa}MPa 超出常见范围 5~50MPa")
    if not 0.8 <= eta <= 1.0:
        raise ValueError(f"历史立柱修正系数 eta={eta} 超出当前接口允许范围 0.8~1.0")
    single_force_kn = p_kn / (n * eta)
    return round(
        bore_for_push_force(
            single_force_kn,
            p_mpa,
        ),
        1,
    )


def round_up_bore(d_mm):
    """兼容入口：向上圆整到标准缸径系列。"""
    return round_up_standard_bore(d_mm)


def setting_ratio(p_set_kn, p_rated_kn):
    """初撑力/额定工作阻力比校核: 返回 (比值%, 是否合格), 合格区间 60%~85%"""
    if p_rated_kn <= 0:
        raise ValueError("额定工作阻力必须为正")
    ratio = round(p_set_kn / p_rated_kn * 100, 1)
    return ratio, 60.0 <= ratio <= 85.0


def design(p_kn, n, p_mpa, eta, p_set_kn=None):
    """缸径选型全流程: 反算->圆整->圆整后计算承载力->初撑力比校核"""
    d_calc = bore_diameter(p_kn, n, p_mpa, eta)
    d_std = round_up_bore(d_calc)
    p_actual = column_force(d_std, p_mpa) * n * eta
    out = {
        "d_calc_mm": d_calc,
        "d_std_mm": d_std,
        "p_actual_kn": round(p_actual, 1),
        "inputs": {"p_kn": p_kn, "n": n, "p_mpa": p_mpa, "eta": eta},
        "source": SOURCE,
    }
    if p_set_kn is not None:
        ratio, ok = setting_ratio(p_set_kn, p_kn)
        out["setting_ratio_pct"] = ratio
        out["setting_ok"] = ok
        out["rule"] = "初撑力/额定工作阻力校核区间 60%~85%（W35-D2 已核标准证据）"
    return out
