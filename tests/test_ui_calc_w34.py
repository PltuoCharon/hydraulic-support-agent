from pathlib import Path


def read(path):
    return Path(path).read_text(
        encoding="utf-8"
    )


def test_calc_center_uses_single_shell_navigation():
    s = read(
        "web/src/views/CalcCenterView.vue"
    )

    assert "PageHeader" in s
    assert "参数化设计辅助" in s
    assert "module-nav" in s

    assert "<el-aside" not in s
    assert "100vh - 60px" not in s


def test_qneed_has_formula_and_correct_semantics():
    s = read(
        "web/src/views/QNeedView.vue"
    )

    assert "FormulaCard" in s
    assert "q_need = max(p1, p2, p3)" in s

    assert "老顶初次来压步距 L1" in s
    assert "基本顶周期来压步距 Lp" in s
    assert "控顶宽度 Bc" in s
    assert "直接顶充填系数 N" in s

    assert "需求支护强度" in s
    assert "不等同于整架工作阻力" in s


def test_column_hides_internal_development_labels():
    s = read(
        "web/src/views/ColumnView.vue"
    )

    assert "填入D3基准" not in s
    assert "填入D4复核示例" not in s

    assert "填入计算示例" in s
    assert "填入校核示例" in s

    assert "FormulaCard" in s
    assert "EmptyState" in s


def test_strength_allowable_stress_boundary_is_visible():
    s = read(
        "web/src/views/ColumnView.vue"
    )

    assert "σs / n" in s
    assert "计算脚手架" in s
    assert "不得直接作为制造级壁厚设计依据" in s
