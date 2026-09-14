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

# W28-D4: Agent 工具的白名单查询(自 tools.py 下沉)
QUERYABLE_TABLES = {
    "mining_areas":  {"name_field": "area_name", "desc": "矿区/工作面地质条件"},
    "support_models": {"name_field": "model",    "desc": "液压支架型号参数"},
    "working_conditions": {"name_field": "working_face_name", "desc": "工作面工况案例"},
}

def search_rows(table: str, keyword: str = "", limit: int = 5) -> list[dict]:
    """白名单模糊查询。table 不在白名单抛 ValueError; limit 强制 1~10"""
    if table not in QUERYABLE_TABLES:
        raise ValueError(f"非法表名 {table}，仅限 {list(QUERYABLE_TABLES)}")
    limit = max(1, min(int(limit), 10))
    name_field = QUERYABLE_TABLES[table]["name_field"]
    if keyword:
        return _fetch(f"SELECT * FROM {table} WHERE {name_field} LIKE %s LIMIT %s",
                      (f"%{keyword}%", limit))
    return _fetch(f"SELECT * FROM {table} LIMIT %s", (limit,))

# W29-D4: 地图选区
def map_areas() -> list[dict]:
    """地图散点: 非盲测 + 有坐标的矿区, 含关键工况。盲测集永不出现在前端(铁律3)"""
    return _fetch("""SELECT id, area_name, adcode, lng, lat, coal_thickness, dip_angle,
                            mining_height_min, mining_height_max, category
                     FROM mining_areas
                     WHERE is_test = 0 AND lng IS NOT NULL ORDER BY id""")

def area_supports(area_id: int) -> list[dict]:
    """矿区在用支架: 该矿区案例的实际用架(suspect 型号除外, 铁律4)"""
    return _fetch("""SELECT s.id, s.model, s.type, s.working_resistance,
                            s.height_min, s.height_max,
                            wc.working_face_name, wc.source
                     FROM working_conditions wc
                     JOIN support_models s ON wc.support_model_id = s.id
                     WHERE wc.area_id = %s
                       AND (s.data_status IS NULL OR s.data_status <> 'suspect')""",
                  (area_id,))


def spectrum() -> list[dict]:
    """W30-D1 架型谱系: X=工作阻力 Y=采高(区间中值)。
    verified 白名单(铁律4 suspect 默认排除);
    口径: 阻力/采高均来自公开型谱值(轴相关估算为零, 2026-09-14 核实),
    其他字段(控顶距/支护强度)的估算标注在 est_fields, 供 tooltip 展示。"""
    rows = _fetch("""SELECT id, model, type, working_resistance, height_min, height_max,
                            manufacturer, source
                     FROM support_models
                     WHERE data_status = 'verified'
                       AND working_resistance IS NOT NULL
                       AND height_max IS NOT NULL
                     ORDER BY working_resistance""")
    for r in rows:
        src = r.get("source") or ""
        est = []
        if "控顶长度" in src and "估算" in src:
            est.append("控顶长度")
        if "复算估算" in src or "二阶估算" in src:
            est.append("支护强度")
        if "未查到公开参数" in src:
            est.append("支护强度(未查到公开参数)")
        r["est_fields"] = "、".join(dict.fromkeys(est)) if est else "无"
        hmin, hmax = r["height_min"], r["height_max"]
        r["height_mid"] = round((float(hmin) + float(hmax)) / 2, 2) if hmin else float(hmax)
    return rows


def vendor_dist() -> dict:
    """W30-D2 厂商分布。verified 白名单(铁律4);
    口径: manufacturer 为 NULL → 未知(占位第一大条, 灰色);
    '国产' 为采集期占位值, 原样保留由前端标橙注明, 不静默归并。"""
    rows = _fetch("""SELECT COALESCE(NULLIF(TRIM(manufacturer), ''), '未知') AS mfr,
                            COUNT(*) AS cnt
                     FROM support_models
                     WHERE data_status = 'verified'
                     GROUP BY mfr
                     ORDER BY (mfr = '未知') DESC, cnt DESC, mfr""")
    total = sum(r["cnt"] for r in rows)
    unknown = next((r["cnt"] for r in rows if r["mfr"] == "未知"), 0)
    known = total - unknown
    return {"total": total, "known": known, "unknown": unknown,
            "coverage": round(known / total * 100, 1) if total else 0,
            "items": [{"manufacturer": r["mfr"], "cnt": r["cnt"]} for r in rows]}
