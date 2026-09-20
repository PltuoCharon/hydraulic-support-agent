from pathlib import Path


DOC = Path("docs/evidence/w35/W35D4_calculation_record_contract.md")


def text():
    return DOC.read_text(encoding="utf-8")


def test_d4_scope_is_column_design_only():
    s = text()
    assert "column_design" in s
    assert "CAD / FEA / 数字孪生任务记录" in s
    assert "working_conditions 自动新增案例" in s


def test_d4_keeps_calculation_core_pure():
    s = text()
    assert "column.py：保持纯计算，不写数据库" in s
    assert "失败请求不得写入正式成功记录" in s


def test_d4_record_schema_has_traceability_snapshots():
    s = text()
    for token in (
        "record_version",
        "calc_type",
        "run_mode",
        "formula_ids",
        "inputs_snapshot",
        "outputs_snapshot",
        "context_source_type",
        "context_confirmed",
        "context_snapshot",
        "created_at",
    ):
        assert token in s


def test_d4_formula_ids_are_conditional():
    s = text()
    assert "F-COL-001：总是记录" in s
    assert "F-COL-002：总是记录" in s
    assert "F-COL-003：仅当 p_set_kn 不为 null 时记录" in s
    assert "不伪造新的 formula_id" in s


def test_d4_context_sources_are_explicit():
    s = text()
    assert "selected_support / calculated_requirement / user_input / NULL" in s
    assert "context_confirmed 为 NULL" in s
    assert "run_mode=example" in s


def test_d4_does_not_redefine_eta():
    s = text()
    assert "D4 不解决 eta 的物理定义" in s
    assert "不把 eta 与 Ks 等同" in s


def test_d4_prevents_false_selected_support_provenance():
    s = text()
    assert "如果用户修改了从推荐支架带入的 p_kn" in s
    assert "不得继续声称该 p_kn 来自原推荐值" in s


def test_d4_api_returns_record_id_without_overclaim():
    s = text()
    assert "新增 record_id" in s
    assert "不代表制造级设计认证" in s
