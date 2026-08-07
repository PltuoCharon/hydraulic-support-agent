"""W16-D2 回测脚本：对 5 个盲测矿区调 match 接口，统计命中率与阻力偏差。
用法:
  1. 以目标组配置启动 uvicorn（G0: EFFECT_HEIGHT_RULE=off；G1: 默认）
  2. python backtest/run_backtest.py G0   # 组标签作为参数
输出: backtest/results_<组>.csv + 终端汇总
"""
import csv, json, re, sys, urllib.request

GROUND_TRUTH = {
    6:  ("鲍店1316",     "ZF15000/25/45",   15000),
    8:  ("晋城寺河",     "ZY21000/38/82D",  21000),
    10: ("平朔安家岭",   "ZY12000/28/58",   12000),
    13: ("神东黄玉川",   "ZF15000/25/45",   15000),
    16: ("义马千秋21121", "ZYA29000/45/100D", 29000),
}

def match(area_id, top_n=5):
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/match/",
        data=json.dumps({"area_id": area_id, "top_n": top_n}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["data"]["items"]

def series_of(model: str) -> str:
    """架型系列 = 型号前导字母，如 ZF15000 -> ZF, ZYA29000 -> ZYA"""
    m = re.match(r"[A-Z]+", model or "")
    return m.group(0) if m else ""

def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "GX"
    rows, hit1, hit3, devs = [], 0, 0, []
    for aid, (name, truth, truth_wr) in GROUND_TRUTH.items():
        items = match(aid)
        models = [it["support_model"] for it in items]
        top1 = items[0]
        h1 = truth in models[:1]
        h3 = truth in models[:3]
        s3 = any(series_of(m) == series_of(truth) for m in models[:3])
        wr = top1.get("working_resistance") or 0
        dev = round((wr - truth_wr) / truth_wr * 100, 1) if wr else None
        hit1 += h1; hit3 += h3
        if dev is not None: devs.append(abs(dev))
        rows.append([group, aid, name, truth, top1["support_model"],
                     top1["similarity"], wr, h1, h3, s3, dev])
        print(f"{name:12s} Top1={top1['support_model']:18s} sim={top1['similarity']:.4f} "
              f"Top1中={h1} Top3中={h3} 同系列Top3={s3} 阻力偏差={dev}%")
    n = len(GROUND_TRUTH)
    print(f"\n===== {group} 汇总 =====")
    print(f"Top-1 命中率: {hit1}/{n} = {hit1/n:.0%}")
    print(f"Top-3 命中率: {hit3}/{n} = {hit3/n:.0%}")
    print(f"Top-1 平均阻力偏差: {sum(devs)/len(devs):.1f}%")
    out = f"backtest/results_{group}.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["group","area_id","area","truth","top1_model","top1_sim",
                    "top1_wr","hit_top1","hit_top3","series_top3","wr_dev_pct"])
        w.writerows(rows)
    print(f"已保存 {out}")

if __name__ == "__main__":
    main()
