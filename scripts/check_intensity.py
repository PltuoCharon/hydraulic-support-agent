"""
W25-D4: 全表支护强度复算核对
q_calc = working_resistance / (center_dist * canopy_len) / 1000   (MPa)
与库内 intensity(varchar, 可为区间) 对比, 输出偏差分布, 偏差>20%列入核查清单。
产出: docs/thesis_data/intensity_check_YYYYMMDD.csv  (论文数据治理素材)
"""
import csv, datetime, pymysql
try:
    from app.core.numparse import parse_number
except Exception:
    import re
    def parse_number(v, ndigits=4):
        """numparse 降级副本: Decimal/float/int→float; '1.0~1.045'区间→中值; 失败→None"""
        if v is None: return None
        if isinstance(v, (int, float)): return float(v)
        s = str(v).strip().replace("～", "~")
        nums = re.findall(r"\d+(?:\.\d+)?", s)
        if not nums: return None
        vals = [float(x) for x in nums[:2]]
        return round(sum(vals) / len(vals), ndigits)

from app.config import settings

conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
                       password=settings.DB_PASSWORD,
                       database=settings.DB_NAME, charset="utf8mb4")
cur = conn.cursor()
cur.execute("""SELECT id, model, working_resistance, center_dist, canopy_len, intensity
               FROM support_models ORDER BY working_resistance""")

results, skipped = [], []
for rid, model, R, B, L, q_db_raw in cur.fetchall():
    Rf, Bf, Lf = parse_number(R), parse_number(B), parse_number(L)
    q_db = parse_number(q_db_raw)
    if not Rf or not Bf or not Lf:
        skipped.append((model, "缺R/B/L")); continue
    q_calc = Rf / (Bf * Lf) / 1000
    if q_db is None:
        skipped.append((model, "intensity为空(待D5回填)")); continue
    dev = (q_calc - q_db) / q_db * 100
    results.append((model, Rf, Bf, Lf, q_db, round(q_calc, 4), round(dev, 1)))
cur.close(); conn.close()

# ---- 偏差分布 ----
buckets = {"0~5%": 0, "5~10%": 0, "10~20%": 0, ">20%(核查)": 0}
for r in results:
    a = abs(r[6])
    if a <= 5: buckets["0~5%"] += 1
    elif a <= 10: buckets["5~10%"] += 1
    elif a <= 20: buckets["10~20%"] += 1
    else: buckets[">20%(核查)"] += 1

print(f"\n===== 支护强度复算报告 {datetime.date.today()} =====")
print(f"总数可复算: {len(results)}  跳过: {len(skipped)}")
print("偏差分布:")
for k, v in buckets.items():
    print(f"  {k:>12}: {'#'*v} {v}")

review = [r for r in results if abs(r[6]) > 20]
print(f"\n偏差>20%核查清单 ({len(review)} 条):")
for r in review:
    print(f"  {r[0]:<22} 库内q={r[4]:<7} 复算q={r[5]:<7} 偏差={r[6]:+}%")

# ---- 归档 CSV ----
import os
os.makedirs("docs/thesis_data", exist_ok=True)
fp = f"docs/thesis_data/intensity_check_{datetime.date.today():%Y%m%d}.csv"
with open(fp, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["model", "R_kN", "B_m", "L_m", "q_db_MPa", "q_calc_MPa", "dev_pct"])
    w.writerows(results)
print(f"\n已归档: {fp}")
if skipped[:10]:
    print("跳过样例(前10):", skipped[:10])
