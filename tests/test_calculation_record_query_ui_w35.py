from pathlib import Path


API = Path("web/src/api/index.js")
VIEW = Path("web/src/views/ColumnView.vue")


def test_d6_frontend_has_read_only_record_apis():
    s = API.read_text(encoding="utf-8")
    assert "getCalculationRecords" in s
    assert "getCalculationRecord" in s
    assert "/api/calc/records" in s


def test_d6_column_view_has_recent_record_list():
    s = VIEW.read_text(encoding="utf-8")
    assert "最近计算记录" in s
    assert "recordList" in s
    assert "loadRecentRecords" in s
    assert "openRecordDetail(row.id)" in s


def test_d6_column_view_has_read_only_detail_drawer():
    s = VIEW.read_text(encoding="utf-8")
    assert "计算记录详情" in s
    assert "recordDrawerOpen" in s
    assert "输入快照" in s
    assert "输出快照" in s
    assert "上下文快照" in s


def test_successful_design_refreshes_record_list():
    s = VIEW.read_text(encoding="utf-8")
    assert "designRes.value = await postColumnDesign(payload)" in s
    assert "loadRecentRecords()" in s


def test_unknown_context_source_is_not_silently_reinterpreted():
    s = VIEW.read_text(encoding="utf-8")
    assert "return map[value] || value || '无上游上下文'" in s


def test_d6_ui_does_not_add_record_mutation_actions():
    s = VIEW.read_text(encoding="utf-8")
    assert "deleteCalculationRecord" not in s
    assert "restoreCalculationRecord" not in s
    assert "rerunCalculationRecord" not in s
