#!/bin/bash
cd ~/hs_agent

BACKUP=$(ls -t db/backup_v1_*.sql | head -1)
echo "使用备份: $BACKUP"

sudo mysql -u root -e "CREATE DATABASE IF NOT EXISTS hs_restore_test DEFAULT CHARSET utf8mb4;"
sudo mysql -u root hs_restore_test < "$BACKUP"

echo "验证数据..."
sudo mysql -u root hs_restore_test -e "
SELECT 'support_models' AS t, COUNT(*) AS c FROM support_models
UNION ALL SELECT 'mining_areas', COUNT(*) FROM mining_areas
UNION ALL SELECT 'param_dependencies', COUNT(*) FROM param_dependencies
UNION ALL SELECT 'support_parts', COUNT(*) FROM support_parts
UNION ALL SELECT 'working_conditions', COUNT(*) FROM working_conditions;"

echo "验证盲测集..."
sudo mysql -u root hs_restore_test -e "SELECT id, name, is_test FROM mining_areas WHERE is_test = 1;"

sudo mysql -u root -e "DROP DATABASE hs_restore_test;"
echo "=== 完成 ==="
