"""支架型号谱系完整性检查"""

import pandas as pd
import sys

def main():
    df = pd.read_excel("data/raw/支架型号.xlsx")
    
    print("=== 支架型号谱系检查 ===")
    total = len(df)
    print(f"总数: {total} {'✅' if total >= 100 else '❌'} (期望 ≥100)")
    
    # 按类型分类统计
    type_counts = df['type'].value_counts()
    print(f"\n类型分布:")
    for t, c in type_counts.items():
        print(f"  {t}: {c}")
    
    # 薄煤层端（最小高度 ≤ 1.5m）
    thin = df[df['height_min'] <= 1.5]
    print(f"\n薄煤层端 (height_min ≤ 1.5m): {len(thin)} {'✅' if len(thin) >= 10 else '❌'} (期望 ≥10)")
    
    # 大采高端（最大高度 ≥ 5.0m）
    large = df[df['height_max'] >= 5.0]
    print(f"大采高端 (height_max ≥ 5.0m): {len(large)} {'✅' if len(large) >= 15 else '❌'} (期望 ≥15)")
    
    # 逻辑异常检查
    anomalies = []
    
    # 异常1：最小高度 > 最大高度
    invalid_height = df[df['height_min'] > df['height_max']]
    if len(invalid_height) > 0:
        anomalies.append(f"最小高度>最大高度: {len(invalid_height)} 条")
    
    # 异常2：阻力为0或负数
    invalid_res = df[df['resistance'] <= 0]
    if len(invalid_res) > 0:
        anomalies.append(f"阻力≤0: {len(invalid_res)} 条")
    
    # 异常3：高度为0
    invalid_h = df[(df['height_min'] == 0) | (df['height_max'] == 0)]
    if len(invalid_h) > 0:
        anomalies.append(f"高度为0: {len(invalid_h)} 条")
    
    # 异常4：型号解析失败
    import re
    bad_model = []
    for _, row in df.iterrows():
        m = re.search(r'[A-Z]+?(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)', str(row['model']))
        if not m:
            bad_model.append(row['model'])
    
    if bad_model:
        anomalies.append(f"型号解析失败: {len(bad_model)} 条")
    
    print(f"\n逻辑异常: {len(anomalies)} {'✅' if len(anomalies) == 0 else '❌'} (期望 0)")
    for a in anomalies:
        print(f"  ❌ {a}")
    
    # 总验收
    ok = (total >= 100 and len(thin) >= 10 and len(large) >= 15 and len(anomalies) == 0)
    print(f"\n{'🎉 谱系完整检查通过' if ok else '⚠️ 存在异常，需处理'}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
