import pandas as pd

df = pd.read_excel("data/支架型号.xlsx")
print(f"总型号数：{len(df)}（≥100 {'✅' if len(df)>=100 else '❌'}）")

# 1. 架型覆盖
print("\n架型分布："); print(df["type"].value_counts())

# 2. 高度谱系连续性（薄煤层端与大采高端必须有人）
thin = df[df.height_min <= 1.0]
high = df[df.height_max >= 5.5]
print(f"\n薄煤层端(最低≤1.0m)：{len(thin)} 型 {'✅' if len(thin)>=5 else '❌'}")
print(f"大采高端(最高≥5.5m)：{len(high)} 型 {'✅' if len(high)>=8 else '❌'}")
print(f"高度范围：{df.height_min.min()} ~ {df.height_max.max()} m")

# 3. 零编造自查：来源空/型号解码不一致
print(f"\n缺来源：{df['source'].isna().sum()} 行")
mismatch = df[(df.resistance <= 0) | (df.height_min >= df.height_max)]
print(f"参数逻辑异常（高度min≥max 或 阻力≤0）：{len(mismatch)} 行")

# 4. 阻力谱
print(f"\n阻力范围：{df.resistance.min()} ~ {df.resistance.max()} kN")
print("阻力分档：")
print(pd.cut(df.resistance, [0,5000,9000,13000,18000,30000]).value_counts().sort_index())
