from pathlib import Path


JACK = Path("web/src/views/JackView.vue")


def text():
    return JACK.read_text(encoding="utf-8")


def test_input_changes_invalidate_result():
    s = text()

    assert "watch(" in s
    assert "inputVersion += 1" in s
    assert "result.value = null" in s
    assert "{ deep: true }" in s


def test_new_request_clears_old_result():
    s = text()

    start = s.index("const runDesign = async")
    end = s.index("const clearResult", start)
    block = s[start:end]

    assert "result.value = null" in block
    assert "loading.value = true" in block
    assert (
        block.index("result.value = null")
        < block.index("loading.value = true")
    )


def test_stale_response_cannot_replace_current_result():
    s = text()

    assert "requestInputVersion === inputVersion" in s
    assert "currentRequest === requestVersion" in s
    assert "const nextResult = await postPushJackDesign" in s


def test_manual_clear_invalidates_pending_request():
    s = text()

    start = s.index("const clearResult")
    block = s[start:]

    assert "requestVersion += 1" in block
    assert "result.value = null" in block


def test_engineering_boundary_is_visible():
    s = text()

    assert "计算依据与边界" in s
    assert "压力-面积关系得到的理论计算值" in s
    assert "未引入液压效率修正" in s
    assert "GB/T 2348" in s
    assert "不等于 MT/T94 合规判定" in s
    assert "不参与本阶段力学反算" in s


def test_closeout_does_not_add_premature_traceability():
    s = text()

    assert "F-JACK" not in s
    assert "record_id" not in s
    assert "FormulaCard" not in s
    assert "31.5" not in s
    assert "eta" not in s
