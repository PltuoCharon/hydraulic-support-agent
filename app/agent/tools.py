"""Agent 工具集。W28-D4: SQL 已全部下沉 services 层, 工具只做参数校验+结果格式化。
铁律：所有工具内部参数化/白名单，禁止执行 LLM 生成的裸 SQL。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import json
from langchain_core.tools import tool
from app.services import queries
from app.services.matching import match_by_params
from app.services.support_calc import recalc
from app.services.knowledge import search

@tool
def query_database(table: str, keyword: str = "", limit: int = 5) -> str:
    """查询液压支架选型数据库。当需要矿区地质条件、支架型号参数、历史工况案例等
    事实数据时调用。
    Args:
        table: 表名，仅限 mining_areas(矿区) / support_models(支架) / working_conditions(工况案例)
        keyword: 模糊关键词（如矿区名"补连塔"、型号片段"ZY21000"），空则按 id 返回前几条
        limit: 返回条数，1~10
    Returns:
        JSON 字符串：匹配的记录列表。
    """
    try:
        rows = queries.search_rows(table, keyword, limit)
    except ValueError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    # Decimal/datetime 转字符串，保证可 JSON 序列化
    for r in rows:
        for k, v in r.items():
            if not isinstance(v, (int, float, str, type(None))):
                r[k] = str(v)
    return json.dumps({"table": table, "count": len(rows), "rows": rows},
                      ensure_ascii=False, default=str)

@tool
def run_matching(coal_thickness: float, dip_angle: float = 0.0, top_n: int = 3) -> str:
    """CBR 案例匹配引擎：输入工作面工况参数，返回最相似的历史案例及其实际用架。
    当用户给出煤层厚度等地质条件、要求推荐支架型号时，必须调用本工具获取
    真实匹配结果，禁止凭记忆推荐型号。
    Args:
        coal_thickness: 煤层厚度（米），必须 >0.5 且 <25
        dip_angle: 煤层倾角（度），0~45，未知填 0
        top_n: 返回案例数，1~5
    Returns:
        文字摘要：Top-N 相似案例的矿区、用架型号、工作阻力、相似度、差异说明。
    """
    if not (0.5 < coal_thickness < 25):
        return f"参数错误：煤层厚度 {coal_thickness} 超出有效范围 (0.5, 25)"
    top_n = max(1, min(int(top_n), 5))
    try:
        data = match_by_params(coal_thickness, dip_angle, top_n)
    except Exception as e:
        return f"匹配引擎错误：{type(e).__name__}: {e}"
    if not data["items"]:
        return "案例库为空，无匹配结果"
    lines = [f"案例库共 {data['total']} 个可比案例，Top-{len(data['items'])} 相似案例："]
    for i, it in enumerate(data["items"], 1):
        lines.append(
            f"{i}. {it.get('area_name')}（采高{it.get('_eff_h')}m）"
            f"→ 实际用架 {it.get('support_model')}，"
            f"工作阻力 {it.get('working_resistance')}kN，"
            f"相似度 {it.get('similarity')}；"
            f"差异：{'；'.join(it.get('diffs', []))}")
    return "\n".join(lines)

@tool
def recalc_params(bore_mm: float, pressure_mpa: float = 31.5, n_cylinders: int = 2,
                  center_dist: float = 1.75, canopy_len: float = 4.0) -> str:
    """支架部件参数修改重算：给定立柱缸径(mm)、泵站压力(MPa)、立柱数、中心距(m)、
    支护长度参数(m)，按历史公式链重算单柱推力、工作阻力、支护强度。
    用于"缸径320换成360会怎样""泵站压力提高后阻力多大"类问题。
    结果为历史公式链估算值，非厂家实测；canopy_len工程定义及eta物理口径仍在W34审计中。
    """
    try:
        r = recalc(bore_mm, pressure_mpa, n_cylinders, center_dist, canopy_len)
    except ValueError as e:
        return f"参数错误：{e}"
    return (f"重算结果（{r['note']}，η={r['eta']}）：\n"
            f"单柱推力 {r['single_thrust_kn']}kN；"
            f"整架工作阻力 {r['resistance_kn']}kN；"
            f"支护强度 {r['intensity_mpa']}MPa")

@tool
def search_knowledge(query: str, top_k: int = 3) -> str:
    """检索液压支架设计手册/标准知识库（当前含 MT/T 556-1996 设计规范）。
    当用户问设计规则、参数确定方法、规范要求等"书上怎么说"类问题时调用。
    返回相关内容块及其来源(文件+页码)，回答时必须注明来源。
    """
    top_k = max(1, min(int(top_k), 5))
    hits = search(query, top_k)
    if not hits:
        return "知识库中未找到相关内容（当前语料：MT/T 556-1996 液压支架设计规范）"
    lines = []
    for i, h in enumerate(hits, 1):
        lines.append(f"【{i}】来源:{h['source']} {h['loc']} (相关度{h['score']})\n"
                     f"{h['content'].strip()}")
    return "\n\n".join(lines)

TOOLS = [query_database, run_matching, recalc_params, search_knowledge]

if __name__ == "__main__":
    print(query_database.invoke({"table": "support_models", "keyword": "ZY21000"}))
    print(query_database.invoke({"table": "mining_areas", "keyword": "补连塔", "limit": 2}))
    print(query_database.invoke({"table": "users"}))   # 白名单拒绝测试
    print("--- 工具2测试 ---")
    print(run_matching.invoke({"coal_thickness": 8.8, "dip_angle": 2}))
    print(run_matching.invoke({"coal_thickness": 99}))   # 越界测试
    print("--- 工具3测试 ---")
    print(recalc_params.invoke({"bore_mm": 320}))
    print(recalc_params.invoke({"bore_mm": 999}))   # 越界测试
    print("--- 工具4测试 ---")
    print(search_knowledge.invoke({"query": "支护强度确定"})[:300])
