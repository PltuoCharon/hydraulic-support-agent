"""选型硬约束筛选：纯函数，与HTTP解耦，方便单测"""
from app.core.numparse import parse_number

def height_ok(support: dict, h_min: float, h_max: float,
              allowance: float = 0.3, roof_sink: float = 0.15) -> bool:
    s_min = parse_number(support.get("height_min"))
    s_max = parse_number(support.get("height_max"))
    if s_min is None or s_max is None:
        return True   # 高度缺失的架型不因此淘汰，留待人工核对
    return s_max >= h_max + allowance and s_min <= h_min - roof_sink

def dip_ok(support: dict, dip_angle: float) -> bool:
    return dip_angle <= 25

def required_intensity(h_max: float) -> float:
    """需求支护强度估算 p≈8×M×γ/1000 MPa（工程估算式，论文需引出处）"""
    return round(8 * h_max * 25 / 1000, 3)

def effective_height(area: dict) -> float:
    """有效采高：煤层厚>6.5m(综放/分层)用机采高度，否则用煤层厚度。
    机采高度优先级: mining_height -> (min+max)/2 -> max -> min -> 4.0(综放默认值,与案例库一致)"""
    from app.core.numparse import parse_number
    coal = parse_number(area.get("coal_thickness")) or 0
    if coal <= 6.5:
        return coal
    h = parse_number(area.get("mining_height"))
    if h:
        return h
    lo = parse_number(area.get("mining_height_min"))
    hi = parse_number(area.get("mining_height_max"))
    if lo and hi:
        return (lo + hi) / 2
    if hi or lo:
        return hi or lo
    return 4.0


def filter_supports(area: dict, supports: list) -> dict:
    h_max = effective_height(area)
    h_min = parse_number(area.get("mining_height_min")) or h_max * 0.7
    dip = parse_number(area.get("dip_angle")) or 0
    req_p = required_intensity(h_max)

    passed, rejected = [], []
    for s in supports:
        reasons = []
        if not height_ok(s, h_min, h_max):
            reasons.append("高度范围不匹配")
        if not dip_ok(s, dip):
            reasons.append("倾角超出适应范围")
        si = parse_number(s.get("intensity"))
        if si is not None and si < req_p:
            reasons.append(f"支护强度{si}MPa<需求{req_p}MPa")
        if reasons:
            rejected.append({**s, "reject_reasons": reasons})
        else:
            passed.append(s)
    return {"required_intensity": req_p, "h_used": [h_min, h_max],
            "passed": passed, "rejected": rejected}


