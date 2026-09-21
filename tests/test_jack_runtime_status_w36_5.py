from pathlib import Path


VIEW = Path("web/src/views/JackView.vue")


def text():
    return VIEW.read_text(encoding="utf-8")


def test_push_check_uses_literal_vue_strings():
    s = text()

    assert "result.push_ok ? 'success' : 'danger'" in s
    assert "result.push_ok ? '满足' : '不满足'" in s
    assert "result.push_ok ? success : danger" not in s


def test_pull_check_uses_literal_vue_strings():
    s = text()

    assert "result.pull_ok ? 'success' : 'danger'" in s
    assert "result.pull_ok ? '满足' : '不满足'" in s
    assert "result.pull_ok ? success : danger" not in s
