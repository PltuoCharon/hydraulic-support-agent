"""W28-D2 重构前基线：盲测8矿区 Top-5 快照，供重构后逐条比对"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import get_conn
from app.services.matcher import run_match

conn = get_conn()
cur = conn.cursor()
cur.execute("SELECT id, area_name FROM mining_areas WHERE is_test=1 ORDER BY id")
areas = cur.fetchall()
conn.close()

snap = {}
for a in areas:
    d = run_match(area_id=a["id"], top_n=5)
    snap[a["area_name"]] = {
        "total": d["total"],
        "top5": [(it["case_id"], it["support_model"], it["similarity"]) for it in d["items"]],
    }

os.makedirs("docs/thesis_data", exist_ok=True)
out = "docs/thesis_data/w28_baseline.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(snap, f, ensure_ascii=False, indent=1)
print(f"已存 {out}，{len(snap)} 个矿区")
for k, v in snap.items():
    print(f"  {k}: total={v['total']}  Top1={v['top5'][0] if v['top5'] else '无'}")
