from pathlib import Path


def read(path):
    return Path(path).read_text(
        encoding="utf-8"
    )


def test_result_enters_new_column_design():
    s = read(
        "web/src/views/ResultView.vue"
    )

    assert "进入立柱设计" in s
    assert "goColumnDesign(it)" in s
    assert 'path: "/calc"' in s
    assert 'm: "column"' in s
    assert 'ctx: "selected_support"' in s

    assert (
        "router.push('/modify')"
        not in s
    )

    assert "getRequirement" not in s
    assert ':required="null"' in s
    assert "未查到公开参数" in s
    assert "旧需求阈值计算链已退出主结果展示" in s


def test_compare_never_maps_missing_to_zero():
    s = read(
        "web/src/views/CompareView.vue"
    )

    assert "comparableDims" in s
    assert "共同完整维度" in s

    assert (
        "缺失字段不会按 0 参与计算"
        in s
    )

    assert "?? 0" not in s
    assert "（按 0 计）" not in s


def test_compare_requires_shared_complete_dimensions():
    s = read(
        "web/src/views/CompareView.vue"
    )

    assert "selected.value.every" in s

    assert (
        "comparableDims.length < 3"
        in s
    )

    assert (
        "共同完整维度不足 3 项"
        in s
    )


def test_modify_route_is_compatibility_redirect():
    s = read(
        "web/src/router/index.js"
    )

    assert "path: '/modify'" in s

    assert (
        "redirect: '/calc?m=column'"
        in s
    )


def test_legacy_modify_implementation_is_not_deleted():
    s = read(
        "web/src/views/ModifyView.vue"
    )

    assert "postRecalc" in s
    assert "getRequirement" in s
