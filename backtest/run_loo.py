"""W16-D2b 全案例库 LOO 回测：遍历所有 is_test=0 矿区，引擎自带按 area_id 排除（天然LOO），
以该矿区真实用架为 ground truth，统计 Top-1/Top-3 命中率与阻力偏差。
用法: python backtest/run_loo.py G1   (服务器需以对应组配置运行)
输出: backtest/loo_<组>.csv + 终端汇总
"""
import csv, json, sys, urllib.request
from collections import defaultdict
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import get_conn

def truth_by_area():
    """每个非盲测矿区的真实用架集合 {area_id: (name, {model: wr})}"""
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT ma.id, ma.area_name, sm.model, sm.working_resistance
        FROM working_conditions wc
        JOIN mining_areas ma ON ma.id = wc.area_id
        JOIN support_models sm ON sm.id = wc.support_model_id
        WHERE ma.is_test = 0
    """)
    d = defaultdict(dict)
    names = {}
    for r in cur.fetchall():
        names[r["id"]] = r["area_name"]
        d[r["id"]][r["model"]] = r["working_resistance"]
    return {aid: (names[aid], models) for aid, models in d.items()}

def match(area_id, top_n=5):
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/match/",
        data=json.dumps({"area_id": area_id, "top_n": top_n}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["data"]["items"]

def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "GX"
    truths = truth_by_area()
    rows, hit1, hit3, devs = [], 0, 0, []
    for aid, (name, models) in sorted(truths.items()):
        items = match(aid)
        if not items:
            continue
        recs = [it["support_model"] for it in items]
        top1 = items[0]
        h1 = top1["support_model"] in models
        h3 = any(m in models for m in recs[:3])
        # 阻力偏差：Top1 阻力 vs 真实架阻力的最小相对偏差
        wr = top1.get("working_resistance")
        dev = min(abs((wr - t) / t * 100) for t in models.values() if t) if wr else None
        hit1 += h1; hit3 += h3
        if dev is not None: devs.append(dev)
        rows.append([group, aid, name, "|".join(models), top1["support_model"],
                     top1["similarity"], wr, h1, h3, round(dev, 1) if dev is not None else ""])
        mark = "✓" if h1 else ("~" if h3 else "✗")
        print(f"{mark} {name:14s} 真实={'|'.join(models):28s} Top1={top1['support_model']:18s} sim={top1['similarity']:.3f}")
    n = len(rows)
    print(f"\n===== {group} LOO 汇总 (n={n}) =====")
    print(f"Top-1 命中率: {hit1}/{n} = {hit1/n:.0%}")
    print(f"Top-3 命中率: {hit3}/{n} = {hit3/n:.0%}")
    print(f"Top-1 平均最小阻力偏差: {sum(devs)/len(devs):.1f}%")
    out = f"backtest/loo_{group}.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["group","area_id","area","truth_models","top1_model","top1_sim",
                    "top1_wr","hit_top1","hit_top3","wr_dev_pct"])
        w.writerows(rows)
    print(f"已保存 {out}")

if __name__ == "__main__":
    main()
