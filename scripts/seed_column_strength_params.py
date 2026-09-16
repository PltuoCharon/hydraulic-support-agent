"""W33-D4: 立柱强度参数挂库 —— param_dependencies(27SiMn sigma_s) + dict_enum(材料条目), 幂等
口径: 只动参数表/字典表, 不碰 data-v5 冻结三表; sigma_b 未核到出处, 不入库(未查到公开参数)。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pymysql
from app.config import settings

SRC_SUN = "孙萌《综采液压支架双伸缩立柱强度分析及疲劳寿命预估研究》"
SRC_WALL = "吕晶霞等《液压千斤顶缸筒壁厚的计算及设计研究》引《液压工程手册》"

PARAM_ROWS = [
    ("mat_27simn_sigma_s", "835", "MPa", "27SiMn 屈服强度",
     "同文校核实例: 1.5倍额定载荷中缸656.7MPa<835MPa, 安全系数1.27; sigma_b未查到公开参数",
     "calc_column_strength", SRC_SUN),
    ("column_wall_formula", "thin/mid/thick", "-", "缸筒壁厚三档公式口径",
     "薄壁delta=pD/2[sigma]; 中壁delta=pD/(2.3[sigma]-3p); 厚壁拉美式; 按delta/D自动判档",
     "calc_column_strength", SRC_WALL),
]

ENUM_ROWS = [
    ("cylinder_material", "27SiMn", "27SiMn σs=835MPa(孙萌论文); σb未查到公开参数"),
]

def main():
    conn = pymysql.connect(host=getattr(settings, "DB_HOST", "127.0.0.1"),
                           port=getattr(settings, "DB_PORT", 3306),
                           user=settings.DB_USER, password=settings.DB_PASSWORD,
                           database=settings.DB_NAME)
    cur = conn.cursor()
    for name, val, unit, note, desc, cat, src in PARAM_ROWS:
        cur.execute("SELECT id FROM param_dependencies WHERE param_name=%s", (name,))
        if cur.fetchone():
            print(f"跳过(已存在): {name}")
            continue
        cur.execute(
            "INSERT INTO param_dependencies(param_name,param_value,unit,note,description,category,source)"
            " VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (name, val, unit, note, desc, cat, src))
        print(f"入库: {name}")
    for field, code, label in ENUM_ROWS:
        cur.execute("SELECT id FROM dict_enum WHERE field_name=%s AND code=%s", (field, code))
        if cur.fetchone():
            print(f"跳过(已存在): {field}/{code}")
            continue
        cur.execute("INSERT INTO dict_enum(field_name,code,label) VALUES(%s,%s,%s)",
                    (field, code, label))
        print(f"入库: {field}/{code}")
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM param_dependencies")
    print("param_dependencies 总行数:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM dict_enum")
    print("dict_enum 总行数:", cur.fetchone()[0])
    conn.close()

if __name__ == "__main__":
    main()
