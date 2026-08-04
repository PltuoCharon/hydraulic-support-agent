#!/bin/bash
cd ~/hs_agent
source venv/bin/activate

echo "========================================"
echo "M3 里程碑最终验收"
echo "========================================"

echo ""
echo "--- 1. 来源完整率 ---"
python -c "
import pandas as pd
for f, col in [('data/raw/支架型号.xlsx','source'), ('data/raw/矿区工况.xlsx','source')]:
    df = pd.read_excel(f)
    n = df[col].isna().sum()
    print(f, '缺来源', n, '行', '✅' if n==0 else '❌')
"

echo ""
echo "--- 2. 谱系完整 ---"
python scripts/check_supports.py

echo ""
echo "--- 3. 台账七类覆盖 ---"
python scripts/check_ledger.py

echo ""
echo "--- 4. 盲测集核对 ---"
echo "数据库盲测集:"
mysql -u hs_user -pzyb123 hydraulic_support -e "SELECT id, name, category FROM mining_areas WHERE is_test=1;"
echo ""
echo "文档记录:"
grep -A 10 "盲测集" docs/数据库设计.md | head -15

echo ""
echo "========================================"
echo "验收完成"
echo "========================================"
