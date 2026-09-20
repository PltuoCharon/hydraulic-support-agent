from pathlib import Path


DOC = Path(
    "docs/evidence/w35/"
    "W35D7C_formula_trace_ui_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_d7c_uses_existing_formula_detail_api():
    s = text()
    assert "GET /api/formulas/{formula_id}" in s
    assert "不创建第二份公式数据" in s
    assert "不在前端硬编码公式正文" in s


def test_formula_trace_entry_is_calculation_record_detail():
    s = text()
    assert "计算记录详情 Drawer -> Formula ID" in s
    assert "recordDetail.formula_ids" in s


def test_formula_detail_uses_read_only_dialog():
    s = text()
    assert "Formula Registry 详情使用只读 Dialog" in s
    assert "不使用第二层 Drawer" in s
    assert "关闭公式详情不得关闭计算记录详情" in s


def test_formula_fields_are_frozen():
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


def test_registry_status_is_not_reinterpreted():
    s = text()
    assert "active 保持 active" in s
    assert "legacy_review 保持 legacy_review" in s
    assert "未知未来 status 应显示原值" in s


def test_formula_failure_must_not_fabricate_content():
    s = text()
    assert "不伪造公式内容" in s
    assert "不回退到前端硬编码内容" in s
    assert "必须清空上一条 formula detail" in s


def test_d7c_remains_read_only():
    s = text()
    assert "POST /api/formulas" in s
    assert "PUT /api/formulas" in s
    assert "PATCH /api/formulas" in s
    assert "DELETE /api/formulas" in s
    assert "公式编辑" in s
    assert "计算记录重算" in s


def test_d7c_does_not_claim_parameter_level_evidence():
    s = text()
    assert "参数级 provenance" in s
    assert "D7-C 不实现 parameter_evidence / evidence_sources UI" in s
