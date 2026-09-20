from pathlib import Path


RESULT = Path("web/src/views/ResultView.vue")
COLUMN = Path("web/src/views/ColumnView.vue")
TRANSFER = Path("web/src/utils/designTransfer.js")


def test_transfer_uses_session_storage():
    s = TRANSFER.read_text(encoding="utf-8")

    assert "sessionStorage" in s
    assert "selected_support" in s
    assert "calculated_requirement" in s


def test_result_builds_selected_support_context():
    s = RESULT.read_text(encoding="utf-8")

    assert "writeDesignTransfer" in s
    assert "goColumnDesign(it)" in s
    assert "source_type" in s
    assert "selected_support" in s
    assert "support_source" in s
    assert "support_status" in s
    assert "ctx" in s


def test_old_direct_column_jump_is_removed():
    s = RESULT.read_text(encoding="utf-8")

    assert "router.push('/calc?m=column')" not in s
    assert "goColumnDesign(it)" in s


def test_column_defaults_are_not_hidden_design_data():
    s = COLUMN.read_text(encoding="utf-8")

    assert "n: null" in s
    assert "p_mpa: null" in s
    assert "eta: null" in s
    assert "p_set_kn: null" in s
    assert "const enableSetting = ref(false)" in s


def test_column_loads_and_confirms_transfer_context():
    s = COLUMN.read_text(encoding="utf-8")

    assert "readDesignTransfer()" in s
    assert "transferPayload?.source_type === route.query.ctx" in s
    assert "confirmDesignContext" in s
    assert "contextConfirmed" in s
    assert "designContext.value?.target?.resistance_kn" in s


def test_example_values_are_explicit_example_only():
    s = COLUMN.read_text(encoding="utf-8")

    assert "const fillDesignExample" in s
    assert "clearDesignTransfer()" in s
    assert "designForm.p_kn = 2533" in s
    assert "designForm.p_mpa = 31.5" in s
    assert "designForm.eta = 1.0" in s
    assert "designForm.p_set_kn = 1900" in s


def test_design_call_has_readiness_guard():
    s = COLUMN.read_text(encoding="utf-8")

    assert "const designReady = computed" in s
    assert "if (designReady.value === false) return" in s
    assert ':disabled="designReady === false"' in s


def test_column_shows_design_context():
    s = COLUMN.read_text(encoding="utf-8")

    assert 'class="design-context"' in s
    assert "confirmDesignContext" in s
    assert "designContext.provenance?.source_text" in s
    assert "designContext.provenance?.data_status" in s
