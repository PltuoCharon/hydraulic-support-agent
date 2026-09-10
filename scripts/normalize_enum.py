import sys, csv, os
sys.path.insert(0, '.')
from app.config import settings
import pymysql

APPLY = '--apply' in sys.argv

MAP_GAS = {
    "低瓦斯": "低瓦斯",
    "低瓦斯煤层涌出量大": "低瓦斯",
    "高瓦斯(400m3/min)": "高瓦斯",
    "高瓦斯突出矿区": "突出",
    "涌出量大": None,
}
MAP_ROOF = {
    "破碎": "1类-不稳定", "顶板弱易冒落": "1类-不稳定",
    "顶板强度低易冒落": "1类-不稳定", "中等冒落顶板": "1类-不稳定",
    "中等稳定": "2类-中等稳定", "直接顶2类": "2类-中等稳定",
    "直接顶2类,基本顶II级": "2类-中等稳定",
    "直接顶2类中等稳定,基本顶II级": "2类-中等稳定",
    "直接顶2类老顶1类": "2类-中等稳定",
    "坚硬": "4类-坚硬", "直接顶K2石灰岩坚硬": "4类-坚硬",
    "直接顶K2石灰岩II级坚硬": "4类-坚硬", "基本顶14m石灰岩": "4类-坚硬",
    "浅埋薄基岩": None, "浅埋": None, "深部": None,
    "复杂": None, "冲击": None, "特厚煤层综放": None,
    "直接顶粉砂岩,基本顶中细砂岩": None, "顶板泥岩粉砂岩": None,
    "直接顶中粒砂岩": None,
}

def main():
    conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
        password=settings.DB_PASSWORD, database=settings.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    nulled = []
    for tbl, col, ncol, mp in [
        ("working_conditions", "gas_level", "gas_level_norm", MAP_GAS),
        ("mining_areas", "gas_level", "gas_level_norm", MAP_GAS),
        ("working_conditions", "roof_condition", "roof_class", MAP_ROOF),
        ("mining_areas", "roof_category", "roof_class", MAP_ROOF),
    ]:
        for raw, norm in mp.items():
            cur.execute(f"SELECT COUNT(*) AS n FROM {tbl} WHERE {col}=%s", (raw,))
            n = cur.fetchone()["n"]
            if n == 0:
                continue
            tag = norm if norm else "NULL(无法归一,原文保留)"
            print(f"{tbl}.{col}: [{raw}] x{n} -> {tag}")
            if norm is None:
                nulled.append((tbl, col, raw, n))
            if APPLY:
                cur.execute(f"UPDATE {tbl} SET {ncol}=%s WHERE {col}=%s",
                            (norm, raw))
    # 检查:有没有映射表之外漏网的非空原值
    for tbl, col, ncol, mp in [
        ("working_conditions", "gas_level", "gas_level_norm", MAP_GAS),
        ("mining_areas", "gas_level", "gas_level_norm", MAP_GAS),
        ("working_conditions", "roof_condition", "roof_class", MAP_ROOF),
        ("mining_areas", "roof_category", "roof_class", MAP_ROOF),
    ]:
        cur.execute(f"SELECT DISTINCT {col} AS v FROM {tbl} "
                    f"WHERE {col} IS NOT NULL AND {ncol} IS NULL")
        miss = [r["v"] for r in cur.fetchall() if r["v"] not in mp or mp[r["v"]]]
        for v in miss:
            print(f"!! 漏网原值 {tbl}.{col}=[{v}] 不在映射表,需人工补")
    os.makedirs("docs/thesis_data", exist_ok=True)
    if nulled:
        import datetime
        fp = f"docs/thesis_data/enum_nulled_{datetime.date.today():%Y%m%d}.csv"
        with open(fp, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["table", "column", "raw_value", "rows"])
            w.writerows(nulled)
        print(f"置NULL留痕: {fp} ({len(nulled)}类)")
    if APPLY:
        conn.commit()
        print("已提交")
    else:
        print("DRY-RUN,加 --apply 执行")
    conn.close()

if __name__ == "__main__":
    main()
