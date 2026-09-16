"""立柱强度校核(W33-D4): 缸筒壁厚三档公式 + 应力校核 + 压杆稳定

壁厚公式口径: 吕晶霞等《液压千斤顶缸筒壁厚的计算及设计研究》(液压气动与密封2013(06))
  引《液压工程手册》三档:
    薄壁 delta/D<=0.08:  delta >= p*D/(2*[sigma])
    中壁 0.08~0.3:       delta >= p*D/(2.3*[sigma]-3*p)
    厚壁 >=0.3(拉美):    delta >= D/2*(sqrt(([sigma]+0.4p)/([sigma]-1.3p))-1)
材料: 27SiMn sigma_s=835MPa —— 孙萌《综采液压支架双伸缩立柱强度分析及疲劳寿命预估研究》
  (同文校核实例: 1.5倍额定载荷中缸最大应力656.7MPa < 835MPa, 安全系数1.27)
压杆稳定: 欧拉公式 Pcr=pi^2*E*I/(mu*L)^2, 安全系数>=2(设计惯例)
诚实边界: 参数化设计计算与校核, 不生成结构设计图样
"""
import math

SOURCE_WALL = "吕晶霞等《液压千斤顶缸筒壁厚的计算及设计研究》引《液压工程手册》三档壁厚公式"
SOURCE_MAT = "孙萌《综采液压支架双伸缩立柱强度分析及疲劳寿命预估研究》: 27SiMn sigma_s=835MPa"

# 材料表(只收有出处的值; 未核到出处的一律 None 并视为"未查到公开参数")
MATERIALS = {
    "27SiMn": {"sigma_s": 835.0, "sigma_b": None, "e_mpa": 206000.0, "source": SOURCE_MAT},
}


def allowable_stress(sigma_s, n=2.0):
    """许用应力 [sigma] = sigma_s / n"""
    if sigma_s <= 0:
        raise ValueError("屈服强度必须为正")
    if not 1.0 <= n <= 5.0:
        raise ValueError(f"安全系数 n={n} 超出常见范围 1.0~5.0")
    return round(sigma_s / n, 1)


def wall_thickness(d_mm, p_mpa, sigma_allow):
    """缸筒壁厚三档公式, 按 delta/D 自动判档
    返回 (delta_mm, regime), regime in {thin, mid, thick}"""
    if not 40 <= d_mm <= 600:
        raise ValueError(f"缸径 {d_mm}mm 超出常见范围 40~600mm")
    if not 1 <= p_mpa <= 400:
        raise ValueError(f"压力 {p_mpa}MPa 超出公式适用范围 1~400MPa")
    if sigma_allow <= 1.3 * p_mpa:
        raise ValueError("许用应力过低([sigma]<=1.3p), 拉美公式无解, 需换材料或降压")
    thin = p_mpa * d_mm / (2 * sigma_allow)
    if thin / d_mm <= 0.08:
        return round(thin, 2), "thin"
    mid = p_mpa * d_mm / (2.3 * sigma_allow - 3 * p_mpa)
    if mid / d_mm <= 0.3:
        return round(mid, 2), "mid"
    thick = d_mm / 2 * (math.sqrt((sigma_allow + 0.4 * p_mpa)
                                  / (sigma_allow - 1.3 * p_mpa)) - 1)
    return round(thick, 2), "thick"


def check_stress(sigma_max, sigma_s):
    """应力校核: 返回 (安全系数, 是否通过)"""
    if sigma_s <= 0 or sigma_max < 0:
        raise ValueError("应力参数非法")
    n = round(sigma_s / sigma_max, 2) if sigma_max > 0 else float("inf")
    return n, sigma_max < sigma_s


def euler_buckling(e_mpa, i_mm4, l_mm, p_kn, mu=1.0):
    """压杆稳定校核: Pcr=pi^2*E*I/(mu*L)^2, 返回 (Pcr_kN, 安全系数, 是否通过>=2)"""
    if e_mpa <= 0 or i_mm4 <= 0 or l_mm <= 0:
        raise ValueError("E/I/L 必须为正")
    if p_kn <= 0:
        raise ValueError("载荷必须为正")
    pcr_n = math.pi**2 * e_mpa * i_mm4 / (mu * l_mm) ** 2
    pcr_kn = round(pcr_n / 1000, 1)
    n = round(pcr_kn / p_kn, 2)
    return pcr_kn, n, n >= 2.0
