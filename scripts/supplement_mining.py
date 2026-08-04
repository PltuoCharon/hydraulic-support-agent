"""补录 mining_areas 缺失字段"""

import pandas as pd
from sqlalchemy import create_engine, text

ENGINE_URL = "mysql+pymysql://hs_user:zyb123@127.0.0.1:3306/hydraulic_support?charset=utf8mb4"
engine = create_engine(ENGINE_URL)


def supplement():
    """从 CSV 补录缺失字段"""
    
    # 读取补录数据
    df = pd.read_csv("data/supplement_mining.csv")
    print(f"补录文件: {len(df)} 条记录")
    
    with engine.begin() as conn:
        updated = 0
        
        for _, row in df.iterrows():
            # 只更新 NULL 字段
            result = conn.execute(text("""
                UPDATE mining_areas 
                SET 
                    depth = COALESCE(depth, :depth),
                    hardness_f = COALESCE(hardness_f, :hardness_f),
                    roof_category = COALESCE(roof_category, :roof_category),
                    floor_pressure = COALESCE(floor_pressure, :floor_pressure),
                    mine_pressure = COALESCE(mine_pressure, :mine_pressure),
                    face_length = COALESCE(face_length, :face_length)
                WHERE name = :name
            """), {
                "name": row['name'],
                "depth": row['depth'] if pd.notna(row['depth']) else None,
                "hardness_f": row['hardness_f'] if pd.notna(row['hardness_f']) else None,
                "roof_category": row['roof_category'] if pd.notna(row['roof_category']) else None,
                "floor_pressure": row['floor_pressure'] if pd.notna(row['floor_pressure']) else None,
                "mine_pressure": row['mine_pressure'] if pd.notna(row['mine_pressure']) else None,
                "face_length": row['face_length'] if pd.notna(row['face_length']) else None
            })
            
            if result.rowcount > 0:
                updated += 1
                print(f"  ✓ {row['name']}")
        
        print(f"\n✅ 更新 {updated} 条记录")
    
    # 验证补录结果
    print("\n=== 补录后验证 ===")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) AS 总数,
                SUM(CASE WHEN floor_pressure IS NULL THEN 1 ELSE 0 END) AS 底板比压缺失,
                SUM(CASE WHEN hardness_f IS NULL THEN 1 ELSE 0 END) AS f值缺失,
                SUM(CASE WHEN face_length IS NULL THEN 1 ELSE 0 END) AS 面长缺失,
                SUM(CASE WHEN mine_pressure IS NULL THEN 1 ELSE 0 END) AS 矿压缺失,
                SUM(CASE WHEN depth IS NULL THEN 1 ELSE 0 END) AS 埋深缺失
            FROM mining_areas
        """))
        row = result.fetchone()
        print(f"总数: {row.总数}")
        print(f"底板比压缺失: {row.底板比压缺失}")
        print(f"f值缺失: {row.f值缺失}")
        print(f"面长缺失: {row.面长缺失}")
        print(f"矿压缺失: {row.矿压缺失}")
        print(f"埋深缺失: {row.埋深缺失}")


if __name__ == "__main__":
    supplement()
