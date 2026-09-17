from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def read(path):
    return Path(path).read_text(
        encoding="utf-8"
    )


def test_selection_center_explains_matching_scope():
    s = read(
        "web/src/views/SelectCenterView.vue"
    )

    assert "当前匹配核心输入" in s
    assert "煤层厚度" in s
    assert "煤层倾角" in s

    assert (
        "工况档案与后续设计参数"
        in s
    )

    # Workbench 已承担全局KPI，
    # 选型页不应再次调用 getStats。
    assert "getStats" not in s


def test_area_page_has_completeness_and_selection_chain():
    s = read(
        "web/src/views/AreasView.vue"
    )

    assert "DataCompleteness" in s
    assert "关键工况字段完整度" in s

    assert (
        "store.prefillFromArea(area)"
        in s
    )

    assert "采高范围覆盖" in s


def test_map_page_has_coverage_and_stable_detail_panel():
    s = read(
        "web/src/views/MapView.vue"
    )

    assert "可地图化" in s
    assert "坐标覆盖率" in s

    assert "getAreaDetail" in s
    assert "EmptyState" in s

    # 右侧面板应始终存在，
    # 不再通过 v-if=selected 整体移除。
    assert (
        '<aside\n'
        '        v-loading="panelLoading"'
        in s
    )

    assert (
        'aside v-if="selected"'
        not in s
    )


def test_map_api_returns_only_complete_coordinates():
    client = TestClient(app)

    response = client.get(
        "/api/mining-areas/"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["code"] == 0

    data = payload["data"]

    assert data["total"] == len(
        data["items"]
    )

    assert all(
        item["lng"] is not None
        and item["lat"] is not None
        for item in data["items"]
    )

    assert data["coord_note"]
