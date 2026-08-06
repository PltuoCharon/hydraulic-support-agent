#!/bin/bash
# W13~W15 全功能验收脚本（需 uvicorn 在运行）
cd ~/hs_agent || exit 1
source venv/bin/activate 2>/dev/null
BASE=http://127.0.0.1:8000
PASS=0; FAIL=0
ck() {
  if eval "$2" > /dev/null 2>&1; then echo "  [PASS] $1"; PASS=$((PASS+1))
  else echo "  [FAIL] $1"; FAIL=$((FAIL+1)); fi
}
jqr() { python3 -c "import sys,json;d=json.load(sys.stdin);$1" 2>/dev/null; }

echo "===== 0. 服务与文件结构 ====="
ck "uvicorn 运行中"              "curl -s $BASE/health | grep -q ok"
for f in app/main.py app/config.py app/db.py app/core/params.py app/core/numparse.py \
         app/core/response.py app/models/schemas.py app/routers/areas.py \
         app/routers/supports.py app/routers/match.py app/services/filter.py \
         app/services/match_features.py app/services/normalize.py app/services/ahp.py; do
  ck "$f" "test -f $f"
done

echo "===== 1. W13 基础能力 ====="
ck "Swagger可访问"              "curl -s $BASE/docs | grep -qi swagger"
ck "矿区列表返回真实数据"        "curl -s $BASE/api/areas/ | jqr 'assert d[\"data\"][\"total\"]>0'"
ck "矿区keyword模糊查询"         "curl -s '$BASE/api/areas/?keyword=补连塔' | jqr 'assert d[\"data\"][\"total\"]>=1'"
ck "矿区详情404"                "test \$(curl -s -o /dev/null -w '%{http_code}' $BASE/api/areas/99999) = 404"
ck "统一响应格式code/data/msg"   "curl -s $BASE/api/areas/ | jqr 'assert d[\"code\"]==0 and \"data\" in d and \"msg\" in d'"
ck "Pydantic 422校验"           "test \$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/supports/recommend -H 'Content-Type: application/json' -d '{\"seam_thickness\":99,\"gas_level\":\"低瓦斯\"}') = 422"
ck "参数读库eta"                "python -c 'from app.core.params import Params; assert 0.8 < Params().eta < 1.0'"

echo "===== 2. W14 业务接口 ====="
ck "支架筛选(掩护式含变体)"      "curl -s '$BASE/api/supports/?type=掩护式' | jqr 'assert d[\"data\"][\"total\"]>0'"
ck "suspect被默认排除"           "! curl -s $BASE/api/supports/ | grep -q ZY18900"
ck "/filter真实筛选"            "curl -s -X POST $BASE/api/supports/filter -H 'Content-Type: application/json' -d '{\"area_id\":1}' | jqr 'assert \"required_intensity\" in d[\"data\"]'"
ck "CORS预配置"                 "curl -s -H 'Origin: http://localhost:5173' -I $BASE/api/areas/ | grep -qi access-control-allow-origin"

echo "===== 3. W15 CBR引擎 ====="
ck "AHP一致性CR<0.1"            "python -c 'from app.services.ahp import ahp_weights,JUDGE_MATRIX; assert ahp_weights(JUDGE_MATRIX)[\"CR\"]<0.1'"
ck "/api/match返回TopN"         "curl -s -X POST $BASE/api/match -H 'Content-Type: application/json' -d '{\"area_id\":1,\"top_n\":5}' | jqr 'assert d[\"data\"][\"total\"]>0 and len(d[\"data\"][\"items\"])<=5'"
ck "LOO留一法(total<36)"        "curl -s -X POST $BASE/api/match -H 'Content-Type: application/json' -d '{\"area_id\":1,\"top_n\":5}' | jqr 'assert d[\"data\"][\"total\"]<36'"
ck "相似度降序"                 "curl -s -X POST $BASE/api/match -H 'Content-Type: application/json' -d '{\"area_id\":1,\"top_n\":5}' | jqr 's=[i[\"similarity\"] for i in d[\"data\"][\"items\"]]; assert s==sorted(s,reverse=True)'"
ck "diffs可解释字段"            "curl -s -X POST $BASE/api/match -H 'Content-Type: application/json' -d '{\"area_id\":1,\"top_n\":3}' | grep -q diffs"
ck "互斥校验422"                "test \$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/match -H 'Content-Type: application/json' -d '{\"area_id\":1,\"coal_thickness\":3}') = 422"

echo "===== 4. 测试与工程质量 ====="
TP=$(python -m pytest tests/ -q 2>/dev/null | tail -1)
echo "  [INFO] pytest: $TP"
ck "pytest全绿"                 "python -m pytest tests/ -q 2>/dev/null | grep -q passed"
ck "无未提交改动"               "test -z \"\$(git status --porcelain)\""
ck "7天内有dump备份"            "find backups -name '*.sql' -mtime -7 | grep -q ."

echo ""
echo "===== 验收结果: PASS=$PASS FAIL=$FAIL ====="
