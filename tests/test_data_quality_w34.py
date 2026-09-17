"""W34-D6 数据质量与制造商治理守门。"""

from fastapi.testclient import TestClient

from app.main import app
from app.services.queries import (
    data_quality_summary,
    vendor_dist,
)


def test_data_quality_support_status_conservation():
    d = data_quality_summary()
    s = d["supports"]

    assert s["total"] == 168
    assert s["verified"] == 166
    assert s["suspect"] == 2

    assert (
        s["verified"] + s["suspect"]
        == s["total"]
    )


def test_data_quality_field_metrics_are_consistent():
    d = data_quality_summary()

    verified = d["supports"]["verified"]

    for item in d["supports"]["verified_fields"]:
        assert item["total"] == verified
        assert 0 <= item["known"] <= verified
        assert item["missing"] == (
            verified - item["known"]
        )

        expected = round(
            item["known"]
            / verified
            * 100,
            1,
        )

        assert item["coverage"] == expected


def test_vendor_known_items_exclude_missing_categories():
    d = vendor_dist()

    assert (
        d["known"] + d["unknown"]
        == d["total"]
    )

    assert (
        d["usable_known"]
        + d["unknown"]
        + d["placeholder"]
        == d["total"]
    )

    assert all(
        i["manufacturer"]
        not in {"未知", "国产"}
        for i in d["known_items"]
    )

    assert sum(
        i["cnt"]
        for i in d["known_items"]
    ) == d["usable_known"]


def test_quality_api_contract():
    client = TestClient(app)

    r = client.get(
        "/api/supports/quality"
    )

    assert r.status_code == 200

    payload = r.json()

    assert payload["code"] == 0

    d = payload["data"]

    assert "supports" in d
    assert "areas" in d
    assert "source_schema" in d

    assert (
        d["source_schema"]["max_length"]
        == 100
    )
