"""
W26-D2/D3: 文献案例批量入库 (11案例/10新矿区/10新架型)
数据全部来自已上传文献, source 字段记出处; 型号/矿区已存在则复用(幂等)。
用法: python scripts/import_cases_w26.py [--apply]
"""
import sys, pymysql
from app.config import settings
APPLY = "--apply" in sys.argv

# (model, R_kN, h_min, h_max, center_dist, intensity, source)
MODELS = [
    ("ZY10800/30/65D", 10800, 3.0, 6.5, 1.75, "1.05~1.08", "纵帅等,煤矿机械2013(34)04"),
    ("ZY12000/25/55D", 12000, 2.5, 5.5, 1.75, "1.1~1.2",   "许梦斌,煤炭技术2022(41)07"),
    ("ZF15000/23/43",  15000, 2.3, 4.3, None, "1.46",       "查文华等,中国安全生产科学技术2014(10)08"),
    ("ZZ6000/17/32",    6000, 1.7, 3.2, None, None,          "闫振东,煤炭科学技术2012(40)11"),
    ("ZY6800/19/40",    6800, 1.9, 4.0, None, None,          "陈贵等,煤矿机械2011(32)04"),
    ("ZF7200/17/33",    7200, 1.7, 3.3, None, None,          "王鑫海,山东煤炭科技2023(06)"),
    ("ZY7000/09/18D",   7000, 0.9, 1.8, None, None,          "宋启等,煤矿机械2015(36)07"),
    ("ZY4000/09/20",    4000, 0.9, 2.0, None, None,          "宋启等,煤矿机械2015(36)07"),
    ("ZY10000/22/45D", 10000, 2.2, 4.5, 1.75, None,
     "张陟学位论文,中国矿业大学2023(表4-1作ZY7800/22/45D,与正文不一致,以正文实际生产为准)"),
    ("ZF9000/24/40",    9000, 2.4, 4.0, None, None,          "乔粉先,2019(09)"),
]

# (area_name, is_test, coal, dip, depth, category, roof, source)
AREAS = [
    ("谢桥1341(3)", 1, 5.00, 12.1, None, "大采高", "直接顶2类中等稳定,基本顶II级", "纵帅等,煤矿机械2013(34)04"),
    ("大宁3#四五采区", 1, 4.74, 5.0, 476.0, "大采高", "顶板泥岩粉砂岩", "许梦斌,煤炭技术2022(41)07"),
    ("龙固2301", 1, 9.20, 6.0, 864.0, "深井特厚综放", None, "查文华等,中国安全生产科学技术2014(10)08"),
    ("朱仙庄II1034", 1, 2.30, 24.0, None, "大倾角中厚", "直接顶中粒砂岩", "陈贵等,煤矿机械2011(32)04"),
    ("王台铺2306", 0, 2.52, 3.0, 155.0, "中厚坚硬顶板", "直接顶K2石灰岩II级坚硬", "闫振东,煤炭科学技术2012(40)11"),
    ("豹子沟10103", 0, 4.20, 5.0, None, "组合煤层综放", "基本顶14m石灰岩", "王鑫海,山东煤炭科技2023(06)"),
    ("南梁20302(1)", 0, 1.60, 1.6, None, "薄煤层刨煤机", "直接顶2类", "宋启等,煤矿机械2015(36)07"),
    ("祁南7122", 0, 1.30, 8.0, None, "薄煤层", "直接顶2类老顶1类", "宋启等,煤矿机械2015(36)07"),
    ("金家渠110301", 0, 3.70, 26.0, 190.0, "大倾角多断层", "顶板强度低易冒落", "张陟学位论文,中国矿业大学2023"),
    ("麻地沟13204", 0, 10.95, 20.0, None, "特厚综放", "中等冒落顶板", "乔粉先,2019(09)"),
]

# (area_name, face, model, coal, dip, mining_height, roof, gas, source)
# 注: 金鸡滩为在库矿区, 按 name 查 id
CASES = [
    ("谢桥1341(3)", "1341(3)", "ZY10800/30/65D", 5.00, 12.1, 6.0, "直接顶2类,基本顶II级", None, "纵帅等,煤矿机械2013(34)04"),
    ("金鸡滩", "08103", "ZY21000/38/82D", 7.10, 2.5, 6.8, "直接顶粉砂岩,基本顶中细砂岩", None, "郝翰等,2024(12)"),
    ("大宁3#四五采区", "四五采区", "ZY12000/25/55D", 4.74, 5.0, 5.28, "顶板泥岩粉砂岩", None, "许梦斌,煤炭技术2022(41)07"),
    ("龙固2301", "2301", "ZF15000/23/43", 9.20, 6.0, 4.0, "特厚煤层综放", None, "查文华等,中国安全生产科学技术2014(10)08"),
    ("王台铺2306", "2306", "ZZ6000/17/32", 2.52, 3.0, 2.5, "直接顶K2石灰岩坚硬", "低瓦斯", "闫振东,煤炭科学技术2012(40)11"),
    ("朱仙庄II1034", "II1034", "ZY6800/19/40", 2.30, 24.0, 2.3, "直接顶中粒砂岩", None, "陈贵等,煤矿机械2011(32)04"),
    ("豹子沟10103", "10103", "ZF7200/17/33", 4.20, 5.0, 2.8, "基本顶14m石灰岩", None, "王鑫海,山东煤炭科技2023(06)"),
    ("南梁20302(1)", "20302(1)", "ZY7000/09/18D", 1.60, 1.6, 1.4, "直接顶2类", None, "宋启等,煤矿机械2015(36)07"),
    ("祁南7122", "7122", "ZY4000/09/20", 1.30, 8.0, 1.3, "直接顶2类老顶1类", None, "宋启等,煤矿机械2015(36)07"),
    ("金家渠110301", "110301", "ZY10000/22/45D", 3.70, 26.0, 3.7, "顶板弱易冒落", None, "张陟学位论文,中国矿业大学2023"),
    ("麻地沟13204", "13204", "ZF9000/24/40", 10.95, 20.0, 3.5, "中等冒落顶板", None, "乔粉先,2019(09)"),
]

conn = pymysql.connect(host=settings.DB_HOST, user=settings.DB_USER,
                       password=settings.DB_PASSWORD,
                       database=settings.DB_NAME, charset="utf8mb4",
                       cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()
log = []

def upsert_model(m):
    model, R, hmin, hmax, cd, inten, src = m
    cur.execute("SELECT id FROM support_models WHERE model=%s", (model,))
    r = cur.fetchone()
    if r: log.append(f"架型复用: {model} -> id={r["id"]}"); return r["id"]
    if APPLY:
        cur.execute("""INSERT INTO support_models
            (model, working_resistance, height_min, height_max, center_dist, intensity, source, data_status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,\'verified\')""",
            (model, R, hmin, hmax, cd, inten, "文献: "+src))
        log.append(f"架型新增: {model} -> id={cur.lastrowid}")
        return cur.lastrowid
    log.append(f"架型待新增: {model}"); return None

def upsert_area(a):
    name, istest, coal, dip, depth, cat, roof, src = a
    cur.execute("SELECT id FROM mining_areas WHERE name=%s OR area_name=%s", (name, name))
    r = cur.fetchone()
    if r: log.append(f"矿区复用: {name} -> id={r["id"]}"); return r["id"]
    if APPLY:
        cur.execute("""INSERT INTO mining_areas
            (area_name, name, coal_thickness, dip_angle, depth, category, roof_category, source, is_test)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (name, name, coal, dip, depth, cat, roof, "文献: "+src, istest))
        log.append(f"矿区新增: {name}(is_test={istest}) -> id={cur.lastrowid}")
        return cur.lastrowid
    log.append(f"矿区待新增: {name}(is_test={istest})"); return None

def case_exists(area_id, face):
    cur.execute("SELECT id FROM working_conditions WHERE area_id=%s AND working_face_name=%s",
                (area_id, face))
    return cur.fetchone()

if APPLY:
    mid = {m[0]: upsert_model(m) for m in MODELS}
    aid = {a[0]: upsert_area(a) for a in AREAS}
    n_case = 0
    for area, face, model, coal, dip, mh, roof, gas, src in CASES:
        a_id = aid.get(area)
        if a_id is None and area == "金鸡滩":
            cur.execute("SELECT id FROM mining_areas WHERE name LIKE \'%金鸡滩%\'")
            r = cur.fetchone(); a_id = r["id"] if r else None
        if a_id is None: log.append(f"!! 矿区未找到, 跳过案例: {face}"); continue
        if case_exists(a_id, face): log.append(f"案例已存在, 跳过: {face}"); continue
        cur.execute("""INSERT INTO working_conditions
            (area_id, support_model_id, working_face_name, coal_thickness,
             dip_angle, mining_height, roof_condition, gas_level, source)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (a_id, mid.get(model), face, coal, dip, mh, roof, gas, "文献: "+src))
        n_case += 1
        log.append(f"案例新增: {face} (area_id={a_id}, model={model})")
    conn.commit()
    log.append(f"已提交: 新增案例 {n_case} 条")
else:
    for m in MODELS: upsert_model(m)
    for a in AREAS: upsert_area(a)
    log.append(f"试运行: 计划案例 {len(CASES)} 条 (金鸡滩按name模糊匹配)")

print("\n".join(log))
cur.close(); conn.close()
