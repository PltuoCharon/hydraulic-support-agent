from pathlib import Path
import csv


DOCS = [
    Path("docs/ui/W34D3_信息架构.md"),
    Path("docs/ui/W34D3_ModifyView迁移分析.md"),
    Path("docs/ui/W34D3_页面视觉规范_v1.md"),
]


def test_ui_docs_have_no_shell_artifacts():
    forbidden = [
        "\nEOF ",
        "\nEOF\n",
        "zhangyongbo@",
        "(venv)",
    ]

    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (
                f"{path} contains shell artifact: {token!r}"
            )


def test_ui_architecture_required_sections():
    ia = Path(
        "docs/ui/W34D3_信息架构.md"
    ).read_text(encoding="utf-8")

    for name in [
        "工作台",
        "智能选型",
        "支架数据库",
        "设计计算",
        "图纸·模型·仿真",
        "知识与证据",
        "AgentDock",
    ]:
        assert name in ia


def test_route_migration_csv_is_valid():
    path = Path("docs/ui/W34D3_路由迁移表.csv")

    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows
    assert any(
        r["current_route"] == "/modify"
        and r["action"] == "deprecate_after_migration"
        for r in rows
    )
