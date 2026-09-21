from pathlib import Path


DOC = Path(
    "docs/evidence/w36/"
    "W36D4_push_jack_api_ui_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_api_path_and_core_are_frozen():
    s = text()

    assert "POST /api/calc/push-jack-design" in s
    assert "push_jack_design()" in s
    assert "不得在 Router 或 Vue 页面复制" in s


def test_pressure_has_no_default():
    s = text()

    assert "pressure_mpa 无默认值" in s
    assert "不得默认 31.5 MPa" in s


def test_api_preserves_existing_response_style():
    s = text()

    assert "HTTP 200" in s
    assert '"code": 1' in s
    assert "HTTP 422" in s


def test_no_record_or_formula_registry_yet():
    s = text()

    assert "不调用" in s
    assert "create_calculation_record()" in s
    assert "不增加 F-JACK-*" in s
    assert "不显示 FormulaCard" in s


def test_frontend_uses_existing_api_unwrap_semantics():
    s = text()

    assert "postPushJackDesign(data)" in s
    assert "直接接收计算结果" in s
    assert "result.code" in s
    assert "result.data" in s


def test_pull_requirement_needs_rod():
    s = text()

    assert "pull_required_kn" in s
    assert "未填写 rod_mm" in s
    assert "前端应阻止提交" in s


def test_mt_t94_warning_is_visible():
    s = text()

    assert "mt_t94_verified == false" in s
    assert "尚未完成 MT/T94" in s
    assert "候选缸径" in s


def test_calc_center_opens_jack_without_new_router():
    s = text()

    assert "validModules 增加" in s
    assert "/calc?m=jack" in s
    assert "不新增新的 Vue Router path" in s


def test_ui_does_not_claim_standard_compliance():
    s = text()

    assert "MT/T94标准缸径" in s
    assert "不得把 bore_candidate_mm" in s
    assert "宣称 MT/T94 已核验" in s
