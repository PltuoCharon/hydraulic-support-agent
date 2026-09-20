import math

from app.services.calc.resistance import (
    base_resistance,
    control_area,
    rated_resistance,
    required_resistance,
)


def test_ka554_d3_decomposition_matches_direct_formula():
    ps_mpa = 1.0
    sc_m = 1.5
    bc_m = 5.0
    ks = 0.90

    area = control_area(sc_m, bc_m)
    f_base = base_resistance(ps_mpa, area)
    f_rated = rated_resistance(f_base, ks)

    direct = ps_mpa * 1000.0 * sc_m * bc_m / ks

    assert math.isclose(area, 7.5)
    assert math.isclose(f_base, 7500.0)
    assert math.isclose(
        f_rated,
        8333.333333333334,
    )
    assert math.isclose(f_rated, direct)


def test_support_efficiency_is_divisor_not_multiplier():
    f_base = 7500.0

    assert rated_resistance(f_base, 0.90) > f_base
    assert math.isclose(
        rated_resistance(f_base, 0.90),
        f_base / 0.90,
    )


def test_support_efficiency_rejects_invalid_values():
    for bad in (0, -0.1, 1.01):
        try:
            rated_resistance(7500.0, bad)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"expected ValueError for Ks={bad}"
            )


def test_required_resistance_returns_traceability():
    result = required_resistance(
        q_need_mpa=1.0,
        center_dist_m=1.5,
        control_width_m=5.0,
        support_efficiency=0.90,
    )

    assert result["formula_ids"] == [
        "F-QN-005",
        "F-QN-006",
        "F-QN-007",
    ]
    assert math.isclose(
        result["required_working_resistance_kn"],
        8333.333333333334,
    )
    assert "canopy_len" in result["note"]
    assert "历史eta" in result["note"]
