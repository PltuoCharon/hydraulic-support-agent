"""W33-D3 立柱缸径反算对拍测试
对拍基准: D=320mm, p=31.5MPa -> 单柱推力 2533kN(老案例)
"""
import math
import pytest

from app.services.calc.column import (
    bore_diameter, column_force, design, round_up_bore, setting_ratio,
)


def test_benchmark_forward_2533():
    # 老案例: D=320mm, 31.5MPa -> 2533kN
    assert column_force(320, 31.5) == pytest.approx(2533.4, abs=0.5)


def test_benchmark_inverse_320():
    # 反算: P=2533kN, n=1, p=31.5, eta=1.0 -> D≈320mm
    d = bore_diameter(2533, 1, 31.5, eta=1.0)
    assert d == pytest.approx(320.0, abs=0.1)


def test_round_up_bore():
    assert round_up_bore(320.0) == 320
    assert round_up_bore(320.1) == 360
    assert round_up_bore(63) == 63
    with pytest.raises(ValueError):
        round_up_bore(501)


def test_setting_ratio_bounds():
    ratio, ok = setting_ratio(75, 100)
    assert ratio == 75.0 and ok
    _, ok_low = setting_ratio(50, 100)
    assert not ok_low
    _, ok_high = setting_ratio(90, 100)
    assert not ok_high


def test_design_full_flow():
    # 需求 2533kN -> 反算 320 -> 圆整 320 -> 实际阻力与需求一致
    r = design(2533, 1, 31.5, eta=1.0, p_set_kn=1900)
    assert r["d_std_mm"] == 320
    assert r["p_actual_kn"] == pytest.approx(2533.4, abs=0.5)
    assert r["setting_ratio_pct"] == pytest.approx(75.0, abs=0.2)
    assert r["setting_ok"]


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        bore_diameter(10, 1, 31.5, eta=1.0)
    with pytest.raises(ValueError):
        column_force(320, 100)
