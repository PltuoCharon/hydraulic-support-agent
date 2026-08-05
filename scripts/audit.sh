#!/bin/bash
# hs_agent 项目体检脚本：逐项检查 12 项整改与项目健康度
cd ~/hs_agent || exit 1
PASS=0; FAIL=0
ck() {  # ck "描述" "命令" 
  if eval "$2" > /dev/null 2>&1; then
    echo "  [PASS] $1"; PASS=$((PASS+1))
  else
    echo "  [FAIL] $1"; FAIL=$((FAIL+1))
  fi
}

echo "===== 1. 环境与依赖 ====="
ck "venv 存在"                "test -d venv"
ck "requirements.txt 非空"    "test -s requirements.txt"
python -c "import fastapi" 2>/dev/null && echo "  [INFO] fastapi 已装" || echo "  [INFO] fastapi 未装(W13要装)"

echo "===== 2. 备份(问题6) ====="
ck "git 仓库已初始化"          "git rev-parse --git-dir"
ck "已配置 GitHub 远程"        "git remote get-url origin | grep -q github"
ck "本地无未提交改动"          "test -z \"\$(git status --porcelain)\""
ck "backups/ 有7天内的dump"    "find backups -name '*.sql' -mtime -7 | grep -q ."
ck "crontab 已配自动备份"      "crontab -l | grep -q mysqldump"

echo "===== 3. 密钥安全(问题7) ====="
ck ".env 存在"                "test -f .env"
ck ".env 已被 gitignore"      "grep -qx '.env' .gitignore"
ck "代码无硬编码Key"          "! grep -rn 'api_key=.[a-z0-9A-Z]\{20,\}' --include='*.py' . | grep -v venv | grep -q ."
ck "git历史无Key泄露"         "! git log -p --all 2>/dev/null | grep -q '\.env'"

echo "===== 4. 数据库健康(问题4/5/8/10) ====="
Q="mysql -u hs_user -p'zyb123' hydraulic_support -N -e"
ck "数据库可连接"              "$Q 'SELECT 1' | grep -q 1"
echo "  [INFO] 强度缺失: $($Q 'SELECT SUM(intensity IS NULL) FROM support_models')"
echo "  [INFO] 重量缺失: $($Q 'SELECT SUM(weight IS NULL) FROM support_models')"
echo "  [INFO] suspect数: $($Q \"SELECT COUNT(*) FROM support_models WHERE data_status='suspect'\")"
ck "param_dependencies 表存在(问题8)" "$Q 'SHOW TABLES' | grep -q param_dependencies"
ck "dict_enum 表存在(问题10)"        "$Q 'SHOW TABLES' | grep -q dict_enum"

echo "===== 5. 语料与文档(问题11/12) ====="
ck "corpus/ 有PDF语料"         "find corpus -name '*.pdf' 2>/dev/null | grep -q ."
ck "docs/ 无占位符"           "! grep -rn '（日期）\|待补充\|TODO' docs/ 2>/dev/null | grep -q ."

echo ""
echo "===== 体检结果: PASS=$PASS  FAIL=$FAIL ====="
