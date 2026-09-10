"""
W25-D5: 支护强度(intensity)复算回填
q = R/(B*L)/1000  (MPa, 上限口径)
只填 intensity 为空的行, 绝不覆盖已有标称值;
L为估算值的行标注"二阶估算"; 黑名单行跳过。
用法:
  python scripts/fill_intensity.py          # dry-run
  python scripts/fill_intensity.py --apply  # 落库
"""
import sys, pymysql
try:
    from app.core.numparse import parse_number
except Exception:
    import re
    def parse_number(v, ndigits=4):
        if v is None: return None
        if isinstance(v, (int, float)): return float(v)
        s = str(v).strip().replace("～", "~")
        nums = re.findall(r"\d+(?:\.\d+)?", s)
        if not nums: return None
        vals = [float(x) for x in nums[:2]]
        return round(sum(vals) / len(vals), ndigits)

from app.config import settings

APPLY = "--apply" in sys.argv
BLACKLIST = ["ZYR200/16/32"]   # W25-D4立案待查行, 禁止回填

conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
                       password=settings.DB_PASSWORD,
                       database=settings.DB_NAME, charset="utf8mb4")
cur = conn.cursor()
cur.execute("""SELECT id, model, working_resistance, center_dist, canopy_len, source
               FROM support_models
               WHERE (intensity IS NULL OR intensity='')
                 AND working_resistance IS NOT NULL
                 AND center_dist IS NOT NULL
                 AND canopy_len IS NOT NULL AND canopy_len > 0""")
rows = cur.fetchall()
plan, skip = [], []
for rid, model, R, B, L, src in rows:
    if model in BLACKLIST:
        skip.append((model, "立案黑名单")); continue
    Rf, Bf, Lf = parse_number(R), parse_number(B), parse_number(L)
    if not Rf or not Bf or not Lf:
        skip.append((model, "R/B/L解析失败")); continue
    q = round(Rf / (Bf * Lf) / 1000, 2)
    second = src and "按架型经验估算" in src
    tag = "支护强度按P/(B·L)复算估算(二阶估算,L为经验值)" if second \
        else "支护强度按P/(B·L)复算估算(上限口径)"
    plan.append((rid, model, q, tag, bool(second)))

n2 = sum(1 for p in plan if p[4]); n1 = len(plan) - n2
print(f"{'正式回填' if APPLY else '试运行'}: 计划 {len(plan)} 条 "
      f"(一阶 {n1} / 二阶 {n2}), 跳过 {len(skip)} 条: {[s[0] for s in skip]}")
for p in plan[:20]:
    print(f"  {p[1]:<22} -> q={p[2]:<6} [{p[3][:14]}...]")
if len(plan) > 20: print(f"  ... 其余 {len(plan)-20} 条略")

if APPLY:
    n = 0
    for rid, model, q, tag, _ in plan:
        cur.execute(
            "UPDATE support_models SET intensity=%s, "
            "source=CONCAT(LEFT(COALESCE(source,''),60), IF(CHAR_LENGTH(source)>60,'…',''), ' | ', %s) "
            "WHERE id=%s AND (intensity IS NULL OR intensity='')",
            (str(q), tag, rid))
        n += cur.rowcount
    conn.commit()
    print(f"已更新 {n} 行 (与计划 {len(plan)} 不一致则说明有并发改动, 需复查)")
cur.close(); conn.close()
