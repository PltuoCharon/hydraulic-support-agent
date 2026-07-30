import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np

engine = create_engine(
    "mysql+pymysql://hs_user:zyb123@127.0.0.1:3306/hydraulic_support?charset=utf8mb4"
)

df = pd.read_excel("data/矿区工况.xlsx")

def safe_val(val):
    if pd.isna(val):
        return None
    return val

with engine.begin() as conn:
    inserted = 0
    skipped = 0
    
    for _, r in df.iterrows():
        name = safe_val(r.get("name"))
        if not name:
            continue
            
        # 检查是否已存在
        exists = conn.execute(
            text("SELECT COUNT(*) FROM mining_areas WHERE name = :n"),
            {"n": name}
        ).scalar()
        
        if exists:
            skipped += 1
            continue
        
        # 插入完整数据
        conn.execute(
            text("""
                INSERT INTO mining_areas 
                (area_name, name, mine_name, location, category, depth,
                 mining_height_min, mining_height_max, dip_angle, hardness_f,
                 roof_category, floor_pressure, mine_pressure, gas_level,
                 face_length, support_model, source)
                VALUES 
                (:area_name, :name, :mine_name, :location, :category, :depth,
                 :mining_height_min, :mining_height_max, :dip_angle, :hardness_f,
                 :roof_category, :floor_pressure, :mine_pressure, :gas_level,
                 :face_length, :support_model, :source)
            """),
            {
                "area_name": name,
                "name": name,
                "mine_name": safe_val(r.get("mine_name", "未知矿井")),
                "location": safe_val(r.get("location", "未知位置")),
                "category": safe_val(r.get("category")),
                "depth": safe_val(r.get("depth")),
                "mining_height_min": safe_val(r.get("mining_height_min")),
                "mining_height_max": safe_val(r.get("mining_height_max")),
                "dip_angle": safe_val(r.get("dip_angle")),
                "hardness_f": safe_val(r.get("hardness_f")),
                "roof_category": safe_val(r.get("roof_category")),
                "floor_pressure": safe_val(r.get("floor_pressure")),
                "mine_pressure": safe_val(r.get("mine_pressure")),
                "gas_level": safe_val(r.get("gas_level")),
                "face_length": safe_val(r.get("face_length")),
                "support_model": safe_val(r.get("support_model")),
                "source": safe_val(r.get("source"))
            }
        )
        inserted += 1
    
    total = conn.execute(text("SELECT COUNT(*) FROM mining_areas")).scalar()
    print(f"✅ 导入完成：新增 {inserted} 条，跳过 {skipped} 条")
    print(f"📊 mining_areas 表现有 {total} 行")

