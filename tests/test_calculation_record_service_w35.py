import pytest

from app.services.calculation_records import normalize_context


def test_direct_engineering_input_is_user_input():
    source, confirmed, snapshot = normalize_context(
        p_kn=3000,
        run_mode="engineering",
    )
    assert source == "user_input"
    assert confirmed is None
    assert snapshot is None


def test_example_does_not_claim_engineering_provenance():
    source, confirmed, snapshot = normalize_context(
        p_kn=2533,
        run_mode="example",
        context_source_type="selected_support",
        context_confirmed=True,
        context_snapshot={"target": {"resistance_kn": 2533}},
    )
    assert source is None
    assert confirmed is None
    assert snapshot == {"target": {"resistance_kn": 2533}}


def test_confirmed_selected_support_is_preserved_when_value_matches():
    source, confirmed, snapshot = normalize_context(
        p_kn=5000,
        run_mode="engineering",
        context_source_type="selected_support",
        context_confirmed=True,
        context_snapshot={
            "target": {
                "support_model": "TEST",
                "resistance_kn": 5000,
            }
        },
    )
    assert source == "selected_support"
    assert confirmed is True
    assert snapshot["target"]["resistance_kn"] == 5000


def test_modified_transferred_resistance_becomes_user_input():
    source, confirmed, snapshot = normalize_context(
        p_kn=5200,
        run_mode="engineering",
        context_source_type="selected_support",
        context_confirmed=True,
        context_snapshot={
            "target": {
                "support_model": "TEST",
                "resistance_kn": 5000,
            }
        },
    )
    assert source == "user_input"
    assert confirmed is None
    assert snapshot["actual_input_override"] == {
        "field": "p_kn",
        "reference_value": 5000.0,
        "actual_value": 5200.0,
    }


def test_unconfirmed_transferred_context_is_rejected():
    with pytest.raises(ValueError, match="not confirmed"):
        normalize_context(
            p_kn=5000,
            run_mode="engineering",
            context_source_type="selected_support",
            context_confirmed=False,
            context_snapshot={"target": {"resistance_kn": 5000}},
        )
