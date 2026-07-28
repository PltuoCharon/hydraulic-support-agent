import pandas as pd

# 1. 读入
df = pd.read_excel("data/支架参数.xlsx")
print("== 全部数据 ==")
print(df.head())

# 2. 条件筛选：阻力 ≥ 10000 的架型
big = df[df["阻力kN"] >= 10000]
print("\n== 高阻力架型 ==")
print(big[["型号", "阻力kN"]])

# 3. 导出（utf-8-sig 保证 Excel 打开不乱码）
big.to_csv("data/高阻力支架.csv", index=False, encoding="utf-8-sig")
print("\n已导出 data/高阻力支架.csv")
