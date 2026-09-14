"""W28-D2 重构后比对: 与 w29_pre_norm_baseline.json 逐条核对, 差异须可归因到 suspect 退出"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db import get_conn
from app.services.matcher import run_match

base = json.load(open("docs/thesis_data/w29_pre_norm_baseline.json", encoding="utf-8"))
conn = get_conn(); cur = conn.cursor()
cur.execute("SELECT id, area_name FROM mining_areas WHERE is_test=1 ORDER BY id")
areas = cur.fetchall(); conn.close()

diffs = 0
for a in areas:
    d = run_match(area_id=a["id"], top_n=5)
    now = [(it["case_id"], it["support_model"], it["similarity"]) for it in d["items"]]
    old = [tuple(x) for x in base[a["area_name"]]["top5"]]
    if base[a["area_name"]]["total"] != d["total"] or old != now:
        diffs += 1
        print(f"[差异] {a['area_name']}: total {base[a['area_name']]['total']}→{d['total']}")
        for i in range(max(len(old), len(now))):
            o = old[i] if i < len(old) else None
            n = now[i] if i < len(now) else None
            print(f"   {i+1}. 旧{o} 新{n}{'' if o == n else '  <-- 变'}")
    else:
        print(f"[一致] {a['area_name']}")
print(f"\n{len(areas)-diffs}/{len(areas)} 完全一致")
if diffs:
    print("存在差异: 逐一确认变化位置的型号是否为 suspect 退出所致, 否则不得提交")
