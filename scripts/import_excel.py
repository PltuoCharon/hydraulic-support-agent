"""Excel 数据导入 MySQL：校验 → 去重 → 插入。可重复执行（幂等）。"""
import re
import pandas as pd
from sqlalchemy import create_engine, text

ENGINE_URL = "mysql+pymysql://hs_user:zyb123@127.0.0.1:3306/hydraulic_support?charset=utf8mb4"
engine = create_engine(ENGINE_URL)

def ensure_columns(conn, table, cols):
    """缺列则补列，保证脚本与库结构同步"""
    for col, typ in cols.items():
        try:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {typ}"))
            print(f"  [结构] {table} 新增列 {col}")
        except Exception:
            pass

def decode(model):
    m = re.search(r"[A-Z]+?(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)", str(model))
    if not m:
        return None
    return int(float(m.group(1))), float(m.group(2)) / 10, float(m.group(3)) / 10

# ---------- 1. 支架型号 ----------
def import_supports(conn):
    df = pd.read_excel("data/支架型号.xlsx")
    print(f"Excel 列名: {df.columns.tolist()}")
    
    ensure_columns(conn, "support_models", {
        "intensity": "VARCHAR(20)", "initial_force": "INT",
        "floor_pressure": "VARCHAR(20)", "weight": "FLOAT",
        "manufacturer": "VARCHAR(30)", "source": "VARCHAR(100)"})

    ok, reject, skip = 0, [], 0
    for _, r in df.iterrows():
        if pd.isna(r["model"]) or pd.isna(r["resistance"]):
            reject.append((r.get("model"), "必填缺失")); continue
        d = decode(r["model"])
        if d and (d[0] != r["resistance"] or abs(d[1] - r["height_min"]) > 0.05):
            reject.append((r["model"], "型号与参数不一致")); continue
        if conn.execute(text("SELECT COUNT(*) FROM support_models WHERE model=:m"),
                        {"m": r["model"]}).scalar():
            skip += 1; continue
        conn.execute(text("""
            INSERT INTO support_models (model, type, working_resistance, height_min, height_max,
                center_dist, canopy_len, intensity, initial_force, floor_pressure,
                weight, manufacturer, source)
            VALUES (:model,:type,:res,:h1,:h2,:cd,:cl,:it,:if_,:fp,:w,:mk,:src)
        """), {"model": r["model"], "type": r["type"], "res": int(r["resistance"]),
               "h1": r["height_min"], "h2": r["height_max"],
               "cd": r["center_dist"] if pd.notna(r["center_dist"]) else None,
               "cl": r["canopy_len"] if pd.notna(r.get("canopy_len")) else None,
               "it": r["intensity"] if pd.notna(r.get("intensity")) else None,
               "if_": int(r["initial_force"]) if pd.notna(r.get("initial_force")) else None,
               "fp": r["floor_pressure"] if pd.notna(r.get("floor_pressure")) else None,
               "w": r["weight"] if pd.notna(r.get("weight")) else None,
               "mk": r["manufacturer"] if pd.notna(r.get("manufacturer")) else None,
               "src": r["source"] if pd.notna(r.get("source")) else None})
        ok += 1
    print(f"[support_models] 插入 {ok}，跳过(已存在) {skip}，拒收 {len(reject)}")
    for m, why in reject:
        print(f"  拒收：{m} —— {why}")

# ---------- 2. 矿区台账 ----------
def import_areas(conn):
    df = pd.read_excel("data/矿区工况.xlsx")
    print(f"Excel 列名: {df.columns.tolist()}")
    
    ensure_columns(conn, "mining_areas", {
        "coal_thickness": "DECIMAL(5,2)",
        "category": "VARCHAR(20)", "dip_angle": "FLOAT", "hardness_f": "FLOAT",
        "gas_level": "VARCHAR(20)", "face_length": "FLOAT", "source": "VARCHAR(100)"})
    ok, skip = 0, 0
    for _, r in df.iterrows():
        if pd.isna(r["name"]) or pd.isna(r["source"]):
            print(f"  拒收：{r.get('name')} —— 名称或来源缺失"); continue
        if conn.execute(text("SELECT COUNT(*) FROM mining_areas WHERE name=:n"),
                        {"n": r["name"]}).scalar():
            skip += 1; continue
        # 同时插入 area_name 和 name
        conn.execute(text("""
            INSERT INTO mining_areas (area_name, name, coal_thickness, category, dip_angle,
                                      hardness_f, gas_level, face_length, source)
            VALUES (:an,:n,:h,:c,:d,:f,:g,:fl,:s)
        """), {"an": r["name"],  # area_name = name
               "n": r["name"],
               "h": r["mining_height_max"] if pd.notna(r["mining_height_max"]) else None,
               "c": r["category"],
               "d": r["dip_angle"] if pd.notna(r["dip_angle"]) else None,
               "f": r["hardness_f"] if pd.notna(r["hardness_f"]) else None,
               "g": r["gas_level"] if pd.notna(r["gas_level"]) else None,
               "fl": r["face_length"] if pd.notna(r["face_length"]) else None,
               "s": r["source"]})
        ok += 1
    print(f"[mining_areas] 插入 {ok}，跳过 {skip}")

with engine.begin() as conn:
    import_supports(conn)
    import_areas(conn)
print("导入完成")
