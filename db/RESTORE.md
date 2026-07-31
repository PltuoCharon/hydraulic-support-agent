# 数据库恢复步骤
1. mysql -u hs_user -p -e "CREATE DATABASE IF NOT EXISTS hydraulic_support DEFAULT CHARSET utf8mb4"
2. mysql -u hs_user -p hydraulic_support < db/backup_v1_YYYY-MM-DD.sql
3. 验证：SELECT COUNT(*) FROM support_models; 应为 146
