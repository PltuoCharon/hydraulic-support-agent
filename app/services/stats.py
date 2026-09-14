"""W29-D3: 首页总览统计(自 main.py 下沉; SQL 只允许在 services 层)。
行为变化(已记录): areas 计数改为排除盲测矿区(is_test=0), 与前端列表口径一致;
原口径把盲测集计入总数, 与列表页数字对不上。"""
from app.db import get_conn

def overview() -> dict:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) c FROM support_models")
        supports = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) c FROM support_models WHERE weight IS NOT NULL")
        has_w = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) c FROM support_models WHERE intensity IS NOT NULL")
        has_i = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) c FROM working_conditions")
        cases = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) c FROM param_dependencies")
        rules = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) c FROM mining_areas WHERE is_test = 0")
        areas = cur.fetchone()["c"]
        cur.execute("""SELECT manufacturer, COUNT(*) c FROM support_models
                       WHERE manufacturer IS NOT NULL
                       GROUP BY manufacturer ORDER BY c DESC LIMIT 5""")
        vendors = cur.fetchall()
    finally:
        conn.close()
    return {
        "supports": supports,
        "weight_coverage": round(has_w / supports * 100, 1),
        "intensity_coverage": round(has_i / supports * 100, 1),
        "cases": cases, "rules": rules, "areas": areas,
        "vendors": [{"name": v["manufacturer"], "count": v["c"]} for v in vendors],
    }
