"""W35-D2 需求支护强度 → 需求工作阻力计算链。

依据：
- KA/T 554-1996（原 MT/T 554-1996）附录 D

边界：
- control_width_m 为显式、已核的控顶宽度 Bc；
- 不允许由历史 canopy_len 静默推断；
- support_efficiency 为支撑效率 Ks，不等同于历史 eta；
- 不自动使用全局 safety_factor。
"""


def control_area(
    center_dist_m: float,
    control_width_m: float,
) -> float:
    """F-QN-005: A_control = Sc × Bc."""
    if center_dist_m <= 0:
        raise ValueError("center_dist_m must be > 0")
    if control_width_m <= 0:
        raise ValueError("control_width_m must be > 0")

    return center_dist_m * control_width_m


def base_resistance(
    q_need_mpa: float,
    area_m2: float,
) -> float:
    """F-QN-006: F_base = q_need × A_control × 1000."""
    if q_need_mpa < 0:
        raise ValueError("q_need_mpa must be >= 0")
    if area_m2 <= 0:
        raise ValueError("area_m2 must be > 0")

    return q_need_mpa * area_m2 * 1000.0


def rated_resistance(
    base_kn: float,
    support_efficiency: float,
) -> float:
    """F-QN-007: F_rated = F_base / Ks."""
    if base_kn < 0:
        raise ValueError("base_kn must be >= 0")
    if not 0 < support_efficiency <= 1:
        raise ValueError(
            "support_efficiency must be in (0, 1]"
        )

    return base_kn / support_efficiency


def required_resistance(
    q_need_mpa: float,
    center_dist_m: float,
    control_width_m: float,
    support_efficiency: float,
) -> dict:
    """执行 F-QN-005 → 006 → 007 完整基础链。"""
    area = control_area(
        center_dist_m,
        control_width_m,
    )
    base = base_resistance(
        q_need_mpa,
        area,
    )
    rated = rated_resistance(
        base,
        support_efficiency,
    )

    return {
        "control_area_m2": area,
        "base_resistance_kn": base,
        "required_working_resistance_kn": rated,
        "support_efficiency": support_efficiency,
        "formula_ids": [
            "F-QN-005",
            "F-QN-006",
            "F-QN-007",
        ],
        "source": (
            "KA/T 554-1996 附录D；"
            "q_need为项目控制需求支护强度输入"
        ),
        "note": (
            "Bc必须为显式/已核控顶宽度；"
            "禁止由canopy_len静默推断；"
            "Ks不等同于历史eta"
        ),
    }
