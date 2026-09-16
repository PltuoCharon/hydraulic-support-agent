"""q_need 参数出处挂库(param_dependencies) —— W33-D1, 幂等
口径: 只动 param_dependencies(参数表, 不在 data-v5 冻结三表内), 不碰案例/架型/矿区。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pymysql
from app.config import settings

SRC = "纵帅等《大采高综采工作面液压支架选型研究及应用》谢桥矿实例"
ROWS = [
    ("q_need_k1", "6", "-", "载荷估算法影响系数(行业惯例6~8倍采高岩柱)",
     "p1=K1·hm·γ 系数; 谢桥实例取6", "calc_q_need", SRC),
    ("q_need_gamma", "25", "kN/m³", "顶板岩层容重",
     "p1=K1·hm·γ 容重; 谢桥实例取25", "calc_q_need", SRC),
    ("q_need_k_dynamic", "2", "-", "动载荷系数",
     "p2=K(15+0.8L1)×10⁻² 系数; 谢桥实例取2", "calc_q_need", SRC),
    ("q_need_p3_coeffs", "72.3,4.5,78.9,-10.24,-62.1", "-", "统计公式法回归系数",
     "p3=72.3hm+4.5Lp+78.9Bc-10.24N-62.1 (kPa); 统计回归式, 适用性以原文为准",
     "calc_q_need", SRC),
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
