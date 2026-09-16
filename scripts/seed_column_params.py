"""column 参数出处挂库(param_dependencies) —— W33-D3, 幂等
口径: 只动 param_dependencies(参数表, 不在 data-v5 冻结三表内)。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pymysql
from app.config import settings

ROWS = [
    ("column_bore_series", "40,50,63,80,100,125,140,160,180,200,220,250,280,320,360,400,450,500", "mm",
     "立柱缸径标准系列(常用段)",
     "缸径反算后向上圆整所用系列", "calc_column",
     "GB/T 2348 液压缸缸径系列"),
    ("column_setting_ratio", "60~85", "%", "初撑力/工作阻力 校核区间",
     "初撑力比校核: 低于60%初撑不足, 高于85%安全裕度偏小(设计惯例)",
     "calc_column",
     "液压支架设计惯例: 初撑力比60%~85%"),
]

def main():
    conn = pymysql.connect(host=getattr(settings, "DB_HOST", "127.0.0.1"),
                           port=getattr(settings, "DB_PORT", 3306),
                           user=settings.DB_USER, password=settings.DB_PASSWORD,
                           database=settings.DB_NAME)
    cur = conn.cursor()
    for name, val, unit, note, desc, cat, src in ROWS:
        cur.execute("SELECT id FROM param_dependencies WHERE param_name=%s", (name,))
        if cur.fetchone():
            print(f"跳过(已存在): {name}")
            continue
        cur.execute(
            "INSERT INTO param_dependencies(param_name,param_value,unit,note,description,category,source)"
            " VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (name, val, unit, note, desc, cat, src))
        print(f"入库: {name}")
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM param_dependencies")
    print("param_dependencies 总行数:", cur.fetchone()[0])
    conn.close()

if __name__ == "__main__":
    main()
