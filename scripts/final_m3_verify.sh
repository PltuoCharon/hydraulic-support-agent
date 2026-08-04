#!/bin/bash
cd ~/hs_agent
source venv/bin/activate

echo "========================================"
echo "M3 里程碑最终验收 - 恢复演练 + 语料检查"
echo "========================================"

# 1. 恢复演练
echo ""
echo "--- 1. 备份恢复演练 ---"
mysql -u hs_user -pzyb123 -e "CREATE DATABASE IF NOT EXISTS hs_restore_test DEFAULT CHARSET utf8mb4"
mysql -u hs_user -pzyb123 hs_restore_test < db/backup_v1_2026-07-31.sql

count=$(mysql -u hs_user -pzyb123 hs_restore_test -e "SELECT COUNT(*) FROM support_models;" | tail -1)
echo "support_models 恢复数量: $count"
if [ "$count" -ge 100 ]; then
    echo "✅ 恢复成功"
else
    echo "❌ 恢复失败，数量不足"
fi

mysql -u hs_user -pzyb123 -e "DROP DATABASE hs_restore_test;"

# 2. 语料检查
echo ""
echo "--- 2. PDF 语料检查 ---"
pdf_count=$(find data/corpus -name "*.pdf" | wc -l)
echo "PDF 数量: $pdf_count"
if [ "$pdf_count" -ge 3 ]; then
    echo "✅ PDF 数量达标"
else
    echo "⚠️ PDF 不足 3 个，使用 txt 替代"
    txt_count=$(find data/corpus -name "*.txt" | wc -l)
    echo "TXT 数量: $txt_count"
fi

# 3. 切分测试
echo ""
echo "--- 3. 文本切分测试 ---"
python scripts/chunk_demo.py

echo ""
echo "========================================"
echo "验收完成"
echo "========================================"
