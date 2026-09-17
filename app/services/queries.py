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
                     WHERE is_test = 0
                       AND lng IS NOT NULL
                       AND lat IS NOT NULL
                     ORDER BY id""")

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
            est.append("支护长度参数")
        if "复算估算" in src or "二阶估算" in src:
            est.append("支护强度")
        if "未查到公开参数" in src:
            est.append("支护强度(未查到公开参数)")
        r["est_fields"] = "、".join(dict.fromkeys(est)) if est else "无"
        hmin, hmax = r["height_min"], r["height_max"]
        r["height_mid"] = round((float(hmin) + float(hmax)) / 2, 2) if hmin else float(hmax)
    return rows


def vendor_dist() -> dict:
    """制造商字段分布。

    兼容旧接口：
    - total / known / unknown / coverage / items 保持不变
    - items 仍包含“未知”，避免破坏 W30 既有契约

    新增治理口径：
    - “未知”属于字段缺失，不是制造商类别
    - “国产”属于历史占位值，不作为已核实制造商
    - known_items 仅用于真实制造商分布图
    """
    rows = _fetch("""
        SELECT
            COALESCE(NULLIF(TRIM(manufacturer), ''), '未知') AS mfr,
            COUNT(*) AS cnt
        FROM support_models
        WHERE data_status = 'verified'
        GROUP BY mfr
        ORDER BY
            (mfr = '未知') DESC,
            cnt DESC,
            mfr
    """)

    items = [
        {
            "manufacturer": r["mfr"],
            "cnt": int(r["cnt"]),
        }
        for r in rows
    ]

    total = sum(i["cnt"] for i in items)

    unknown = next(
        (
            i["cnt"]
            for i in items
            if i["manufacturer"] == "未知"
        ),
        0,
    )

    placeholder = next(
        (
            i["cnt"]
            for i in items
            if i["manufacturer"] == "国产"
        ),
        0,
    )

    # legacy known 口径保持兼容：
    # 只排除 NULL/空字段映射的“未知”。
    known = total - unknown

    usable_known = total - unknown - placeholder

    known_items = [
        i
        for i in items
        if i["manufacturer"] not in {"未知", "国产"}
    ]

    return {
        "total": total,
        "known": known,
        "unknown": unknown,
        "coverage": (
            round(known / total * 100, 1)
            if total
            else 0
        ),

        "placeholder": placeholder,

        "usable_known": usable_known,

        "usable_coverage": (
            round(usable_known / total * 100, 1)
            if total
            else 0
        ),

        "items": items,
        "known_items": known_items,
    }


def data_quality_summary() -> dict:
    """W34-D6 数据质量中心聚合数据。

    本接口只描述：
    - 数据状态
    - 字段完整度
    - 缺失情况
    - 当前来源字段结构

    “字段有值”不代表参数正确，也不代表工程可信。
    """

    status = _fetchone("""
        SELECT
            COUNT(*) AS total,
            SUM(data_status = 'verified') AS verified,
            SUM(data_status = 'suspect') AS suspect
        FROM support_models
    """)

    support = _fetchone("""
        SELECT
            COUNT(*) AS total,

            SUM(
                manufacturer IS NOT NULL
                AND TRIM(manufacturer) <> ''
                AND manufacturer <> '国产'
            ) AS manufacturer_known,

            SUM(
                type IS NOT NULL
                AND TRIM(type) <> ''
            ) AS type_known,

            SUM(
                intensity IS NOT NULL
                AND TRIM(CAST(intensity AS CHAR)) <> ''
            ) AS intensity_known,

            SUM(weight IS NOT NULL)
                AS weight_known,

            SUM(initial_force IS NOT NULL)
                AS initial_force_known,

            SUM(
                source IS NOT NULL
                AND TRIM(source) <> ''
            ) AS source_known,

            SUM(
                source LIKE '%%估算%%'
                OR source LIKE '%%复算%%'
            ) AS estimated_rows

        FROM support_models
        WHERE data_status = 'verified'
    """)

    areas = _fetchone("""
        SELECT
            COUNT(*) AS total,

            SUM(coal_thickness IS NOT NULL)
                AS coal_thickness_known,

            SUM(dip_angle IS NOT NULL)
                AS dip_angle_known,

            SUM(
                mining_height_min IS NOT NULL
                OR mining_height_max IS NOT NULL
            ) AS mining_height_known,

            SUM(hardness_f IS NOT NULL)
                AS hardness_known,

            SUM(
                roof_category IS NOT NULL
                AND TRIM(roof_category) <> ''
            ) AS roof_known,

            SUM(floor_pressure IS NOT NULL)
                AS floor_pressure_known,

            SUM(
                mine_pressure IS NOT NULL
                AND TRIM(mine_pressure) <> ''
            ) AS mine_pressure_known,

            SUM(
                gas_level IS NOT NULL
                AND TRIM(gas_level) <> ''
            ) AS gas_known,

            SUM(depth IS NOT NULL)
                AS depth_known,

            SUM(face_length IS NOT NULL)
                AS face_length_known,

            SUM(
                lng IS NOT NULL
                AND lat IS NOT NULL
            ) AS coordinate_known

        FROM mining_areas
        WHERE is_test = 0
    """)

    source_schema = _fetchone("""
        SELECT
            DATA_TYPE AS data_type,
            CHARACTER_MAXIMUM_LENGTH AS max_length
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'support_models'
          AND COLUMN_NAME = 'source'
    """)

    def metric(key, label, known, total):
        total = int(total or 0)
        known = int(known or 0)

        return {
            "key": key,
            "label": label,
            "known": known,
            "missing": max(total - known, 0),
            "total": total,
            "coverage": (
                round(known / total * 100, 1)
                if total
                else 0
            ),
        }

    support_total = int(support["total"] or 0)
    area_total = int(areas["total"] or 0)

    support_fields = [
        metric(
            "manufacturer",
            "制造商",
            support["manufacturer_known"],
            support_total,
        ),
        metric(
            "type",
            "架型",
            support["type_known"],
            support_total,
        ),
        metric(
            "intensity",
            "支护强度",
            support["intensity_known"],
            support_total,
        ),
        metric(
            "weight",
            "支架质量",
            support["weight_known"],
            support_total,
        ),
        metric(
            "initial_force",
            "初撑力",
            support["initial_force_known"],
            support_total,
        ),
        metric(
            "source",
            "主要来源摘要",
            support["source_known"],
            support_total,
        ),
    ]

    area_fields = [
        metric(
            "coal_thickness",
            "煤层厚度",
            areas["coal_thickness_known"],
            area_total,
        ),
        metric(
            "dip_angle",
            "煤层倾角",
            areas["dip_angle_known"],
            area_total,
        ),
        metric(
            "mining_height",
            "采高范围",
            areas["mining_height_known"],
            area_total,
        ),
        metric(
            "hardness_f",
            "煤层硬度",
            areas["hardness_known"],
            area_total,
        ),
        metric(
            "roof_category",
            "顶板类型",
            areas["roof_known"],
            area_total,
        ),
        metric(
            "floor_pressure",
            "底板比压",
            areas["floor_pressure_known"],
            area_total,
        ),
        metric(
            "mine_pressure",
            "矿压特征",
            areas["mine_pressure_known"],
            area_total,
        ),
        metric(
            "gas_level",
            "瓦斯",
            areas["gas_known"],
            area_total,
        ),
        metric(
            "depth",
            "埋深",
            areas["depth_known"],
            area_total,
        ),
        metric(
            "face_length",
            "工作面长度",
            areas["face_length_known"],
            area_total,
        ),
        metric(
            "coordinate",
            "城市级近似坐标",
            areas["coordinate_known"],
            area_total,
        ),
    ]

    return {
        "supports": {
            "total": int(status["total"] or 0),
            "verified": int(status["verified"] or 0),
            "suspect": int(status["suspect"] or 0),
            "verified_fields": support_fields,
            "estimated_rows": int(
                support["estimated_rows"] or 0
            ),
        },

        "areas": {
            "total": area_total,
            "fields": area_fields,
        },

        "source_schema": {
            "data_type": (
                source_schema["data_type"]
                if source_schema
                else None
            ),
            "max_length": (
                int(source_schema["max_length"])
                if source_schema
                and source_schema["max_length"] is not None
                else None
            ),
        },

        "notes": [
            "字段完整度仅表示字段是否有值，不代表数据准确性或工程可信度。",
            "verified 与 suspect 为数据状态；suspect 默认不参与谱系与制造商分析。",
            "source 当前仅作为主要来源摘要使用，详细参数级 provenance 尚待独立建模。",
        ],
    }
