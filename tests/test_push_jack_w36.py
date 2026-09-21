import pytest

from app.services.calc.push_jack import (
    push_jack_design,
)


def test_push_only_design_returns_candidate_bore():
    result = push_jack_design(
        push_required_kn=300,
        pressure_mpa=31.5,
    )

    assert result["bore_calc_mm"] == pytest.approx(
        110.1,
        abs=0.1,
    )
    assert result["bore_candidate_mm"] == 125
    assert result["push_actual_kn"] == pytest.approx(
        386.6,
        abs=0.1,
    )
    assert result["push_ok"] is True
    assert result["mt_t94_verified"] is False


def test_no_rod_means_no_pull_result():
    result = push_jack_design(
        push_required_kn=300,
        pressure_mpa=31.5,
    )

    assert "rod_mm" not in result
    assert "pull_actual_kn" not in result
    assert "pull_ok" not in result


def test_known_rod_calculates_pull_force():
    result = push_jack_design(
        push_required_kn=300,
        pressure_mpa=31.5,
        rod_mm=70,
    )

    assert result["rod_mm"] == 70
    assert result["pull_actual_kn"] == pytest.approx(
        265.4,
        abs=0.1,
    )


def test_pull_requirement_passes_when_capacity_is_enough():
    result = push_jack_design(
        push_required_kn=300,
        pressure_mpa=31.5,
        rod_mm=70,
        pull_required_kn=250,
    )

    assert result["pull_required_kn"] == 250
    assert result["pull_ok"] is True


def test_pull_requirement_fails_when_capacity_is_not_enough():
    result = push_jack_design(
        push_required_kn=300,
        pressure_mpa=31.5,
        rod_mm=70,
        pull_required_kn=300,
    )

    assert result["pull_ok"] is False


def test_stroke_is_preserved_as_user_input_only():
    result = push_jack_design(
        push_required_kn=300,
        pressure_mpa=31.5,
        stroke_mm=800,
    )

    assert result["stroke_mm"] == 800
    assert result["stroke_origin"] == "user_input"


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "push_required_kn": 0,
            "pressure_mpa": 31.5,
        },
        {
            "push_required_kn": 300,
            "pressure_mpa": 0,
        },
        {
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
            "rod_mm": 0,
        },
        {
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
            "stroke_mm": 0,
        },
        {
            "push_required_kn": 300,
            "pressure_mpa": 31.5,
            "pull_required_kn": 0,
        },
    ],
)
def test_non_positive_inputs_are_rejected(kwargs):
    with pytest.raises(ValueError):
        push_jack_design(**kwargs)


def test_rod_must_be_smaller_than_candidate_bore():
    with pytest.raises(
        ValueError,
        match="活塞杆直径必须小于候选缸径",
    ):
        push_jack_design(
            push_required_kn=300,
            pressure_mpa=31.5,
            rod_mm=125,
        )


def test_pull_requirement_requires_rod_diameter():
    with pytest.raises(
        ValueError,
        match="提供杆腔拉力需求时必须同时提供活塞杆直径",
    ):
        push_jack_design(
            push_required_kn=300,
            pressure_mpa=31.5,
            pull_required_kn=250,
        )
