import pandas as pd

df = pd.read_excel("data/矿区工况.xlsx")
print(f"总行数：{len(df)}（≥15 {'✅' if len(df)>=15 else '❌'}）")

no_source = df[df["source"].isna()]
print(f"缺来源：{len(no_source)} 行 {'✅' if len(no_source)==0 else '❌'}")

for c in ["name", "support_model", "depth"]:
    n = df[c].isna().sum()
    print(f"{c} 缺失 {n} 行（{'✅ 关键项完整' if n==0 else '⚠️ 知网补录'}）")

cats = set(df["category"].str.replace("深部","").str[:4])
print(f"\n类别覆盖 {df['category'].nunique()} 种：{sorted(df['category'].unique())}")
