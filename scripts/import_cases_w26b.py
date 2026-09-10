import sys
sys.path.insert(0, '.')
from app.config import settings
import pymysql

APPLY = '--apply' in sys.argv

MODELS = [
    ("ZFY18000/27/50", 18000, 2.7, 5.0, 1.75, "1.4~1.5",
     "文献:长城煤矿在用(郝翰等)"),
    ("ZY2400/10/26", 2400, 1.0, 2.6, 1.5, None,
     "文献:徐万军等,通安煤矿Ⅲ上煤"),
    ("ZY10000/26/56", 10000, 2.6, 5.6, 1.75, "1.13~1.19",
     "文献:孟庆坤,淮北三软煤层设计参数,非生产实测"),
]

AREAS = [
    ("桃园矿", 2.84, 28.0, "文献:宋维德等,桃园1034综采面"),
    ("通安煤矿", 4.40, 24.0, "文献:徐万军等,Ⅲ上煤,倾角20~28取中值24"),
    ("下沟煤矿", 16.80, 7.0, "文献:闫少宏等,ZF1802综放面,埋深325m"),
]

CASES = [
    ("桃园矿", "1034", "ZY6800/19/40", 2.84, 28.0, 2.84,
     "文献:宋维德等,一次采全高,81架"),
    ("通安煤矿", "Ⅲ上煤综采面", "ZY2400/10/26", 4.40, 24.0, None,
     "文献:徐万军等,采高文献未明确(架高上限2.6<煤厚4.4)"),
    ("下沟煤矿", "ZF1802综放面", None, 16.80, 7.0, None,
     "文献:闫少宏等,文献未给出具体架型型号及采高"),
]

def main():
    conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
        password=settings.DB_PASSWORD, database=settings.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    for m, r, h1, h2, cd, itn, src in MODELS:
        cur.execute("SELECT id FROM support_models WHERE model=%s", (m,))
        row = cur.fetchone()
        if row:
            print(f"架型复用 {m} id={row[chr(105)+chr(100)] if False else row['id']}")
        else:
            print(f"{'插入' if APPLY else '将插入'}架型 {m}")
            if APPLY:
                cur.execute("""INSERT INTO support_models
                    (model, working_resistance, height_min, height_max,
                     center_dist, intensity, source)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (m, r, h1, h2, cd, itn, src))
    area_ids = {}
    for name, coal, dip, src in AREAS:
        cur.execute("SELECT id FROM mining_areas WHERE name=%s", (name,))
        row = cur.fetchone()
        if row:
            area_ids[name] = row["id"]
            print(f"矿区复用 {name} id={row['id']}")
        elif APPLY:
            cur.execute("""INSERT INTO mining_areas
                (name, area_name, coal_thickness, dip_angle, source, is_test)
                VALUES (%s,%s,%s,%s,%s,0)""",
                (name, name, coal, dip, src))
            area_ids[name] = cur.lastrowid
            print(f"插入矿区 {name} id={cur.lastrowid}")
        else:
            print(f"将插入矿区 {name}")
    for aname, face, model, coal, dip, mh, src in CASES:
        aid = area_ids.get(aname)
        if aid is None:
            cur.execute("SELECT id FROM mining_areas WHERE name=%s", (aname,))
            r = cur.fetchone()
            aid = r["id"] if r else -1
        cur.execute("""SELECT id FROM working_conditions
            WHERE working_face_name=%s AND area_id=%s""", (face, aid))
        if cur.fetchone():
            print(f"案例已存在,跳过 {aname}/{face}")
            continue
        mid = None
        if model:
            cur.execute("SELECT id FROM support_models WHERE model=%s", (model,))
            r = cur.fetchone()
            mid = r["id"] if r else None
            if mid is None:
                print(f"!! 架型未找到 {model},案例以外键NULL插入")
        print(f"{'插入' if APPLY else '将插入'}案例 {aname}/{face} model={model} aid={aid}")
        if APPLY and aid != -1:
            cur.execute("""INSERT INTO working_conditions
                (area_id, support_model_id, working_face_name,
                 coal_thickness, dip_angle, mining_height, source)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (aid, mid, face, coal, dip, mh, src))
    if APPLY:
        conn.commit()
        print("已提交")
    else:
        print("DRY-RUN,加 --apply 执行")
    conn.close()

if __name__ == "__main__":
    main()
