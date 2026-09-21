from pathlib import Path


DOC = Path(
    "docs/evidence/w36/"
    "W36D5_push_jack_product_closeout_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_result_must_follow_current_inputs():
    s = text()

    assert "输入变化 -> result = null" in s
    assert "不采用自动重算" in s


def test_failed_request_cannot_leave_old_result():
    s = text()

    assert "每次开始新的计算请求前" in s
    assert "result 必须先清空" in s
    assert "不恢复旧 result" in s


def test_calculation_boundary_is_explicit():
    s = text()

    assert "压力-面积理论计算结果" in s
    assert "未引入液压效率修正" in s
    assert "GB/T 2348" in s
    assert "不等于 MT/T94 合规判定" in s


def test_stroke_remains_user_input():
    s = text()

    assert "stroke_mm 为用户输入" in s
    assert "不参与本阶段力学反算" in s


def test_no_new_traceability_claims():
    s = text()

    assert "F-JACK Formula ID" in s
    assert "calculation record" in s
    assert "record_id" in s
    assert "不得增加" in s


def test_w36_freezes_after_closeout():
    s = text()

    assert "W36 千斤顶功能线冻结" in s
    assert "不得修改 W36-D3 已冻结的纯计算语义" in s
