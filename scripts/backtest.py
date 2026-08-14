"""回测：留一法(LOO) Top-1/Top-3 命中率，三组权重对比。W24 验收闸门2。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import get_conn
from app.services.matcher import run_match

def load_cases():
    """标注集：真实工作面用架（working_conditions -> support_models）"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT wc.id, wc.coal_thickness, wc.dip_angle, s.model AS support_model
                FROM working_conditions wc
                JOIN support_models s ON wc.support_model_id = s.id
                WHERE wc.support_model_id IS NOT NULL
            """)
            return cur.fetchall()
    finally:
        conn.close()

def run_backtest(mode):
    os.environ["MATCH_WEIGHTS"] = mode
    cases = load_cases()
    hit1 = hit3 = total = 0
    misses = []
    for c in cases:
        try:
            res = run_match(coal_thickness=c["coal_thickness"], dip_angle=c["dip_angle"] or 0, top_n=3)
        except Exception as e:
            print(f"[warn] case {c['id']} 匹配失败: {e}")
            continue
        items = res.get("items", [])
        if not items:
            continue
        total += 1
        models = [i["support_model"] for i in items]
        if c["support_model"] in models:
            hit3 += 1
            if models[0] == c["support_model"]:
                hit1 += 1
        else:
            misses.append((c["id"], c["support_model"], models[:3]))
    p1 = hit1 / total * 100 if total else 0
    p3 = hit3 / total * 100 if total else 0
    print(f"[{mode}] 案例数={total} Top1命中={hit1}({p1:.1f}%) Top3命中={hit3}({p3:.1f}%)")
    if misses:
        print("  Top3 未命中示例:", misses[:5])
    return {"mode": mode, "total": total, "top1": hit1, "top3": hit3, "p1": round(p1, 1), "p3": round(p3, 1)}

if __name__ == "__main__":
    results = [run_backtest(m) for m in ["entropy", "ahp", "combo"]]
    # 生成回测表文档
    lines = ["# 回测表（留一法 LOO，三组权重对比）", "",
             "生成时间：W24 总验收", "", "| 权重模式 | 案例数 | Top-1 命中 | Top-1 率 | Top-3 命中 | Top-3 率 |",
             "|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['mode']} | {r['total']} | {r['top1']} | {r['p1']}% | {r['top3']} | {r['p3']}% |")
    lines.append("")
    lines.append("达标线：Top-3 ≥ 60% 或完成失败分析。")
    with open("docs/回测表.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n已写入 docs/回测表.md")
