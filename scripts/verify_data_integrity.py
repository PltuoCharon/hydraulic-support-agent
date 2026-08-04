"""数据完整性验证：对账 + 孤儿记录检查"""

import pandas as pd
from sqlalchemy import create_engine, text

ENGINE_URL = "mysql+pymysql://hs_user:zyb123@127.0.0.1:3306/hydraulic_support?charset=utf8mb4"
engine = create_engine(ENGINE_URL)


def check_excel_vs_db():
    """Excel 行数 ≤ 数据库行数"""
    results = []
    
    # 支架型号
    xl = pd.read_excel("data/raw/支架型号.xlsx")
    with engine.connect() as conn:
        db = conn.execute(text("SELECT COUNT(*) FROM support_models")).scalar()
    results.append(("支架型号", len(xl), db, db >= len(xl)))
    
    # 矿区工况
    xl = pd.read_excel("data/raw/矿区工况.xlsx")
    with engine.connect() as conn:
        db = conn.execute(text("SELECT COUNT(*) FROM mining_areas")).scalar()
    results.append(("矿区工况", len(xl), db, db >= len(xl)))
    
    return results


def check_orphan_records():
    """检查孤儿记录"""
    checks = []
    
    with engine.connect() as conn:
        # working_conditions → mining_areas
        r = conn.execute(text("""
            SELECT COUNT(*) FROM working_conditions w
            LEFT JOIN mining_areas m ON w.area_id = m.id 
            WHERE m.id IS NULL
        """)).scalar()
        checks.append(("wc→mining_areas", r))
        
        # support_parts → support_models
        r = conn.execute(text("""
            SELECT COUNT(*) FROM support_parts p
            LEFT JOIN support_models m ON p.model_id = m.id 
            WHERE m.id IS NULL
        """)).scalar()
        checks.append(("sp→support_models", r))
        
        # working_conditions → support_models
        r = conn.execute(text("""
            SELECT COUNT(*) FROM working_conditions w
            LEFT JOIN support_models m ON w.support_model_id = m.id 
            WHERE w.support_model_id IS NOT NULL AND m.id IS NULL
        """)).scalar()
        checks.append(("wc→support_models", r))
    
    return checks


def main():
    print("=" * 50)
    print("数据完整性验证")
    print("=" * 50)
    
    # 对账
    print("\n--- 1. Excel vs 数据库对账 ---")
    all_pass = True
    for name, xl_cnt, db_cnt, ok in check_excel_vs_db():
        status = "✅" if ok else "❌"
        print(f"{status} {name}: Excel={xl_cnt}, DB={db_cnt}, DB≥Excel={ok}")
        if not ok:
            all_pass = False
    
    # 孤儿记录
    print("\n--- 2. 孤儿记录检查 ---")
    for name, cnt in check_orphan_records():
        status = "✅" if cnt == 0 else "❌"
        print(f"{status} {name}: 孤儿={cnt} (期望 0)")
        if cnt != 0:
            all_pass = False
    
    print("\n" + "=" * 50)
    if all_pass:
        print("🎉 所有检查通过！数据完整性 OK")
    else:
        print("⚠️ 发现异常，请检查数据")
    print("=" * 50)


if __name__ == "__main__":
    main()
