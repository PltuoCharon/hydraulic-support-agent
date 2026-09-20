from pathlib import Path


DOC = Path(
    "docs/evidence/w35/"
    "W35D3_设计参数传递契约.md"
)


def content():
    return DOC.read_text(encoding="utf-8")


def test_transfer_sources_are_explicit():
    s = content()

    assert "selected_support" in s
    assert "calculated_requirement" in s
    assert "user_input" in s


def test_selected_support_only_passes_safe_context():
    s = content()

    assert "support_model" in s
    assert "working_resistance" in s
    assert "target_resistance_kn" in s
    assert "未知保持 NULL" in s


def test_eta_and_ks_must_not_be_merged():
    s = content()

    assert "`eta != Ks`" in s
    assert "不允许从 Ks 自动映射" in s


def test_example_defaults_are_not_design_provenance():
    s = content()

    assert "2533 kN" in s
    assert "31.5 MPa" in s
    assert "只允许作为" in s
    assert "`计算示例`" in s


def test_d3_does_not_auto_infer_design_parameters():
    s = content()

    assert "自动推断立柱数量" in s
    assert "自动推断泵站压力" in s
    assert "自动补齐初撑力" in s
