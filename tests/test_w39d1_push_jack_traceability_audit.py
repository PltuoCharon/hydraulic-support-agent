import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOC = (
    ROOT
    / "docs/evidence/w39/W39D1_push_jack_traceability_audit.md"
)

REGISTRY = (
    ROOT
    / "docs/evidence/formulas/W34D2_Formula_Registry.csv"
)


def text():
    return DOC.read_text(encoding="utf-8")


def normalized():
    return " ".join(text().split())


def test_audit_distinguishes_router_from_core():
    s = text()

    assert "app/services/calc/push_jack.py" in s
    assert "app/routers/calc.py" in s

    assert (
        "different interfaces"
        in s
    )


def test_existing_push_jack_capability_is_preserved():
    s = text()

    for item in (
        "push_required_kn",
        "pressure_mpa",
        "rod_mm",
        "pull_required_kn",
        "stroke_mm",
    ):
        assert item in s

    assert "HydraulicCylinder primitives" in s


def test_mt_t94_remains_unverified():
    s = normalized()

    assert "mt_t94_verified = false" in s

    assert (
        "shall remain unchanged until the candidate sequence "
        "is independently verified"
        in s
    )


def test_registry_still_has_no_f_jack():
    with REGISTRY.open(
        encoding="utf-8-sig",
        newline="",
    ) as f:
        rows = list(csv.DictReader(f))

    ids = {
        (
            row.get("formula_id")
            or row.get("id")
            or ""
        )
        for row in rows
    }

    assert not any(
        formula_id.startswith("F-JACK")
        for formula_id in ids
    )


def test_audit_preserves_no_formula_and_no_record():
    s = text()

    assert "formula_ids = []" in s
    assert "calculation_record_ids = []" in s

    assert (
        "Push-jack engineering traceability remains PARTIAL"
        in s
    )


def test_w39_does_not_pay_debt_with_fake_traceability():
    s = text()

    assert "DO NOT CREATE F-JACK DURING W39-D1" in s

    assert (
        "DO NOT CREATE A PUSH-JACK CALCULATION RECORD "
        "DURING W39-D1"
        in normalized()
    )

    assert "P1 system-completeness debt" in s


def test_push_jack_is_not_a_w39_research_blocker():
    s = text()

    assert "W39 four-bar closure" in s
    assert "W40 kinematic validation" in s
    assert "W41 mature linkage optimization" in s

    assert (
        "return its main effort to deterministic linkage solving"
        in s
    )
