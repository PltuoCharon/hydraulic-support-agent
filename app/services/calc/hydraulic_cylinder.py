"""W36-D2 通用液压执行元件基础计算。

只包含液压缸基础几何与压力-面积-力关系。

边界：
- 不包含支架型号
- 不包含立柱根数 n
- 不包含历史 eta
- 不包含初撑力比
- 不包含支护强度
- 不包含具体千斤顶载荷语义

W36-D2 暂不建立新的 Formula Registry ID。
这些函数作为后续立柱/千斤顶共享的基础计算原语。
"""

import math


STANDARD_BORES = [
    40, 50, 63, 80, 100, 125, 140, 160, 180, 200,
    220, 250, 280, 320, 360, 400, 450, 500,
]


def piston_area(bore_mm):
    """活塞无杆腔面积，mm^2。"""
    if bore_mm <= 0:
        raise ValueError("缸径必须大于0")

    return math.pi * bore_mm**2 / 4


def annular_area(bore_mm, rod_mm):
    """活塞杆腔有效面积，mm^2。"""
    if bore_mm <= 0:
        raise ValueError("缸径必须大于0")

    if not 0 < rod_mm < bore_mm:
        raise ValueError(
            "活塞杆直径必须大于0且小于缸径"
        )

    return math.pi * (bore_mm**2 - rod_mm**2) / 4


def _validate_pressure(pressure_mpa):
    if pressure_mpa <= 0:
        raise ValueError("压力必须大于0")


def push_force(bore_mm, pressure_mpa):
    """无杆腔推力，kN。F=p*A。"""
    _validate_pressure(pressure_mpa)

    force_kn = (
        pressure_mpa
        * piston_area(bore_mm)
        / 1000
    )

    return force_kn


def pull_force(bore_mm, rod_mm, pressure_mpa):
    """杆腔拉力，kN。F=p*A_annular。"""
    _validate_pressure(pressure_mpa)

    force_kn = (
        pressure_mpa
        * annular_area(bore_mm, rod_mm)
        / 1000
    )

    return force_kn


def bore_for_push_force(force_kn, pressure_mpa):
    """由目标单缸推力与压力反算理论缸径，mm。"""
    if force_kn <= 0:
        raise ValueError("目标推力必须大于0")

    _validate_pressure(pressure_mpa)

    diameter_mm = math.sqrt(
        4 * force_kn * 1000
        / (math.pi * pressure_mpa)
    )

    return diameter_mm


def round_up_standard_bore(bore_mm):
    """向上圆整到当前 GB/T 2348 常用缸径系列。"""
    if bore_mm <= 0:
        raise ValueError("缸径必须大于0")

    for standard in STANDARD_BORES:
        if standard >= bore_mm:
            return standard

    raise ValueError(
        f"缸径 {bore_mm}mm 超出标准系列上限 "
        f"{STANDARD_BORES[-1]}mm"
    )
