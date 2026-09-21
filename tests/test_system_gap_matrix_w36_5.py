from pathlib import Path


DOC = Path(
    "docs/evidence/w36/"
    "W36_5D2_system_gap_matrix.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_status_vocabulary_is_frozen():
    s = text()

    for status in (
        "COMPLETE",
        "PARTIAL",
        "INTENTIONALLY_DEFERRED",
        "EVIDENCE_GAP",
        "TECH_DEBT",
        "NOT_IMPLEMENTED",
    ):
        assert status in s


def test_provenance_is_not_overclaimed():
    s = text()

    assert "Production implementation" in s
    assert "NOT_IMPLEMENTED" in s
    assert "正式 scripts/migrations provenance migration" in s


def test_jack_record_is_explicitly_deferred():
    s = text()

    assert "Push Jack" in s
    assert "ALLOWED_CALC_TYPES" in s
    assert "INTENTIONALLY_DEFERRED" in s


def test_canopy_len_semantics_remain_guarded():
    s = text()

    assert "canopy_len = 支护长度参数" in s
    assert "不得自动解释为" in s
    assert "控顶宽度" in s


def test_eta_evidence_gap_is_preserved():
    s = text()

    assert "历史立柱修正系数 η" in s
    assert "不等同于 Ks" in s
    assert "不宣称为机械效率或液压效率" in s


def test_real_browser_e2e_is_declared_missing():
    s = text()

    assert "浏览器 E2E" in s
    assert "NOT_IMPLEMENTED" in s
    assert "/calc?m=jack" in s


def test_artifacts_are_not_deleted_blindly():
    s = text()

    assert "不得直接 rm -rf artifacts" in s
    assert "W36.5-D3" in s
