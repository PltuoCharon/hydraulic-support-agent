from pathlib import Path


DOC = Path("docs/evidence/w35/W35D5_column_semantics_contract.md")


def text():
    return DOC.read_text(encoding="utf-8")


def test_d5_eta_is_explicit_provisional_parameter():
    s = text()
    assert "历史立柱修正系数 η（待核）" in s
    assert "eta != Ks" in s
    assert "eta 不得称为“支撑效率”" in s
    assert "eta 必须显式输入" in s
    assert "不得隐式使用 eta=0.9" in s


def test_d5_keeps_legacy_eta_separate():
    s = text()
    assert "legacy 元数据" in s
    assert "不修改 legacy support_calc 的行为" in s
    assert "active column_design 与 legacy support_calc" in s


def test_d5_pressure_and_column_count_terms_are_canonical():
    s = text()
    assert "canonical label: 承载立柱根数" in s
    assert "canonical label: 立柱工作压力" in s


def test_d5_does_not_overattribute_formula_to_bore_standard():
    s = text()
    assert "GB/T 2348 只用于标准缸径系列来源" in s
    assert "整个含 eta 的公式" in s


def test_d5_avoids_actual_load_overclaim():
    s = text()
    assert "UI 不得把 P_calc 表述为“实际承载力”" in s
    assert "圆整后计算承载力" in s


def test_d5_setting_ratio_uses_existing_verified_evidence():
    s = text()
    assert "60%~85%" in s
    assert "W35-D2 已核标准证据" in s
    assert "不再只写“设计惯例”" in s


def test_d5_example_is_not_engineering_default():
    s = text()
    assert "这些值只属于 example，不是工程默认值" in s
    assert "eta required" in s


def test_d5_scope_remains_narrow():
    s = text()
    assert "不新增 CAD / FEA" in s
    assert "不重构强度校核" in s
    assert "eta -> Ks 映射" in s
