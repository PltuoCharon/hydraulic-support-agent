"""W28-D6: services 层关键分支覆盖(白名单拒绝/LOO/suspect口径/纯函数无副作用)"""
import pytest
from app.services import queries, matching

def test_search_rows_whitelist_reject():
    """白名单外表名必须抛 ValueError(Agent SQL 注入面的最后一道闸)"""
    with pytest.raises(ValueError):
        queries.search_rows("users")

def test_search_rows_limit_clamp():
    """limit 强制收敛 1~10"""
    assert len(queries.search_rows("support_models", limit=999)) <= 10
    assert len(queries.search_rows("support_models", limit=0)) >= 1

def test_load_area_missing_raises():
    with pytest.raises(LookupError):
        matching.load_area(999999)

def test_load_cases_suspect_excluded_by_default():
    """suspect 口径: 默认排除=8条ZY21000案例(2026-09-14 核实); include_suspect=True 可复现旧行为"""
    assert len(matching.load_cases(include_suspect=True)) - len(matching.load_cases()) == 8

def test_load_cases_loo():
    """LOO: 指定矿区自身案例退出候选池。
    动态选矿区: 不能写死(补连塔12514的全部案例挂suspect型号, 默认池中本就不存在)"""
    from app.db import get_conn
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""SELECT wc.area_id, COUNT(*) n FROM working_conditions wc
                   JOIN support_models s ON wc.support_model_id = s.id
                   JOIN mining_areas a ON wc.area_id = a.id
                   WHERE wc.support_model_id IS NOT NULL
                     AND (a.is_test = 0 OR a.is_test IS NULL)
                     AND (s.data_status IS NULL OR s.data_status <> 'suspect')
                   GROUP BY wc.area_id ORDER BY n DESC LIMIT 1""")
    row = cur.fetchone(); conn.close()
    aid, n = row["area_id"], row["n"]
    removed = len(matching.load_cases()) - len(matching.load_cases(exclude_area_id=aid))
    assert removed == n, f"LOO 应移除矿区{aid}的{n}条, 实际{removed}"

def test_match_supports_empty_cases():
    assert matching.match_supports({"coal_thickness": 3.5}, []) == {"total": 0, "items": []}

def test_match_supports_no_mutation():
    """纯函数契约: 不得污染调用方传入的 dict(内部拷贝)"""
    cases = matching.load_cases()
    snapshot = [dict(c) for c in cases]
    target = {"coal_thickness": 3.5, "dip_angle": 5}
    matching.match_supports(target, cases, 3)
    assert "_eff_h" not in target
    assert all(c == s for c, s in zip(cases, snapshot))

def test_filter_endpoint_branch():
    """/api/supports/filter: 手动工况路径, 覆盖 filter_supports 主循环 + verified_supports"""
    from fastapi.testclient import TestClient
    from app.main import app
    r = TestClient(app).post("/api/supports/filter",
                             json={"coal_thickness": 3.5, "dip_angle": 5})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["total_passed"] > 0 and d["required_intensity"] > 0
    assert d["total_passed"] + d["rejected_count"] > 0

def test_filter_endpoint_area_not_found():
    from fastapi.testclient import TestClient
    from app.main import app
    r = TestClient(app).post("/api/supports/filter", json={"area_id": 999999})
    assert r.status_code == 404

def test_map_areas_coords_and_no_blind():
    """地图接口: 全部有坐标; 盲测集(寺河/黄玉川等)不得出现(铁律3守门)"""
    rows = queries.map_areas()
    assert rows and all(r["lng"] is not None and r["adcode"] for r in rows)
    names = [r["area_name"] for r in rows]
    for blind in ["寺河", "黄玉川", "鲍店1316", "朱仙庄"]:
        assert not any(blind in n for n in names), f"盲测矿区{blind}泄漏到地图接口!"

def test_area_supports_excludes_suspect():
    """矿区在用架: suspect型号不得返回(铁律4守门)"""
    rows = queries.area_supports(1)   # 补连塔12514: 案例全部挂suspect ZY21000
    assert all("ZY21000/38/82D" != r["model"] for r in rows)
