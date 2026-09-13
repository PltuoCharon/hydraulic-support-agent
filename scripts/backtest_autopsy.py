"""W27-D4 未命中归因验尸: 5个未中矿区逐个解剖。
用法: PYTHONPATH=. python scripts/backtest_autopsy.py"""
import sys
sys.path.insert(0, '.')
import pymysql
from app.config import settings
from app.services.matcher import run_match

MISS_AREAS = ["晋城寺河", "平朔安家岭", "大宁3#四五采区", "谢桥1341(3)", "龙固2301"]

def main():
    conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
        password=settings.DB_PASSWORD, database=settings.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    for name in MISS_AREAS:
        cur.execute("""SELECT a.id, a.name, a.coal_thickness, a.depth,
                              a.hardness_f, wc.mining_height, wc.dip_angle,
                              wc.roof_condition, wc.gas_level, s.model
                       FROM mining_areas a
                       JOIN working_conditions wc ON wc.area_id=a.id
                       LEFT JOIN support_models s ON wc.support_model_id=s.id
                       WHERE a.name=%s LIMIT 1""", (name,))
        t = cur.fetchone()
        print("=" * 64)
        print(f"【{name}】实际架型: {t['model']}")
        print(f"  靶参数: 煤厚{t['coal_thickness']} 采高{t['mining_height']} "
              f"倾角{t['dip_angle']}° 硬度f={t['hardness_f']} 埋深{t['depth']} "
              f"顶板[{t['roof_condition']}] 瓦斯[{t['gas_level']}]")
        r = run_match(area_id=t["id"], top_n=50)
        items = r["items"]
        print(f"  候选总数: {r['total']}")
        print("  --- Top5 ---")
        for i, it in enumerate(items[:5], 1):
            print(f"  {i}. {it['support_model']:<18} sim={it['similarity']:.4f} "
                  f"({it['area_name']}) cat={it.get('cat_detail')}")
        # 实际架型在完整榜单里的名次
        ranks = [i+1 for i, it in enumerate(items)
                 if it["support_model"] == t["model"]]
        if ranks:
            i = ranks[0] - 1
            print(f"  --- 实际架型排名: 第{ranks[0]}名 ---")
            print(f"      {items[i]['support_model']} sim={items[i]['similarity']:.4f} "
                  f"({items[i]['area_name']}) cat={items[i].get('cat_detail')}")
            for d in (items[i].get("diffs") or [])[:6]:
                print(f"      diff: {d}")
        else:
            print("  --- 实际架型: 不在候选池(池内无此型号案例) ---")
    conn.close()

if __name__ == "__main__":
    main()
