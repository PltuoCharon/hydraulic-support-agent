import sys
sys.path.insert(0, '.')
from app.config import settings
import pymysql

def main():
    conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
        password=settings.DB_PASSWORD, database=settings.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    print("=" * 50)
    print("案例库体检报告 check_cases.py (W26-D3)")
    print("=" * 50)

    # 1. 总量
    cur.execute("SELECT COUNT(*) AS n FROM working_conditions")
    total = cur.fetchone()["n"]
    print(f"\n[总量] 案例数: {total}")

    # 2. 外键有效性: area_id 必须存在于 mining_areas
    cur.execute("""SELECT w.id, w.working_face_name FROM working_conditions w
        LEFT JOIN mining_areas a ON w.area_id=a.id
        WHERE w.area_id IS NULL OR a.id IS NULL""")
    bad_area = cur.fetchall()
    print(f"\n[外键] area_id 悬空: {len(bad_area)}")
    for r in bad_area:
        print(f"  !! id={r['id']} {r['working_face_name']}")

    # 3. 外键有效性: support_model_id 非空时必须存在
    cur.execute("""SELECT w.id, w.working_face_name, w.support_model_id
        FROM working_conditions w
        LEFT JOIN support_models m ON w.support_model_id=m.id
        WHERE w.support_model_id IS NOT NULL AND m.id IS NULL""")
    bad_model = cur.fetchall()
    print(f"[外键] support_model_id 悬空: {len(bad_model)}")
    for r in bad_model:
        print(f"  !! id={r['id']} {r['working_face_name']} -> model_id={r['support_model_id']}")

    # 4. 字段完整度(百分比, NULL不可怕, 不知道有多少NULL才可怕)
    fields = ["coal_thickness", "dip_angle", "mining_height",
              "support_model_id", "source"]
    print("\n[字段完整度]")
    for f in fields:
        cur.execute(f"SELECT COUNT(*) AS n FROM working_conditions "
                    f"WHERE {f} IS NULL OR CAST({f} AS CHAR)='' ")
        nulls = cur.fetchone()["n"]
        pct = (total - nulls) / total * 100 if total else 0
        print(f"  {f}: {pct:.1f}% 完整 (NULL {nulls}/{total})")

    # 5. 架型缺失案例清单(允许NULL, 但要看得见)
    cur.execute("""SELECT w.id, w.working_face_name, w.source
        FROM working_conditions w WHERE w.support_model_id IS NULL""")
    rows = cur.fetchall()
    print(f"\n[架型缺失案例] {len(rows)} 条:")
    for r in rows:
        s = (r["source"] or "")[:40]
        print(f"  id={r['id']} {r['working_face_name']} | {s}")

    # 6. 盲测区覆盖
    cur.execute("SELECT COUNT(*) AS n FROM mining_areas WHERE is_test=1")
    print(f"\n[盲测区] 共 {cur.fetchone()['n']} 个")

    # 7. 来源分布(早期采集待回溯的还有多少)
    cur.execute("""SELECT COUNT(*) AS n FROM working_conditions
        WHERE source LIKE '%来源待回溯%'""")
    print(f"[来源] 早期采集待回溯: {cur.fetchone()['n']} 条")

    print("\n体检完毕")
    conn.close()

if __name__ == "__main__":
    main()
