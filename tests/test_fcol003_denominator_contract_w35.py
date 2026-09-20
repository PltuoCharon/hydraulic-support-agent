from pathlib import Path


DOC = Path(
    "docs/evidence/w35/"
    "W35D7A_fcol003_denominator_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_fcol003_denominator_is_rated_working_resistance():
    s = text()
    assert "r = P_set / P_rated" in s
    assert "额定工作阻力" in s


def test_column_design_maps_denominator_to_p_kn():
    s = text()
    assert "F-COL-003 denominator = p_kn" in s
    assert "setting_ratio(p_set_kn, p_kn)" in s


def test_p_actual_is_not_fcol003_denominator():
    s = text()
    assert "p_actual 不等于 P_rated" in s
    assert "不得作为 F-COL-003 分母" in s


def test_discriminating_case_is_frozen():
    s = text()
    assert "p_kn = 3000 kN" in s
    assert "p_set_kn = 2400 kN" in s
    assert "setting_ratio_pct == 80.0" in s
    assert "3206.3" in s


def test_d7a_scope_does_not_redefine_other_semantics():
    s = text()
    assert "修改 eta 语义" in s
    assert "修改 F-COL-001" in s
    assert "修改 F-COL-002" in s
    assert "D7-A 仅修正 F-COL-003 denominator" in s
