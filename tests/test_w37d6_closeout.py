from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = ROOT / "docs/evidence/w37/W37D6_closeout.md"


def text():
    return DOC.read_text(encoding="utf-8")


def test_closeout_freezes_overall_design_contract():
    s = text()

    assert "hs.overallDesign.v1" in s

    for value in (
        "RETRIEVED",
        "CALCULATED",
        "USER_INPUT",
        "AI_PROPOSED",
    ):
        assert value in s


def test_closeout_preserves_geometry_semantics():
    s = text()

    assert "support_length_parameter_m" in s
    assert "Bc / control width" in s
    assert "top-beam length" in s
    assert "支护长度参数" in s


def test_closeout_preserves_ks_eta_boundary():
    s = text()

    assert "Ks is not historical column eta" in s
    assert "does not upgrade eta to VERIFIED" in s


def test_closeout_does_not_overclaim_push_jack_traceability():
    s = text()

    assert "no F-JACK Formula ID" in s
    assert "no push-jack Calculation Record" in s
    assert "MT/T 94 compliance" in s


def test_closeout_preserves_three_design_levels():
    s = text()

    assert "reference_support.working_resistance_kn" in s
    assert (
        "support_requirement.required_working_resistance_kn"
        in s
    )
    assert (
        "overall_parameters.design_working_resistance_kn"
        in s
    )


def test_closeout_records_real_e2e_and_cwd_fix():
    s = text()

    assert "Playwright E2E: 1 passed" in s

    assert (
        "cd .. && PYTHONPATH=. venv/bin/python -m uvicorn "
        "app.main:app"
    ) in s

    assert "working-directory bug" in s


def test_closeout_freezes_p0_and_p1_routes():
    s = text()

    assert "Priority P0 research route" in s
    assert "Priority P1 system-completeness route" in s

    assert (
        "P1 shall not indefinitely block the P0 thesis research route"
        in s
    )


def test_closeout_preserves_validation_boundary():
    s = text()

    assert (
        "does not constitute independent physical"
        in s
    )
    assert "field validation" in s
