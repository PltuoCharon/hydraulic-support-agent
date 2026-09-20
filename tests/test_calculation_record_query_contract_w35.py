from pathlib import Path


DOC = Path(
    "docs/evidence/w35/"
    "W35D6_calculation_record_query_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_d6_is_read_only_and_needs_no_schema_change():
    s = text()
    assert "D6 不新增数据库表" in s
    assert "不修改 calculation_records schema" in s
    assert "只执行 SELECT" in s


def test_d6_query_endpoints_are_frozen():
    s = text()
    assert "GET /api/calc/records" in s
    assert "GET /api/calc/records/{record_id}" in s


def test_d6_list_is_bounded_and_deterministic():
    s = text()
    assert "默认 20" in s
    assert "最大 100" in s
    assert "created_at DESC, id DESC" in s


def test_d6_has_summary_and_detail_payloads():
    s = text()
    assert "列表只返回摘要" in s
    assert "单条详情返回" in s
    assert "inputs_snapshot" in s
    assert "outputs_snapshot" in s


def test_d6_json_corruption_fails_explicitly():
    s = text()
    assert "CalculationRecordDataError" in s
    assert "解析失败 → {}" in s
    assert "不得静默伪造历史记录" in s


def test_d6_preserves_provenance_semantics():
    s = text()
    assert "context_source_type 保留数据库原值" in s
    assert "不得重新解释 selected_support" in s


def test_d6_hardens_direct_and_example_context():
    s = text()
    assert "context_snapshot = NULL" in s
    assert "不得保存伪造的上游 provenance" in s
    assert "actual_input_override" in s


def test_d6_does_not_add_replay_semantics():
    s = text()
    assert "查看历史记录不等于重新执行历史计算" in s
    assert "再次计算" in s
    assert "恢复参数" in s
