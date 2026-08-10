"""支架参数重算服务：薄封装 core.support 公式类。W18-D3。
公式链: 单柱推力=P·πD²/4 → 工作阻力=Σ推力×η → 支护强度=阻力/(中心距×控顶距)
单位: MPa·mm²=N → /1000=kN; kN/m²=kPa → /1000=MPa。
η 支撑效率读 param_dependencies(问题8参数化成果)，默认不再硬编码。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.support import Cylinder, Support
from app.core.params import Params

def recalc(bore_mm: float, pressure_mpa: float = 31.5, n_cylinders: int = 2,
           center_dist: float = 1.75, canopy_len: float = 4.0,
           eta: float | None = None) -> dict:
    """按力学公式重算支架参数。返回公式法估算值（非实测）。"""
    if not (100 <= bore_mm <= 500):
        raise ValueError(f"缸径 {bore_mm}mm 超出常见范围 100~500mm")
    if not (10 <= pressure_mpa <= 50):
        raise ValueError(f"压力 {pressure_mpa}MPa 超出常见范围 10~50MPa")
    if not (1 <= n_cylinders <= 8):
        raise ValueError(f"立柱数 {n_cylinders} 超出常见范围 1~8")
    eta_used = eta if eta is not None else Params().eta
    cyls = [Cylinder(bore_mm, pressure_mpa) for _ in range(n_cylinders)]
    s = Support(f"{n_cylinders}柱Φ{bore_mm}mm@{pressure_mpa}MPa",
                cyls, center_dist, canopy_len, eta_used)
    single = cyls[0].thrust()
    return {
        "bore_mm": bore_mm, "pressure_mpa": pressure_mpa,
        "n_cylinders": n_cylinders, "eta": eta_used,
        "single_thrust_kn": round(single, 1),
        "resistance_kn": round(s.resistance(), 1),
        "intensity_mpa": round(s.intensity(), 3),
        "note": "公式法估算(非实测)",
    }

if __name__ == "__main__":
    import json
    print(json.dumps(recalc(320), ensure_ascii=False, indent=1))
    print(json.dumps(recalc(360), ensure_ascii=False, indent=1))
