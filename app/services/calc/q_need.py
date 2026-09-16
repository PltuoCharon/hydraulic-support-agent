"""支护需求估算器(围岩侧): q_need 三式并算 —— W33-D1
公式出处: 纵帅等《大采高综采工作面液压支架选型研究及应用》谢桥矿实例
  p1 载荷估算法:     p1 = K1·hm·γ                      [kN/m²=kPa]
  p2 老顶来压步距法: p2 = K·(15+0.8·L1)×10⁻²            [MPa]
  p3 统计公式法:     p3 = 72.3·hm+4.5·Lp+78.9·Bc−10.24·N−62.1  [kPa]
取值规则(原文): 支护强度取三式最大值。
单位约定: 对外一律返回 MPa(3位小数)。
诚实边界: 本模块产出"参数整定层面的需求估算", 非围岩结构设计。"""

SRC = "纵帅等《大采高综采工作面液压支架选型研究及应用》谢桥矿实例"


def p1_load(hm: float, gamma: float = 25.0, k1: float = 6.0) -> float:
    """载荷估算法 p1=K1·hm·γ, 返回 MPa。
    hm 采高 m; gamma 顶板岩层容重 kN/m³; k1 影响系数(行业惯例6~8倍采高岩柱)。"""
    if not (0.5 <= hm <= 10):
        raise ValueError(f"采高 {hm}m 超出常见范围 0.5~10m")
    if not (15 <= gamma <= 35):
        raise ValueError(f"容重 {gamma}kN/m³ 超出常见范围 15~35")
    if not (4 <= k1 <= 10):
        raise ValueError(f"影响系数 {k1} 超出常见范围 4~10")
    return round(k1 * hm * gamma / 1000.0, 3)


def p2_weighting_step(l1: float, k: float = 2.0) -> float:
    """老顶来压步距法 p2=K(15+0.8·L1)×10⁻², 返回 MPa。
    l1 老顶初次来压步距 m; k 动载荷系数。"""
    if not (5 <= l1 <= 100):
        raise ValueError(f"初次来压步距 {l1}m 超出常见范围 5~100m")
    if not (1.0 <= k <= 3.0):
        raise ValueError(f"动载荷系数 {k} 超出常见范围 1.0~3.0")
    return round(k * (15 + 0.8 * l1) * 1e-2, 3)


def p3_statistical(hm: float, lp: float, bc: float, n: float) -> float:
    """统计公式法 p3=72.3hm+4.5Lp+78.9Bc−10.24N−62.1 (kPa), 返回 MPa。
    lp 基本顶周期来压步距 m; bc 控顶宽度 m; n 直接顶充填系数（直接顶厚度/采高）。"""
    if not (0.5 <= hm <= 10):
        raise ValueError(f"采高 {hm}m 超出常见范围 0.5~10m")
    if not (3 <= lp <= 60):
        raise ValueError(f"周期来压步距 {lp}m 超出常见范围 3~60m")
    if not (1 <= bc <= 15):
        raise ValueError(f"控顶宽度 {bc}m 超出常见范围 1~15m")
    if not (0.2 <= n <= 5):
        raise ValueError(f"直接顶充填系数 {n} 超出常见范围 0.2~5")
    kpa = 72.3 * hm + 4.5 * lp + 78.9 * bc - 10.24 * n - 62.1
    return round(kpa / 1000.0, 3)


def estimate(hm: float, l1: float, lp: float, bc: float, n: float,
             gamma: float = 25.0, k1: float = 6.0, k: float = 2.0) -> dict:
    """三式并算, 取最大值为需求支护强度 q_need。"""
    r1 = p1_load(hm, gamma, k1)
    r2 = p2_weighting_step(l1, k)
    r3 = p3_statistical(hm, lp, bc, n)
    vals = {"p1": r1, "p2": r2, "p3": r3}
    gov = max(vals, key=vals.get)
    return {
        "p1_mpa": r1, "p2_mpa": r2, "p3_mpa": r3,
        "q_need_mpa": vals[gov], "governing": gov,
        "inputs": {"hm": hm, "gamma": gamma, "k1": k1,
                   "l1": l1, "k": k, "lp": lp, "bc": bc, "n": n},
        "rule": "三式并算取最大值(纵帅等谢桥矿实例同口径)",
        "source": SRC,
    }


if __name__ == "__main__":
    import json
    # 谢桥矿实例: 期望 p1=0.90 p2=0.70 p3=0.82, q_need=0.90(p1)
    print(json.dumps(estimate(hm=6.0, l1=25, lp=15, bc=5, n=1.33),
                     ensure_ascii=False, indent=1))
