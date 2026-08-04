"""矿区台账七类地质条件覆盖检查"""

import pandas as pd
import sys

def main():
    df = pd.read_excel("data/raw/矿区工况.xlsx")
    
    print("=== 矿区台账七类覆盖检查 ===")
    
    # 定义七类地质条件
    categories = {
        '浅埋深': ['浅埋', '浅埋深'],
        '大采高': ['大采高', '超大采高'],
        '放顶煤': ['放顶煤', '综放'],
        '坚硬顶板': ['坚硬顶板', '坚硬'],
        '高瓦斯': ['高瓦斯', '瓦斯'],
        '冲击地压': ['冲击', '冲击地压'],
        '复杂地质': ['复杂', '软岩', '断层', '陷落柱']
    }
    
    found = {k: False for k in categories}
    coverage = {k: [] for k in categories}
    
    for _, row in df.iterrows():
        cat = str(row.get('category', ''))
        for type_name, keywords in categories.items():
            if any(kw in cat for kw in keywords):
                found[type_name] = True
                coverage[type_name].append(row.get('name', 'Unknown'))
    
    print("\n七类覆盖情况:")
    all_ok = True
    for type_name in categories:
        ok = found[type_name]
        status = "✅" if ok else "❌"
        print(f"  {status} {type_name}: {len(coverage[type_name])} 条")
        if coverage[type_name]:
            print(f"      示例: {', '.join(coverage[type_name][:3])}")
        if not ok:
            all_ok = False
    
    # 额外检查
    print(f"\n总矿区数: {len(df)}")
    print(f"有分类的矿区: {df['category'].notna().sum()}")
    print(f"无分类的矿区: {df['category'].isna().sum()}")
    
    print(f"\n{'🎉 七类覆盖检查通过' if all_ok else '⚠️ 存在未覆盖类型'}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
