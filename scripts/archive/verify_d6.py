import pandas as pd
from sqlalchemy import create_engine, text

# 验证 Excel
df = pd.read_excel("data/矿区工况.xlsx")
print("=" * 50)
print("Excel 验证")
print("=" * 50)
print(f"总行数: {len(df)}")
print(f"矿区数: {df['name'].nunique()}")
print(f"来源缺失行: {df['source'].isna().sum()}")
assert len(df) >= 15, "Excel 行数不足15"
assert df['source'].isna().sum() == 0, "存在来源缺失行"
print("✅ Excel 验证通过")

# 验证数据库
engine = create_engine("mysql+pymysql://hs_user:zyb123@127.0.0.1:3306/hydraulic_support?charset=utf8mb4")
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM mining_areas WHERE name IS NOT NULL"))
    db_count = result.scalar()
    print(f"\n数据库记录数: {db_count}")
    assert db_count >= 15, "数据库记录数不足15"
    print("✅ 数据库验证通过")

print("\n🎉 D6 验收全部通过！")

