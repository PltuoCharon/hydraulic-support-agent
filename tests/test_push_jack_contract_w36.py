from pathlib import Path


DOC = Path(
    "docs/evidence/w36/"
    "W36D3_push_jack_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_push_jack_reuses_generic_cylinder():
    s = text()

    assert "hydraulic_cylinder.py" in s
    assert "push_force" in s
    assert "pull_force" in s
    assert "bore_for_push_force" in s


def test_pressure_and_rod_have_no_implicit_defaults():
    s = text()

    assert "pressure_mpa 必须由用户或上游工程参数显式提供" in s
    assert "不猜测活塞杆直径" in s
    assert "不得自动使用 31.5 MPa" in s


def test_stroke_is_input_not_calculated():
    s = text()

    assert "stroke_mm 当前仅作为显式工程输入保存" in s
    assert "不得根据支架型号或缸径自动推断" in s


def test_working_direction_is_not_assumed():
    s = text()

    assert "不能仅根据名称推断" in s
    assert "推输送机一定使用无杆腔" in s
    assert "具体工作方向取决于推移机构连接拓扑" in s


def test_standard_boundaries_are_recorded():
    s = text()

    assert "MT97" in s
    assert "MT/T94" in s
    assert "360 kN" in s
    assert "2.5~4 倍" in s


def test_no_new_formula_ids_in_d3():
    s = text()

    assert "当前 Formula Registry 没有 jack 专用 Formula ID" in s
    assert "不得直接把 F-COL-002 当作推移千斤顶正式 Formula ID" in s
    assert "W36-D3 不创建" in s


def test_calculation_record_is_deferred():
    s = text()

    assert "ALLOWED_CALC_TYPES" in s
    assert "column_design" in s
    assert "W36-D3 不写入" in s
    assert "push_jack_design" in s


def test_first_service_scope_is_small():
    s = text()

    assert "push_jack_design()" in s
    assert "无 rod_mm 时不生成拉力结果" in s
    assert "API、页面、Calculation Record 和 Formula Registry" in s


def test_candidate_bore_is_not_claimed_as_mt_t94_verified():
    s = text()

    assert "bore_candidate_mm" in s
    assert "GB/T 2348" in s
    assert "不等同于 MT/T94 合规判定" in s
    assert "mt_t94_verified = false" in s
