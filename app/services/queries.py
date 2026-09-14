"""W28-D3: 查询服务层。SQL 只允许出现在 services 层; router/agent 一律委托。
口径约定:
- get_area/list_areas 默认排除盲测矿区(include_test=False), 前端列表不可见盲测集
- list_supports/verified_supports 用 data_status='verified'; 与 matching.load_cases
  的 suspect 排除等价(当前 data_status 仅 verified/suspect 两值, 157/2, 2026-09-14 核实)
"""
from app.db import get_conn

def _fetch(sql, args=()):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, args)
        return cur.fetchall()
    finally:
        conn.close()

def _fetchone(sql, args=()):
    rows = _fetch(sql, args)
    return rows[0] if rows else None

def list_areas(keyword: str | None = None, include_test: bool = False) -> list[dict]:
    """矿区列表: 默认排除盲测; keyword=名称模糊查询"""
    sql, args = "SELECT * FROM mining_areas WHERE 1=1", []
    if not include_test:
        sql += " AND is_test = 0"
    if keyword:
        sql += " AND area_name LIKE %s"
        args.append(f"%{keyword}%")
    return _fetch(sql + " ORDER BY id", args)

def get_area(area_id: int, include_test: bool = False) -> dict | None:
    sql = "SELECT * FROM mining_areas WHERE id=%s"
    if not include_test:
        sql += " AND is_test=0"
    return _fetchone(sql, (area_id,))

def get_support(model_id: int) -> dict | None:
    return _fetchone("SELECT * FROM support_models WHERE id=%s", (model_id,))

def list_supports(type: str | None = None, min_force: int = 0,
                  max_force: int = 99999, only_verified: bool = True) -> list[dict]:
    """支架列表: 架型(前缀匹配含变体)+阻力范围, 默认排除suspect"""
    sql, params = "SELECT * FROM support_models WHERE 1=1", []
    if only_verified:
        sql += " AND data_status='verified'"
    if type:
        sql += " AND type LIKE %s"
        params.append(f"{type}%")
    sql += " AND working_resistance BETWEEN %s AND %s ORDER BY working_resistance"
    params += [min_force, max_force]
    return _fetch(sql, params)

def verified_supports() -> list[dict]:
    """硬约束筛选候选池(原 supports.py:65 的 SQL 下沉)"""
    return _fetch("SELECT * FROM support_models WHERE data_status='verified'")
