from pathlib import Path


ROOT = Path("docs/evidence/w35")


def read(name):
    return (ROOT / name).read_text(
        encoding="utf-8"
    )


def test_w35d1_audit_records_real_boundaries():
    s = read("W35D1_现状审计.md")

    assert "param_dependencies 共 23 条" in s
    assert "support_parts 共 83 条" in s
    assert "knowledge_chunks 共 9 条" in s

    assert "整条型号记录状态" in s
    assert "字段级证据链" in s
    assert "支护长度参数" in s


def test_schema_has_independent_status_axes():
    s = read("W35D1_provenance_schema.md")

    for value in (
        "original",
        "supplemented",
        "calculated",
        "estimated",
        "missing",
    ):
        assert value in s

    for value in (
        "verified",
        "provisional",
        "conflicting",
        "unverified",
    ):
        assert value in s

    assert "value_min" in s
    assert "value_max" in s
    assert "formula_id" in s
    assert "is_selected" in s
    assert "不建立 FK" in s


def test_migration_is_semi_automatic():
    s = read("W35D1_迁移策略.md")

    assert "规则提取" in s
    assert "候选断言" in s
    assert "人工审核" in s

    assert "整行全部字段标记 estimated" in s
    assert "不得删除旧 source" in s
    assert "增量迁移" in s


def test_ddl_is_non_destructive_draft():
    s = read(
        "W35D1_provenance_migration_draft.sql"
    )

    assert "DRAFT ONLY" in s
    assert "CREATE TABLE IF NOT EXISTS evidence_sources" in s
    assert "CREATE TABLE IF NOT EXISTS parameter_evidence" in s
    assert "value_origin" in s
    assert "verification_status" in s
    assert "formula_id VARCHAR" in s
    assert "is_selected" in s

    executable = "\n".join(
        line
        for line in s.splitlines()
        if not line.strip().startswith("--")
    )

    assert "ALTER TABLE support_models" not in executable
    assert "INSERT INTO" not in executable
    assert "UPDATE support_models" not in executable
    assert "DELETE FROM" not in executable
