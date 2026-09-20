from pathlib import Path


COLUMN = Path("web/src/views/ColumnView.vue")


def source():
    return COLUMN.read_text(encoding="utf-8")


def test_column_design_sends_record_metadata():
    s = source()

    assert 'run_mode: runMode' in s
    assert 'context_source_type:' in s
    assert 'context_confirmed:' in s
    assert 'context_snapshot:' in s


def test_example_mode_is_explicit_and_value_guarded():
    s = source()

    assert 'const designExampleLoaded = ref(false)' in s
    assert 'designExampleLoaded.value = true' in s
    assert 'const designExampleIsCurrent' in s
    assert '"example"' in s
    assert '"engineering"' in s


def test_transferred_context_is_sent_to_backend():
    s = source()

    assert 'designContext.value?.source_type' in s
    assert 'contextConfirmed.value' in s
    assert 'designContext.value,' in s


def test_record_id_is_visible_in_result():
    s = source()

    assert 'designRes.record_id != null' in s
    assert '#{{ designRes.record_id }}' in s
