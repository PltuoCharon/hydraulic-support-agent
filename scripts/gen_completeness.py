"""W27-D5 论文表3: 数据完备率统计。
用法: PYTHONPATH=. python scripts/gen_completeness.py
输出: docs/thesis_data/completeness_data-v2.csv"""
import sys, csv, os
sys.path.insert(0, '.')
import pymysql
from app.config import settings

def main():
    conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
        password=settings.DB_PASSWORD, database=settings.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    rows = []
    def add(item, value, note=""):
        rows.append(dict(item=item, value=value, note=note))
        print(f"{item}: {value} {note}")

    cur.execute("SELECT COUNT(*) AS n FROM support_models")
    add("架型库总数", cur.fetchone()["n"])
    cur.execute("SELECT COUNT(*) AS n FROM support_models WHERE canopy_len IS NOT NULL")
    n = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS t FROM support_models")
    t = cur.fetchone()["t"]
    add("控顶长度覆盖率", f"{n/t*100:.1f}%", "W25-D3锚定标定+留一法8/8≤15%")
    cur.execute("SELECT COUNT(*) AS n FROM support_models WHERE intensity IS NOT NULL AND intensity<>''")
    add("支护强度覆盖率", f"{cur.fetchone()['n']/t*100:.1f}%", "W25-D4复算,W25-D5回填")
    cur.execute("SELECT COUNT(*) AS n FROM support_models WHERE weight IS NOT NULL")
    add("重量字段条数", cur.fetchone()["n"], "W25-D5审计13/13实测或文献")
    cur.execute("SELECT COUNT(*) AS n FROM working_conditions")
    add("案例总数", cur.fetchone()["n"])
    cur.execute("SELECT COUNT(*) AS n FROM mining_areas WHERE is_test=1")
    add("盲测矿区数", cur.fetchone()["n"], "门槛8-10")
    cur.execute("SELECT COUNT(*) AS n FROM param_dependencies")
    total_p = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM param_dependencies WHERE source IS NOT NULL AND source<>''")
    add("参数溯源标注率", f"{cur.fetchone()['n']}/{total_p}", "W25-D6")
    for f in ["coal_thickness","dip_angle","mining_height","support_model_id","source"]:
        cur.execute(f"SELECT COUNT(*) AS n FROM working_conditions WHERE {f} IS NULL OR CAST({f} AS CHAR)=''")
        nulls = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS t FROM working_conditions")
        t = cur.fetchone()["t"]
        add(f"案例字段完整度_{f}", f"{(t-nulls)/t*100:.1f}%")
    add("枚举归一漏网率", "0%", "W27-D1验收四路全0")
    add("估算数据三处可区分", "是", "库source标签/前端badge/论文标注")

    os.makedirs("docs/thesis_data", exist_ok=True)
    fp = "docs/thesis_data/completeness_data-v2.csv"
    with open(fp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["item","value","note"])
        w.writeheader()
        w.writerows(rows)
    print(f"\n已存档: {fp}")
    conn.close()

if __name__ == "__main__":
    main()
