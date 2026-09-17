from pathlib import Path


DOCS = [
    Path("docs/evidence/formulas/W34D2_参数分类表.md"),
    Path("docs/evidence/formulas/W34D2_公式链关系.md"),
    Path("docs/evidence/formulas/W34D2_历史公式裁定.md"),
]


def test_formula_docs_have_no_shell_paste_artifacts():
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
                f"{path} contains shell/paste artifact: {token!r}"
            )


def test_formula_docs_required_sections_exist():
    contents = {
        p.name: p.read_text(encoding="utf-8")
        for p in DOCS
    }

    assert "参数治理规则" in contents["W34D2_参数分类表.md"]

    chain = contents["W34D2_公式链关系.md"]
    assert "W33 新设计计算链" in chain
    assert "历史 requirement 链" in chain
    assert "历史 /recalc 链" in chain
    assert "support_calc 链" in chain

    decision = contents["W34D2_历史公式裁定.md"]
    assert "Active 主线" in decision
    assert "/api/requirement" in decision
    assert "/api/recalc" in decision
    assert "support_calc.py" in decision
