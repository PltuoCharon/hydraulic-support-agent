"""W33-D4 立柱强度校核对拍测试
基准1(薄壁档, 公式复现算例): D=200, p=43.4MPa(吕晶霞文一级缸安全阀开启压力),
  [sigma]=835/2=417.5 -> delta=10.40mm, delta/D=0.052 薄壁档
基准2(中壁档构造例): D=100, p=80, [sigma]=417.5 -> delta=11.11mm, delta/D=0.111
基准3(厚壁档构造例): D=100, p=200, [sigma]=417.5 -> delta=38.86mm, delta/D=0.389
基准4(孙萌论文校核实例): 656.7MPa vs 835MPa -> 通过, 安全系数1.27
"""
import math
import pytest

from app.services.calc.column_strength import (
    MATERIALS, allowable_stress, check_stress, euler_buckling, wall_thickness,
)

SIG = allowable_stress(835, 2.0)  # 417.5


def test_allowable_stress():
    assert SIG == 417.5
    with pytest.raises(ValueError):
        allowable_stress(835, 0.5)


def test_wall_thin_regime():
    d, regime = wall_thickness(200, 43.4, SIG)
    assert d == pytest.approx(10.40, abs=0.01)
    assert regime == "thin"


def test_wall_mid_regime():
    d, regime = wall_thickness(100, 80, SIG)
    assert d == pytest.approx(11.11, abs=0.01)
    assert regime == "mid"


def test_wall_thick_regime():
    d, regime = wall_thickness(100, 200, SIG)
    assert d == pytest.approx(38.86, abs=0.01)
    assert regime == "thick"


def test_wall_no_solution_raises():
    with pytest.raises(ValueError):
        wall_thickness(100, 400, SIG)  # 1.3*400=520 > 417.5


def test_check_stress_sunmeng_case():
    n, ok = check_stress(656.7, 835)
    assert n == pytest.approx(1.27, abs=0.01)
    assert ok
    _, not_ok = check_stress(900, 835)
    assert not not_ok


def test_materials_honesty():
    # 27SiMn 屈服强度有出处; 抗拉强度未核到出处必须为 None(未查到公开参数)
    m = MATERIALS["27SiMn"]
    assert m["sigma_s"] == 835.0
    assert m["sigma_b"] is None


def test_euler_buckling():
    # 构造例: E=206000MPa, I=1e7 mm4, L=2000mm -> Pcr=pi^2*206000*1e7/2000^2=5082.8kN
    pcr, n, ok = euler_buckling(206000, 1e7, 2000, 2000)
    assert pcr == pytest.approx(5082.8, abs=0.1)
    assert n == pytest.approx(2.54, abs=0.01)
    assert ok
    _, _, not_ok = euler_buckling(206000, 1e7, 2000, 3000)
    assert not not_ok
