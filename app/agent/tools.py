"""Agent 工具集。W18。铁律：所有工具内部参数化/白名单，禁止执行 LLM 生成的裸 SQL。
D1: query_database —— 按条件查矿区/支架。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import json
from langchain_core.tools import tool
from app.db import get_conn

# 允许查询的表与可模糊匹配的字段（白名单）
ALLOWED = {
    "mining_areas":  {"name_field": "area_name", "desc": "矿区/工作面地质条件"},
    "support_models": {"name_field": "model",    "desc": "液压支架型号参数"},
    "working_conditions": {"name_field": "working_face_name", "desc": "工作面工况案例"},
}

@tool
def query_database(table: str, keyword: str = "", limit: int = 5) -> str:
    """查询液压支架选型数据库。当需要矿区地质条件、支架型号参数、历史工况案例等
    事实数据时调用。
    Args:
        table: 表名，仅限 mining_areas(矿区) / support_models(支架) / working_conditions(工况案例)
        keyword: 模糊关键词（如矿区名"补连塔"、型号片段"ZY21000"），空则按 id 返回前几条
        limit: 返回条数，1~10
    Returns:
        JSON 字符串：匹配的记录列表（不含无关于段过多时截断）。
    """
    if table not in ALLOWED:
        return json.dumps({"error": f"非法表名 {table}，仅限 {list(ALLOWED)}"}, ensure_ascii=False)
    limit = max(1, min(int(limit), 10))
    name_field = ALLOWED[table]["name_field"]
    conn = get_conn()
    try:
        cur = conn.cursor()
        if keyword:
            cur.execute(
                f"SELECT * FROM {table} WHERE {name_field} LIKE %s LIMIT %s",
                (f"%{keyword}%", limit))
        else:
            cur.execute(f"SELECT * FROM {table} LIMIT %s", (limit,))
        rows = cur.fetchall()
        # Decimal/datetime 转字符串，保证可 JSON 序列化
        for r in rows:
            for k, v in r.items():
                if not isinstance(v, (int, float, str, type(None))):
                    r[k] = str(v)
        return json.dumps({"table": table, "count": len(rows), "rows": rows},
                          ensure_ascii=False, default=str)
    finally:
        conn.close()

TOOLS = [query_database]   # D2~D4 逐步追加

if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    print(query_database.invoke({"table": "support_models", "keyword": "ZY21000"}))
    print(query_database.invoke({"table": "mining_areas", "keyword": "补连塔", "limit": 2}))
    print(query_database.invoke({"table": "users"}))   # 白名单拒绝测试
