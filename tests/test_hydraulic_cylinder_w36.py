import inspect
import math

import pytest

from app.services.calc.hydraulic_cylinder import (
    STANDARD_BORES,
    annular_area,
    bore_for_push_force,
    piston_area,
    pull_force,
    push_force,
    round_up_standard_bore,
)


def test_piston_area_320():
    area = piston_area(320)

    assert area == pytest.approx(
        math.pi * 320**2 / 4,
        rel=1e-12,
    )


def test_push_force_matches_existing_column_benchmark():
    assert push_force(
        320,
        31.5,
    ) == pytest.approx(
        2533.4,
        abs=0.1,
    )


def test_inverse_push_force_returns_320():
    assert bore_for_push_force(
        2533,
        31.5,
    ) == pytest.approx(
        320.0,
        abs=0.1,
    )


def test_annular_area_is_less_than_piston_area():
    full = piston_area(200)
    annular = annular_area(200, 120)

    assert annular < full
    assert annular == pytest.approx(
        math.pi * (200**2 - 120**2) / 4,
        rel=1e-12,
    )


def test_pull_force_is_less_than_push_force_for_same_pressure():
    push = push_force(200, 31.5)
    pull = pull_force(200, 120, 31.5)

    assert pull < push


def test_standard_bore_rounding_matches_existing_column_series():
    assert 320 in STANDARD_BORES
    assert round_up_standard_bore(320.0) == 320
    assert round_up_standard_bore(320.1) == 360
    assert round_up_standard_bore(63.0) == 63


@pytest.mark.parametrize(
    "args",
    [
        (0,),
        (-1,),
    ],
)
def test_invalid_bore_rejected(args):
    with pytest.raises(ValueError):
        piston_area(*args)


def test_invalid_rod_geometry_rejected():
    with pytest.raises(ValueError):
        annular_area(200, 200)

    with pytest.raises(ValueError):
        annular_area(200, 220)

    with pytest.raises(ValueError):
        annular_area(200, 0)


def test_invalid_pressure_rejected():
    with pytest.raises(ValueError):
        push_force(200, 0)



def test_standard_bore_overflow_rejected():
    with pytest.raises(ValueError):
        round_up_standard_bore(501)


def test_generic_primitives_do_not_apply_column_business_caps():
    assert piston_area(1001) > 0
    assert push_force(200, 101) > 0
    assert bore_for_push_force(60000, 31.5) > 0


def test_generic_primitive_signatures_have_no_eta():
    functions = (
        piston_area,
        annular_area,
        push_force,
        pull_force,
        bore_for_push_force,
        round_up_standard_bore,
    )

    for func in functions:
        assert "eta" not in inspect.signature(func).parameters
