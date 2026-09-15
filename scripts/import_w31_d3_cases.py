#!/usr/bin/env python3
"""W31-D3 案例入库:9条原文核验案例(矿区->架型->案例)
幂等:按唯一键先查后插,重复执行不产生重复行;任一步失败整体回滚。
连接参数取自 app.config.settings,不硬编码凭据。
用法: cd ~/hs_agent && python3 scripts/import_w31_d3_cases.py
"""
import sys
import pymysql
from app.config import settings

def get_conn():
    return pymysql.connect(
        host=getattr(settings, "DB_HOST", "127.0.0.1"),
        port=int(getattr(settings, "DB_PORT", 3306)),
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=getattr(settings, "DB_NAME", "hydraulic_support"),
        charset="utf8mb4", autocommit=False)

AREAS = [
 dict(name="榆家梁44305", coal=None, dip=None, depth=80.0, lng=None, lat=None,
      src="任艳芳,采矿与岩层控制工程学报2020,2(3):036012;浅埋80m"),
 dict(name="黄沙2上煤首采面", coal=0.75, dip=20.0, depth=None, lng=None, lat=None,
      src="谢德瑜,煤矿开采2011,16(5):59-60"),
 dict(name="田陈530", coal=1.65, dip=10.0, depth=None, lng=None, lat=None,
      src="盛国军等,煤炭学报2007,32(3):230-234"),
 dict(name="车集2901", coal=2.70, dip=None, depth=None, lng=None, lat=None,
      src="郑伟卫,2024(10):101-105;河南永煤车集矿"),
 dict(name="霍尔辛赫5110", coal=7.95, dip=None, depth=None, lng=None, lat=None,
      src="赵杰,2023(5):215-217"),
 dict(name="梧桐庄182605", coal=3.45, dip=None, depth=None, lng=None, lat=None,
      src="郭超等,煤炭与化工2023,46(5):71-74"),
 dict(name="榆树坡5105", coal=3.20, dip=None, depth=None, lng=None, lat=None,
      src="陈贵廷,煤炭与化工2020,43(5):97-98,107"),
 dict(name="磁窑沟13101", coal=11.58, dip=None, depth=None, lng=111.3180, lat=39.2920,
      src="杜伟剑等,煤炭与化工2022,45(2):62-66,70;坐标按原文井田经纬度(111°18'03\"~111°20'15\"E,39°16'29\"~39°18'31\"N)取中心换算"),
 dict(name="顾北13121", coal=7.60, dip=5.0, depth=None, lng=None, lat=None,
      src="康志鹏等,煤矿机械2022,43(6):131-134"),
]

MODELS = {
 "C1": dict(model="ZY10660/11/22", type="掩护式", wr=10660, hmin=1.10, hmax=2.20,
      intensity=None, initf=None, cdist=None, weight=None, floor_p=None, manuf=None,
      src="任艳芳,采矿与岩层控制工程学报2020,2(3):036012"),
 "C2": dict(model="ZY3300/07/13D", type="掩护式", wr=3300, hmin=0.70, hmax=1.30,
      intensity="0.42~0.48", initf=2618, cdist=1.50, weight=8.7, floor_p="1.74~1.76", manuf="天地科技",
      src="谢德瑜,煤矿开采2011,16(5):59-60;初撑力2618kN(31.5MPa)"),
 "C3": dict(model="ZY2400/09/20", type="掩护式", wr=2400, hmin=0.90, hmax=2.00,
      intensity=None, initf=2185, cdist=None, weight=None, floor_p=None, manuf=None,
      src="盛国军等,煤炭学报2007,32(3):230-234;原文型号ZY2400-0.9/2.0,支架宽1.43~1.60m"),
 "C4": dict(model="ZY6800/16/35D", type="掩护式", wr=6800, hmin=1.60, hmax=3.50,
      intensity=None, initf=None, cdist=None, weight=None, floor_p=None, manuf=None,
      src="郑伟卫,2024(10):101-105;选型计算最小支护强度0.3328MPa、阻力需求2645.76kN;电液控郑煤机ZE0704,支架厂商原文未述"),
 "C5": dict(model="ZF9000/18/35", type="放顶煤(低位)", wr=9000, hmin=1.80, hmax=3.50,
      intensity="1.10", initf=7760, cdist=1.50, weight=None, floor_p="2.72", manuf=None,
      src="赵杰,2023(5):215-217;移架步距600mm"),
 "C6": dict(model="ZZ6400/19/42D", type="支撑掩护式", wr=6400, hmin=1.70, hmax=3.50,
      intensity="0.75~0.8", initf=5232, cdist=1.50, weight=None, floor_p="2.3~2.5", manuf=None,
      src="郭超等,煤炭与化工2023,46(5):71-74;高度按原文参数表1.7~3.5m,与型号段/19/42不一致,留痕;移架步距630mm;适应倾角<45°"),
 "C7": dict(model="ZY8000/25/50", type="掩护式", wr=8000, hmin=2.50, hmax=5.00,
      intensity="1.09", initf=6392, cdist=1.75, weight=None, floor_p=None, manuf=None,
      src="陈贵廷,煤炭与化工2020,43(5):97-98,107;初撑力原文2.1.4节'639kN'系印刷错误,取参数表6392kN"),
 "C8": dict(model="ZFY15000/24/43D", type="放顶煤(两柱掩护)", wr=15000, hmin=2.40, hmax=4.30,
      intensity="1.63", initf=11928, cdist=1.75, weight=49.0, floor_p=None, manuf=None,
      src="杜伟剑等,煤炭与化工2022,45(2):62-66,70"),
 "C9": dict(model="ZZ13000/24/50", type="支撑掩护式", wr=13000, hmin=2.40, hmax=5.00,
      intensity="1.28~1.33", initf=10128, cdist=1.75, weight=None, floor_p="3.55", manuf=None,
      src="康志鹏等,煤矿机械2022,43(6):131-134;选型计算需求阻力12000kN;正文中心距1700mm与参数表1.75m矛盾,取参数表;移架步距0.8m;原文η取0.95"),
}

CASES = [
 dict(key="C1", area="榆家梁44305", face="榆家梁44305工作面", coal=None, mh=None, dip=None,
      roof=None, rclass=None, floor=None, gas=None, out=None,
      src="任艳芳,采矿与岩层控制工程学报2020,2(3):036012;浅埋80m;设计采高1.7~2.0m区间不单值化;初撑力达设计87%,周期下沉300mm,立柱完好率98%"),
 dict(key="C2", area="黄沙2上煤首采面", face="黄沙矿2上煤首采面", coal=0.75, mh=1.00, dip=20.0,
      roof="粉砂岩", rclass="1类", floor="粉砂岩", gas=None, out=720,
      src="谢德瑜,煤矿开采2011,16(5):59-60;倾角17~24°均20°;直接顶粉砂岩4~5m一类f=3;底板粉砂岩3~4m"),
 dict(key="C3", area="田陈530", face="田陈530工作面", coal=1.65, mh=1.65, dip=10.0,
      roof="砂质页岩", rclass=None, floor="砂质泥岩", gas=None, out=None,
      src="盛国军等,煤炭学报2007,32(3):230-234;煤厚0.8~2.3均1.65;采高最大1.9最小1.1;倾角8~13°均10°;直接顶砂质页岩3.8m f=6~8;直接底砂质泥岩2~4m;瓦斯OCR不完整不采用"),
 dict(key="C4", area="车集2901", face="车集2901工作面", coal=2.70, mh=2.70, dip=None,
      roof="泥岩", rclass=None, floor="砂质泥岩", gas=None, out=None,
      src="郑伟卫,2024(10):101-105;河南永煤车集矿;2-2煤层厚2.7m;倾角8~16°无均值不单值化;直接顶泥岩1.67m,基本顶中粒砂岩2.89m,直接底砂质泥岩3m"),
 dict(key="C5", area="霍尔辛赫5110", face="霍尔辛赫5110工作面", coal=7.95, mh=3.00, dip=None,
      roof="中等稳定", rclass=None, floor=None, gas=None, out=None,
      src="赵杰,2023(5):215-217;煤厚7.95m=采3.0+放4.95;直接顶1.37m中等稳定,老顶10.25m基本顶Ⅱ级;直接底2.0m容许比压2.2MPa;初垮9~15m,初来压37~40m,周期来压16~25m"),
 dict(key="C6", area="梧桐庄182605", face="梧桐庄182605工作面", coal=3.45, mh=3.60, dip=None,
      roof="粉砂岩", rclass=None, floor="粉砂岩", gas=None, out=None,
      src="郭超等,煤炭与化工2023,46(5):71-74;2号煤均3.45m,最大采高3.6m;倾角里段6°、外段6~44°无均值;直接顶粉砂岩5.71m,基本顶中粒砂岩3.30m,直接底粉砂岩2.40m;支护强度三法并算:岩重0.542~0.723/顶板分类0.801/传递岩梁0.823~0.8705→≥0.823MPa"),
 dict(key="C7", area="榆树坡5105", face="榆树坡5105工作面", coal=3.20, mh=3.26, dip=None,
      roof="中等稳定", rclass=None, floor="泥岩", gas=None, out=5000,
      src="陈贵廷,煤炭与化工2020,43(5):97-98,107;3号煤2.97~3.38均3.2m,平均采高3.26m;倾角4~12°无均值;直接顶泥岩6.53m,老顶细粒砂岩3.10m,顶板中等稳定,直接底泥岩0.40m"),
 dict(key="C8", area="磁窑沟13101", face="磁窑沟13101工作面", coal=11.58, mh=4.00, dip=None,
      roof="泥岩", rclass=None, floor="泥岩", gas=None, out=None,
      src="杜伟剑等,煤炭与化工2022,45(2):62-66,70;13号特厚煤2.90~19.40均11.58m,割煤高4.0m综放;地层倾角4~9°无均值;顶板泥岩/砂质泥岩/细砂岩,底板泥岩"),
 dict(key="C9", area="顾北13121", face="顾北13121工作面", coal=7.60, mh=4.50, dip=5.0,
      roof="泥岩", rclass=None, floor="砂质泥岩", gas=None, out=None,
      src="康志鹏等,煤矿机械2022,43(6):131-134;采区煤厚2.59~10.17均7.6m,上分层第1层最大采厚4.5m;倾角5°,支架适应6~8°俯采;直接顶泥岩0~4.0均1.8m(中部缺失砂岩直覆),老顶粉细砂岩1.2~18.4均7m;直接底砂质泥岩0.2~11.5均2.6m;矿压实测:初压前22.8~28.7MPa,来压后30.7~39.4MPa"),
]

def get_or_insert_area(cur, a):
    cur.execute("SELECT id FROM mining_areas WHERE name=%s", (a["name"],))
    row = cur.fetchone()
    if row:
        return row[0], False
    cur.execute(
        "INSERT INTO mining_areas (area_name,name,coal_thickness,dip_angle,depth,lng,lat,source,is_test)"
        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0)",
        (a["name"], a["name"], a["coal"], a["dip"], a["depth"], a["lng"], a["lat"], a["src"]))
    return cur.lastrowid, True

def get_or_insert_model(cur, m):
    cur.execute("SELECT id FROM support_models WHERE model=%s", (m["model"],))
    row = cur.fetchone()
    if row:
        return row[0], False
    cur.execute(
        "INSERT INTO support_models (model,type,working_resistance,height_min,height_max,"
        "manufacturer,center_dist,intensity,initial_force,floor_pressure,weight,source,data_status)"
        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'verified')",
        (m["model"], m["type"], m["wr"], m["hmin"], m["hmax"], m["manuf"],
         m["cdist"], m["intensity"], m["initf"], m["floor_p"], m["weight"], m["src"]))
    return cur.lastrowid, True

def insert_case(cur, c, area_id, model_id):
    cur.execute("SELECT id FROM working_conditions WHERE area_id=%s AND working_face_name=%s",
                (area_id, c["face"]))
    row = cur.fetchone()
    if row:
        return row[0], False
    cur.execute(
        "INSERT INTO working_conditions (area_id,support_model_id,working_face_name,coal_thickness,"
        "roof_condition,roof_class,floor_condition,dip_angle,gas_level,gas_level_norm,"
        "mining_height,daily_output,source) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (area_id, model_id, c["face"], c["coal"], c["roof"], c["rclass"], c["floor"],
         c["dip"], c["gas"], c["gas"], c["mh"], c["out"], c["src"]))
    return cur.lastrowid, True

def main():
    cn = get_conn()
    try:
        cur = cn.cursor()
        area_ids, model_ids = {}, {}
        n_a = n_m = n_c = 0
        for a in AREAS:
            aid, new = get_or_insert_area(cur, a)
            area_ids[a["name"]] = aid
            n_a += new
            print(f"矿区 {'新增' if new else '复用'} id={aid:>3}  {a['name']}")
        for key, m in MODELS.items():
            mid, new = get_or_insert_model(cur, m)
            model_ids[key] = mid
            n_m += new
            print(f"架型 {'新增' if new else '复用'} id={mid:>3}  {m['model']}")
        for c in CASES:
            cid, new = insert_case(cur, c, area_ids[c["area"]], model_ids[c["key"]])
            n_c += new
            print(f"案例 {'新增' if new else '复用'} id={cid:>3}  {c['key']} {c['face']} (area={area_ids[c['area']]}, model={model_ids[c['key']]})")
        cur.execute("SELECT COUNT(*) FROM mining_areas"); na = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM support_models"); nm = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM working_conditions"); nc = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM working_conditions WHERE support_model_id IS NULL")
        nnull = cur.fetchone()[0]
        print(f"\n本次新增: 矿区+{n_a} 架型+{n_m} 案例+{n_c}")
        print(f"库内总数: 矿区={na}(原31) 架型={nm}(原159) 案例={nc}(原41)")
        print(f"案例support_model_id为NULL的条数={nnull}(原1)")
        if nc < 50:
            raise RuntimeError(f"案例总数{nc}<50,未达标,回滚!")
        cn.commit()
        print("COMMIT 完成")
    except Exception as e:
        cn.rollback()
        print("ROLLBACK:", e, file=sys.stderr)
        sys.exit(1)
    finally:
        cn.close()

if __name__ == "__main__":
    main()
