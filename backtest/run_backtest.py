"""盲测回测：遍历测试矿区 → /api/match → 命中判定 → CSV
用法: python backtest/run_backtest.py --weight ahp|entropy|combo --tag G1"""
import argparse, csv, json, re, sys
import urllib.request
sys.path.insert(0, ".")
from app.db import get_conn

BASE = "http://127.0.0.1:8000"

def post(path, payload):
    req = urllib.request.Request(BASE + path, method="POST",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())["data"]

def same_series(rec_model, actual_model):
    """同型号或同系列判定"""
    if not rec_model or not actual_model:
        return False
    if rec_model == actual_model:
        return True
    base = lambda m: re.match(r"^[A-Z]+\d+", m.replace(" ", "")).group(0) if re.match(r"^[A-Z]+\d+", m.replace(" ", "")) else m
    return base(rec_model) == base(actual_model)   # 如 ZY21000 段相同即同系列

def resistance_close(rec_r, actual_r, tol=0.15):
    try:
        return abs(float(rec_r) - float(actual_r)) / float(actual_r) <= tol
    except (TypeError, ZeroDivisionError):
        return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.area_name, s.model AS actual, s.working_resistance AS actual_r
        FROM mining_areas a
        JOIN working_conditions wc ON wc.area_id = a.id
        LEFT JOIN support_models s ON wc.support_model_id = s.id
        WHERE a.is_test=1 GROUP BY a.id""")
    tests = cur.fetchall(); conn.close()
    if not tests:
        sys.exit("没有 is_test=1 的盲测矿区！先按W16计划标记")

    rows = []
    for t in tests:
        data = post("/api/match/", {"area_id": t["id"], "top_n": 5})
        items = data["items"]
        hit1 = items and (same_series(items[0]["support_model"], t["actual"])
                          or resistance_close(items[0]["working_resistance"], t["actual_r"]))
        hit3 = any(same_series(i["support_model"], t["actual"])
                   or resistance_close(i["working_resistance"], t["actual_r"]) for i in items[:3])
        dev = (abs(items[0]["working_resistance"] - t["actual_r"]) / t["actual_r"]
               if items and t["actual_r"] else None)
        rows.append({"area": t["area_name"], "actual": t["actual"],
                     "top1": items[0]["support_model"] if items else None,
                     "sim1": items[0]["similarity"] if items else None,
                     "hit1": bool(hit1), "hit3": bool(hit3),
                     "dev": round(dev, 4) if dev is not None else None})
        print(f"{t['area_name']}: 实际={t['actual']} Top1={rows[-1]['top1']} "
              f"hit1={rows[-1]['hit1']} hit3={rows[-1]['hit3']}")

    n = len(rows)
    summary = {"tag": args.tag, "n": n,
               "top1_rate": round(sum(r["hit1"] for r in rows)/n, 3),
               "top3_rate": round(sum(r["hit3"] for r in rows)/n, 3)}
    print("\n汇总:", summary)
    with open(f"backtest/result_{args.tag}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    with open(f"backtest/summary_{args.tag}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
