from pathlib import Path


API = Path("web/src/api/index.js")
CENTER = Path("web/src/views/CalcCenterView.vue")
JACK = Path("web/src/views/JackView.vue")


def test_push_jack_api_wrapper_exists():
    s = API.read_text(encoding="utf-8")

    assert "postPushJackDesign" in s
    assert "/api/calc/push-jack-design" in s


def test_calc_center_enables_jack():
    s = CENTER.read_text(encoding="utf-8")

    assert "import JackView" in s
    assert "'jack'" in s
    assert "mod === 'jack'" in s

    block = s[
        s.index("key: 'jack'") - 40:
        s.index("key: 'valve'")
    ]
    assert "disabled: true" not in block


def test_jack_inputs_have_no_engineering_defaults():
    s = JACK.read_text(encoding="utf-8")

    assert "push_required_kn: null" in s
    assert "pressure_mpa: null" in s
    assert "rod_mm: null" in s
    assert "stroke_mm: null" in s
    assert "31.5" not in s


def test_pull_requirement_dependency_is_visible():
    s = JACK.read_text(encoding="utf-8")

    assert "pullNeedsRod" in s
    assert "必须同时提供活塞杆直径" in s
    assert ':disabled="!ready"' in s


def test_mt_t94_warning_is_visible():
    s = JACK.read_text(encoding="utf-8")

    assert "MT/T94 尺寸系列尚未核验" in s
    assert "GB/T 2348" in s
    assert "尚未完成 MT/T94" in s
    assert "候选缸径" in s


def test_jack_ui_has_no_premature_traceability():
    s = JACK.read_text(encoding="utf-8")

    assert "F-JACK" not in s
    assert "record_id" not in s
    assert "FormulaCard" not in s
    assert "eta" not in s
