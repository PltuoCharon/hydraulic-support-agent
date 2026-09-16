"""q_need 三式对拍测试 —— W33-D1
对拍基准: 纵帅等谢桥矿实例(原文 pdftotext 提取并逐项验算)
  p1: K1=6, hm=6m, γ=25kN/m³ → 0.90 MPa
  p2: K=2, L1=25m → 0.70 MPa
  p3: hm=6, Lp=15m, Bc=5m, N=1.33 → 0.82 MPa
"""
import pytest
from app.services.calc.q_need import p1_load, p2_weighting_step, p3_statistical, estimate


def test_xieqiao_p1():
    assert p1_load(hm=6.0, gamma=25.0, k1=6.0) == pytest.approx(0.90, abs=1e-3)


def test_xieqiao_p2():
    assert p2_weighting_step(l1=25, k=2.0) == pytest.approx(0.70, abs=1e-3)


def test_xieqiao_p3():
    assert p3_statistical(hm=6.0, lp=15, bc=5, n=1.33) == pytest.approx(0.82, abs=5e-3)


def test_xieqiao_estimate_max_rule():
    r = estimate(hm=6.0, l1=25, lp=15, bc=5, n=1.33)
    assert r["q_need_mpa"] == pytest.approx(0.90, abs=1e-3)
    assert r["governing"] == "p1"
    assert r["source"]


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        p1_load(hm=20.0)
    with pytest.raises(ValueError):
        p2_weighting_step(l1=200)
    with pytest.raises(ValueError):
        p3_statistical(hm=6.0, lp=15, bc=5, n=99)
