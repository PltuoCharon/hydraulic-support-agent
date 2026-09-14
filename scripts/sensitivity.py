"""W27-D3 权重敏感性分析: 3模式基线 + 两特征±20%扰动, 共7组。
用法: PYTHONPATH=. python scripts/sensitivity.py
输出: docs/thesis_data/sensitivity_data-v2.csv"""
import sys, os, csv
sys.path.insert(0, '.')
import pymysql
from app.config import settings
import app.services.matcher as matcher

GROUPS = [
    ("G0_entropy基线", "entropy", None),
    ("G1_ahp基线", "ahp", None),
    ("G2_combo基线", "combo", None),
    ("G3_采高+20%", "ahp", {"_eff_h": 1.2}),
    ("G4_采高-20%", "ahp", {"_eff_h": 0.8}),
    ("G5_煤厚+20%", "ahp", {"coal_thickness": 1.2}),
    ("G6_煤厚-20%", "ahp", {"coal_thickness": 0.8}),
]

def blind_cases(cur):
    cur.execute("""SELECT wc.area_id, a.name AS area, s.model AS actual
                   FROM working_conditions wc
                   JOIN mining_areas a ON wc.area_id=a.id
                   JOIN support_models s ON wc.support_model_id=s.id
                   WHERE a.is_test=1""")
    return cur.fetchall()

def run_group(cur, blinds, mode, perturb):
    os.environ["MATCH_WEIGHTS"] = mode
    saved = dict(matcher.NUM_W)
    if perturb:
        for k, v in perturb.items():
            matcher.NUM_W[k] = saved[k] * v
    c1 = c3 = 0
    area_hit1, area_hit3 = {}, {}
    for b in blinds:
        r = matcher.run_match(area_id=b["area_id"], top_n=5)
        recs = [it.get("support_model") for it in r["items"]]
        h1 = int(recs[:1] == [b["actual"]])
        h3 = int(b["actual"] in recs[:3])
        c1 += h1
        c3 += h3
        area_hit1[b["area"]] = area_hit1.get(b["area"], 0) or h1
        area_hit3[b["area"]] = area_hit3.get(b["area"], 0) or h3
    matcher.NUM_W.clear()
    matcher.NUM_W.update(saved)
    os.environ["MATCH_WEIGHTS"] = "entropy"
    n = len(blinds)
    na = len(area_hit1)
    return (c1/n*100, c3/n*100,
            sum(area_hit1.values())/na*100, sum(area_hit3.values())/na*100)

def main():
    conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
        password=settings.DB_PASSWORD, database=settings.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    blinds = blind_cases(cur)
    print(f"盲测案例 {len(blinds)} 条, 矿区 {len(set(b['area'] for b in blinds))} 个\n")
    print(f"{'组别':<18}{'Top1案例%':>10}{'Top3案例%':>10}{'Top1矿区%':>10}{'Top3矿区%':>10}")
    rows = []
    for name, mode, perturb in GROUPS:
        t1c, t3c, t1a, t3a = run_group(cur, blinds, mode, perturb)
        rows.append(dict(group=name, mode=mode,
            perturb=str(perturb or "-"),
            top1_case=f"{t1c:.1f}", top3_case=f"{t3c:.1f}",
            top1_area=f"{t1a:.1f}", top3_area=f"{t3a:.1f}"))
        print(f"{name:<18}{t1c:>9.1f}%{t3c:>9.1f}%{t1a:>9.1f}%{t3a:>9.1f}%")
    os.makedirs("docs/thesis_data", exist_ok=True)
    fp = "docs/thesis_data/sensitivity_data-v2.csv"
    with open(fp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["group","mode","perturb",
            "top1_case","top3_case","top1_area","top3_area"])
        w.writeheader()
        w.writerows(rows)
    print(f"\n已存档: {fp}")
    conn.close()

if __name__ == "__main__":
    main()
