from pathlib import Path


DOC = Path(
    "docs/evidence/w36/"
    "W36_5D3_e2e_artifacts_contract.md"
)


def text():
    return DOC.read_text(encoding="utf-8")


def test_playwright_stack_is_frozen():
    s = text()

    assert "@playwright/test + Chromium" in s
    assert "仅作为 web 开发依赖" in s


def test_e2e_must_use_real_system_chain():
    s = text()

    assert "Vite :5173" in s
    assert "FastAPI :8000" in s
    assert "不得 mock" in s
    assert "/api/calc/push-jack-design" in s


def test_jack_benchmark_is_frozen():
    s = text()

    assert "push_required_kn = 300" in s
    assert "pressure_mpa = 31.5" in s
    assert "候选缸径显示 125 mm" in s
    assert "推力需求校核显示“满足”" in s


def test_test_pressure_is_not_product_default():
    s = text()

    assert "31.5 MPa 仅为 E2E 测试输入" in s
    assert "压力必须显式输入" in s


def test_result_invalidation_is_real_browser_requirement():
    s = text()

    assert "不得再次点击计算" in s
    assert "旧计算结果立即消失" in s
    assert "deep watch" in s


def test_artifacts_are_ignored_not_deleted():
    s = text()

    assert "忽略 /artifacts/" in s
    assert "不删除本地 artifacts" in s
    assert "不执行 rm -rf artifacts" in s
    assert "SHA256 manifest" in s


def test_w37_is_out_of_scope():
    s = text()

    assert "不得开始 W37" in s
