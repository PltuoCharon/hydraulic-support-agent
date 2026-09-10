"""
W25-D2/D3: 按"架型前缀+高度段"经验规则回填 canopy_len（有效控顶长度, m）
用法:
  python scripts/fill_canopy.py          # 试运行: 只打印计划, 不写库
  python scripts/fill_canopy.py --apply  # 正式回填
幂等: 只处理 canopy_len IS NULL 的行, 重复执行无副作用。
"""
import re, sys, pymysql
from app.config import settings

APPLY = "--apply" in sys.argv

# 规则表: (前缀匹配函数, 高度段判定) -> 估算值
def seg(hmax):
    """按最大支撑高度分段"""
    if hmax is None:  return "mid"
    h = float(hmax)
    if h < 1.8:  return "thin"
    if h < 3.5:  return "mid"
    if h <= 6.5: return "large"
    return "xlarge"

ZY_RULE  = {"thin": 3.9, "mid": 4.1, "large": 5.0, "xlarge": 5.9}

def estimate(model, height_max):
    """返回 (估算值, 规则说明) 或 (None, 原因)"""
    m = model.replace(" ", "").upper()
    s = seg(height_max)
    # 注意前缀匹配顺序: 长的先匹配
    if re.match(r"^ZF", m):                       # 放顶煤(含ZFS/ZFY/ZFA)
        return 5.9, "放顶煤架型,经验区间5.5~6.3取中值"
    if re.match(r"^ZZ", m):                       # 支撑掩护式(含ZZS)
        return round(ZY_RULE[s] + 0.3, 1), f"支撑掩护式,同段掩护式+0.3"
    if re.match(r"^ZY[GT]", m):                   # 过渡/端头(ZYG/ZYT)
        return round(ZY_RULE[s] + 0.2, 1), f"过渡/端头架,同段掩护式+0.2"
    if re.match(r"^ZY|^ZJY", m):                  # 掩护式(含ZYQ/ZYL)
        return ZY_RULE[s], f"掩护式,{s}段经验区间中值"
    if re.match(r"^ZD", m):                       # 垛式
        return 3.8, "垛式支架,经验区间3.6~4.0取中值"
    return None, "未知架型前缀,跳过待人工"

conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
                       password=settings.DB_PASSWORD,
                       database=settings.DB_NAME, charset="utf8mb4")
cur = conn.cursor()
cur.execute("SELECT id, model, height_max FROM support_models WHERE canopy_len IS NULL")
rows = cur.fetchall()
print(f"待回填: {len(rows)} 条  模式: {'正式回填' if APPLY else '试运行(不写库)'}")

ok, skip = 0, []
for rid, model, hmax in rows:
    val, rule = estimate(model, hmax)
    if val is None:
        skip.append((model, rule)); continue
    if APPLY:
        cur.execute(
            "UPDATE support_models SET canopy_len=%s, "
            "source=LEFT(CONCAT(COALESCE(source,''),' | 控顶长度按架型经验估算'),100) "
            "WHERE id=%s AND canopy_len IS NULL",   # 双保险: 并发下也不覆盖已有值
            (val, rid))
        assert cur.rowcount <= 1
    print(f"  {model:<22} 高度段hmax={hmax} -> canopy_len={val}  ({rule})")
    ok += 1

if APPLY:
    conn.commit()
print(f"\n{'已回填' if APPLY else '计划回填'} {ok} 条; 跳过 {len(skip)} 条: {[s[0] for s in skip]}")
cur.close(); conn.close()
