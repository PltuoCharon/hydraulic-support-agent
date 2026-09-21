from pathlib import Path


DOC = Path(
    "docs/evidence/w36/"
    "W36D1_hydraulic_cylinder_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_hydraulic_cylinder_scope_is_generic():
    s = text()

    for name in (
        "piston_area",
        "annular_area",
        "push_force",
        "pull_force",
        "bore_for_push_force",
        "standard bore rounding",
    ):
        assert name in s


def test_generic_cylinder_has_no_column_eta():
    s = text()

    assert "HydraulicCylinder 不定义 eta" in s
    assert "不得给 HydraulicCylinder 设置隐式 eta 默认值" in s
    assert "液压缸效率" in s
    assert "Ks" in s


def test_column_public_api_is_preserved():
    s = text()

    for name in (
        "column_force",
        "bore_diameter",
        "round_up_bore",
        "setting_ratio",
        "design",
    ):
        assert name in s


def test_fcol003_semantics_are_preserved():
    s = text()

    assert "P_set / P_rated" in s
    assert "P_rated 映射为 p_kn" in s
    assert "不得使用 p_actual_kn 作为分母" in s


def test_legacy_support_calc_is_not_promoted():
    s = text()

    assert "core.support.Cylinder" in s
    assert "app.services.support_calc.recalc" in s
    assert "保持 legacy" in s
    assert "不得把 Support 直接迁入" in s


def test_strength_remains_separate():
    s = text()

    assert "column_strength.py" in s
    assert "保持独立" in s
    assert "不得因为 HydraulicCylinder 建立" in s


def test_provenance_migration_location_is_frozen():
    s = text()

    assert "scripts/migrations/" in s
    assert "004_calculation_records.sql" in s
    assert "parameter_evidence.support_id INT" in s
    assert "utf8mb4_0900_ai_ci" in s


def test_d1_does_not_execute_provenance_migration():
    s = text()

    assert "执行 provenance migration" in s
    assert "创建 evidence_sources" in s
    assert "创建 parameter_evidence" in s
    assert "D2 才开始实现 HydraulicCylinder 基础内核" in s
