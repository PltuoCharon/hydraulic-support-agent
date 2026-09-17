from pathlib import Path


def read(path):
    return Path(path).read_text(encoding="utf-8")


def test_app_uses_engineering_shell():
    app = read("web/src/App.vue")

    assert "AppShell" in app
    assert "topmenu" not in app


def test_shell_contains_six_primary_modules():
    shell = read("web/src/layouts/AppShell.vue")

    required = [
        "工作台",
        "智能选型",
        "支架数据库",
        "设计计算",
        "图纸·模型·仿真",
        "知识与证据",
    ]

    for name in required:
        assert name in shell


def test_workbench_route_exists_and_legacy_modify_retained():
    router = read("web/src/router/index.js")

    assert "path: '/workbench'" in router

    assert "path: '/modify'" in router
    assert "legacy: true" in router


def test_design_system_components_exist():
    required = [
        "PageHeader.vue",
        "MetricCard.vue",
        "StatusBadge.vue",
        "SourceBadge.vue",
        "FormulaBadge.vue",
    ]

    base = Path("web/src/components/ui")

    for filename in required:
        assert (base / filename).exists()
