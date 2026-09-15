"""W31-D4 盲测回测(data-v5基线): 9个盲测区出题, Top-1/Top-3命中判定, 未命中归因。
用法: PYTHONPATH=. python scripts/backtest.py
输出: docs/thesis_data/backtest_data-v5.csv"""
import sys, csv, os
sys.path.insert(0, '.')
from app.config import settings
import pymysql
from app.services.matcher import run_match

def family(model):
    """型号族: 系列字母+阻力数, 如 ZY12000/28/58 -> ZY12000"""
    if not model:
        return ""
    return model.split("/")[0]

def main():
    conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
        password=settings.DB_PASSWORD, database=settings.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    cur.execute("""SELECT wc.id AS cid, wc.area_id, wc.working_face_name,
                          s.model AS actual_model, s.type AS actual_type,
                          a.name AS area_name
                   FROM working_conditions wc
                   JOIN mining_areas a ON wc.area_id=a.id
                   LEFT JOIN support_models s ON wc.support_model_id=s.id
                   WHERE a.is_test=1
                   ORDER BY a.name""")
    blinds = cur.fetchall()
    print(f"盲测案例: {len(blinds)} 条")
    rows = []
    for b in blinds:
        actual = b["actual_model"]
        if not actual:
            rows.append(dict(area=b["area_name"], face=b["working_face_name"],
                actual="(无架型)", rank="", hit1=0, hit3=0, near=0,
                top1="", reason="数据缺失:案例无架型"))
            continue
        r = run_match(area_id=b["area_id"], top_n=5)
        items = r["data"]["items"] if "data" in r else r["items"]
        recs = [it.get("support_model") or it.get("model") for it in items]
        rank = recs.index(actual) + 1 if actual in recs else 0
        hit1, hit3 = int(rank == 1), int(1 <= rank <= 3)
        near = 0
        if not hit3 and rank == 0:
            if any(family(rc) == family(actual) and rc for rc in recs):
                near = 1
        reason = ""
        if not hit3:
            cur.execute("SELECT id, type FROM support_models WHERE model=%s", (actual,))
            m = cur.fetchone()
            if not m:
                reason = "数据缺失:实际架型不在库"
            elif recs and family(recs[0])[:2] != family(actual)[:2]:
                reason = "架型不符:Top1系列不同"
            else:
                reason = "权重不当:参数接近但排名靠后"
        rows.append(dict(area=b["area_name"], face=b["working_face_name"],
            actual=actual, rank=rank or "未中", hit1=hit1, hit3=hit3, near=near,
            top1=recs[0] if recs else "", reason=reason))
        print(f"{b['area_name']}: 实际{actual} -> Top1 {recs[0] if recs else '-'} "
              f"rank={rank or '未中'} hit1={hit1} hit3={hit3} near={near}")

    n = len([r for r in rows if r['actual'] != '(无架型)'])
    h1 = sum(r["hit1"] for r in rows)
    h3 = sum(r["hit3"] for r in rows)
    nr = sum(r["near"] for r in rows)
    print("=" * 50)
    print(f"Top-1: {h1}/{n} = {h1/n*100:.1f}%")
    print(f"Top-3: {h3}/{n} = {h3/n*100:.1f}%")
    print(f"同族近似(未中但同族): {nr}/{n}")

    os.makedirs("docs/thesis_data", exist_ok=True)
    fp = "docs/thesis_data/backtest_data-v5.csv"
    with open(fp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["area","face","actual","rank",
                                          "hit1","hit3","near","top1","reason"])
        w.writeheader()
        w.writerows(rows)
    print(f"已存档: {fp}")
    conn.close()

if __name__ == "__main__":
    main()
