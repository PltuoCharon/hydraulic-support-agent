from pathlib import Path


DOC = Path(
    "docs/evidence/w36/"
    "W36_5D4_final_closeout.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_jack_mainline_is_complete_without_standard_overclaim():
    s = text()

    assert "W36 推移千斤顶主链" in s
    assert "COMPLETE" in s
    assert "31.5 MPa 仅为测试输入" in s
    assert "MT/T94 完整缸径/杆径系列核验仍不属于" in s


def test_formula_and_record_deferrals_are_preserved():
    s = text()

    assert "active：16" in s
    assert "legacy_review：8" in s
    assert "没有正式 F-JACK Formula ID" in s
    assert "column_design" in s
    assert "push_jack calculation record" in s


def test_provenance_status_is_not_overclaimed():
    s = text()

    assert "生产实现：" in s
    assert "NOT_IMPLEMENTED" in s
    assert "首轮正式 parameter-level evidence backfill 保留到 W38" in s


def test_eta_and_canopy_semantics_remain_guarded():
    s = text()

    assert "η 不等同于 Ks" in s
    assert "不宣称为机械效率" in s
    assert "支护长度参数" in s
    assert "不得静默把 canopy_len 映射为 Bc" in s


def test_real_browser_e2e_is_complete_but_not_physical_validation():
    s = text()

    assert "/#/calc?m=jack" in s
    assert "@playwright/test + Chromium" in s
    assert "不等同于证明工程公式或物理语义绝对正确" in s


def test_artifacts_governance_is_frozen():
    s = text()

    assert "/artifacts/" in s
    assert "本地 artifacts 未被删除" in s
    assert "5 个关键恢复文件" in s
    assert "SHA256" in s


def test_next_stage_is_w37_not_started_inside_w36_5():
    s = text()

    assert "下一阶段：" in s
    assert "W37：" in s
    assert "不在 W36.5 中开始 W37 功能开发" in s
