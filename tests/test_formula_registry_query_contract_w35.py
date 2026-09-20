from pathlib import Path


DOC = Path(
    "docs/evidence/w35/"
    "W35D7B_formula_registry_query_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_d7b_has_read_only_formula_endpoints():
    s = text()
    assert "GET /api/formulas" in s
    assert "GET /api/formulas/{formula_id}" in s
    assert "D7-B 查询接口只读" in s


def test_registry_csv_remains_single_source():
    s = text()
    assert "docs/evidence/formulas/W34D2_Formula_Registry.csv" in s
    assert "不创建第二份 Formula Registry" in s
    assert "不把 Registry 搬入数据库" in s


def test_detail_fields_are_frozen():
    s = text()
    for field in (
        "formula_id",
        "module",
        "name",
        "status",
        "formula",
        "input_vars",
        "output",
        "unit",
        "source",
        "verification",
        "current_callers",
        "notes",
    ):
        assert field in s


def test_legacy_review_must_remain_visible():
    s = text()
    assert "不得默认隐藏 legacy_review" in s
    assert "legacy_review 也按 Registry 原状态返回" in s
    assert "把 legacy_review 自动改为 active" in s


def test_registry_corruption_must_fail_explicitly():
    s = text()
    assert "formula_id 非空" in s
    assert "formula_id 唯一" in s
    assert "必须显式失败" in s
    assert "静默跳过冲突记录" in s


def test_unknown_formula_has_explicit_not_found_semantics():
    s = text()
    assert "未知 formula_id" in s
    assert "formula not found" in s


def test_d7b_does_not_claim_parameter_level_provenance():
    s = text()
    assert "参数级 provenance" in s
    assert "D7-B 不创建对应数据库表" in s
    assert "前端追溯属于后续 D7-C" in s
