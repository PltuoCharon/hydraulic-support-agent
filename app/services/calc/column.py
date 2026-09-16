"""立柱缸径反算与校核(W33-D3)

公式: P = n * (pi/4) * D^2 * p * eta  =>  D = sqrt(4P / (n*pi*p*eta))
标准缸径系列: GB/T 2348 液压缸内径系列
初撑力比校核: 初撑力/工作阻力 宜在 60%~85%(设计惯例)
诚实边界: 参数化设计计算与校核, 不生成结构设计图样
"""
import math

# GB/T 2348 液压缸缸径系列(常用段, mm)
STANDARD_BORES = [40, 50, 63, 80, 100, 125, 140, 160, 180, 200,
                  220, 250, 280, 320, 360, 400, 450, 500]

SOURCE = "GB/T 2348 液压缸缸径系列; 缸径反算式 P=n*(pi/4)*D^2*p*eta"


def column_force(d_mm, p_mpa):
    """正算单柱推力(kN): P = (pi/4)*D^2*p"""
    if not 40 <= d_mm <= 500:
        raise ValueError(f"缸径 {d_mm}mm 超出系列范围 40~500mm")
    if not 5 <= p_mpa <= 50:
        raise ValueError(f"工作压力 {p_mpa}MPa 超出常见范围 5~50MPa")
    return round(math.pi / 4 * d_mm**2 * p_mpa / 1000, 1)


def bore_diameter(p_kn, n, p_mpa, eta=0.9):
    """反算缸径(mm): D = sqrt(4P/(n*pi*p*eta))"""
    if not 100 <= p_kn <= 50000:
        raise ValueError(f"工作阻力 {p_kn}kN 超出常见范围 100~50000kN")
    if not 1 <= n <= 8:
        raise ValueError(f"立柱根数 {n} 超出常见范围 1~8")
    if not 5 <= p_mpa <= 50:
        raise ValueError(f"工作压力 {p_mpa}MPa 超出常见范围 5~50MPa")
    if not 0.8 <= eta <= 1.0:
        raise ValueError(f"效率 eta={eta} 超出常见范围 0.8~1.0")
    return round(math.sqrt(4 * p_kn * 1000 / (n * math.pi * p_mpa * eta)), 1)


def round_up_bore(d_mm):
    """向上圆整到标准缸径系列"""
    for s in STANDARD_BORES:
        if s >= d_mm:
            return s
    raise ValueError(f"缸径 {d_mm}mm 超出标准系列上限 {STANDARD_BORES[-1]}mm")


def setting_ratio(p_set_kn, p_rated_kn):
    """初撑力比校核: 返回 (比值%, 是否合格), 合格区间 60%~85%"""
    if p_rated_kn <= 0:
        raise ValueError("工作阻力必须为正")
    ratio = round(p_set_kn / p_rated_kn * 100, 1)
    return ratio, 60.0 <= ratio <= 85.0


def design(p_kn, n, p_mpa, eta=0.9, p_set_kn=None):
    """缸径选型全流程: 反算->圆整->圆整后实际阻力->初撑力比校核"""
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
        ratio, ok = setting_ratio(p_set_kn, p_actual)
        out["setting_ratio_pct"] = ratio
        out["setting_ok"] = ok
        out["rule"] = "初撑力/工作阻力 宜在 60%~85%"
    return out
