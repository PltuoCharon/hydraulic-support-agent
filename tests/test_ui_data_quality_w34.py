from pathlib import Path


def read(path):
    return Path(path).read_text(
        encoding="utf-8"
    )


def test_spectrum_uses_support_height_semantics():
    s = read(
        "web/src/views/SpectrumView.vue"
    )

    assert "支撑高度区间中值" in s
    assert "控顶距" not in s
    assert "Y=采高" not in s
    assert "Y：采高" not in s


def test_vendor_separates_missing_from_distribution():
    s = read(
        "web/src/views/VendorView.vue"
    )

    assert "known_items" in s
    assert "制造商缺失" in s
    assert "不代表市场份额" in s
    assert "未知" in s


def test_data_quality_is_not_a_quality_score():
    s = read(
        "web/src/views/DataQualityView.vue"
    )

    assert "字段完整度" in s
    assert "字段有值不等于数据正确" in s
    assert "provenance" in s

    assert "数据质量评分" not in s
    assert "质量得分" not in s


def test_data_quality_route_and_shell_exist():
    router = read(
        "web/src/router/index.js"
    )

    shell = read(
        "web/src/layouts/AppShell.vue"
    )

    assert "path: '/data-quality'" in router
    assert "DataQualityView.vue" in router

    assert "path: '/data-quality'" in shell
    assert "数据质量" in shell
