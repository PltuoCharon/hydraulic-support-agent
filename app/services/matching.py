"""W28-D2: CBR 匹配纯函数核心。
分层约定（接口契约，W28-D7 冻结）:
- 数据层 load_area / load_cases: 唯一允许写 SQL 的地方; 候选池口径在此统一定义
- 纯函数 match_supports(target, cases, top_n): 不碰 DB, 可在 REPL 脱离 FastAPI 直接调用
行为与重构前 matcher.run_match 一致, 唯一有计划的变化:
- 候选案例排除 suspect 型号(W28-D1 对照表#2); 旧行为可用 load_cases(include_suspect=True) 复现
"""
import os
import numpy as np
from app.db import get_conn
from app.services.ahp import ahp_weights, JUDGE_MATRIX
from app.services.normalize import MinMaxScaler, categorical_score
from app.services.match_features import (PRESSURE_MAP, GAS_LEVELS, ROOF_LEVELS,
    PRESSURE_LEVELS, normalize_categorical, roof_class_to_level)
from app.services.filter import effective_height
from app.core.numparse import parse_number

W = np.array(ahp_weights(JUDGE_MATRIX)["weights"])
NUM_FEATS = ["_eff_h", "coal_thickness", "dip_angle", "hardness_f", "depth"]
NUM_W = {"_eff_h": 0.4203, "coal_thickness": 0.2644, "hardness_f": 0.1489,
         "depth": 0.0990, "dip_angle": 0.0674}

def get_num_weights(cases):
    """按 MATCH_WEIGHTS 环境变量返回数值特征权重向量: entropy(默认)/ahp/combo"""
    mode = os.getenv("MATCH_WEIGHTS", "entropy")
    w_ahp = np.array([NUM_W[f] for f in NUM_FEATS])
    if mode == "ahp":
        w = w_ahp
    else:
        from app.services.entropy_weight import entropy_weights
        ew = entropy_weights(cases, NUM_FEATS)
        w_ent = np.array([ew[f] for f in NUM_FEATS])
        w = w_ent if mode == "entropy" else 0.5 * w_ahp + 0.5 * w_ent
    return w / w.sum()

CASE_SQL = """
SELECT wc.id AS case_id, wc.working_face_name, wc.support_model_id,
       wc.coal_thickness, wc.dip_angle, wc.roof_condition, wc.gas_level, wc.mining_height,
       wc.roof_class AS case_roof_class, wc.gas_level_norm AS case_gas_norm,
       a.hardness_f, a.depth, a.mine_pressure, a.area_name, a.roof_class, a.gas_level_norm,
       s.model AS support_model, s.type, s.working_resistance, s.intensity, s.weight,
       s.height_min, s.height_max, s.center_dist, s.initial_force
FROM working_conditions wc
LEFT JOIN mining_areas a ON wc.area_id = a.id
LEFT JOIN support_models s ON wc.support_model_id = s.id
WHERE wc.support_model_id IS NOT NULL
  AND (a.is_test = 0 OR a.is_test IS NULL)  -- W27-D1: 盲测案例不入候选池,防开卷
"""

def load_area(area_id: int) -> dict:
    """取目标矿区; 不存在抛 LookupError"""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM mining_areas WHERE id=%s", (area_id,))
        row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        raise LookupError(f"矿区 id={area_id} 不存在")
    return row

def load_cases(exclude_area_id: int | None = None,
               include_suspect: bool = False) -> list[dict]:
    """候选案例池。exclude_area_id=LOO 排除目标矿区自身案例;
    include_suspect=False(默认): suspect 型号案例退出候选池(W28-D1 #2 口径统一)"""
    sql, args = CASE_SQL, []
    if not include_suspect:
        sql += " AND (s.data_status IS NULL OR s.data_status <> 'suspect')"
    if exclude_area_id:
        sql += " AND wc.area_id != %s"
        args.append(exclude_area_id)
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, args)
        return cur.fetchall()
    finally:
        conn.close()

def build_diffs(target, c, cat_scores):
    diffs = []
    th = parse_number(target.get("_eff_h"))
    ch = parse_number(c.get("_eff_h"))
    if th and ch:
        d = round(ch - th, 2)
        diffs.append(f"案例采高{ch}m({'+' if d >= 0 else ''}{d}m)")
    if c.get("support_model"):
        wr = c.get("working_resistance") or "?"
        diffs.append(f"案例用架{c['support_model']}(阻力{wr}kN)")
    weak = [k for k, v in zip(["顶板", "矿压", "瓦斯"], cat_scores) if v == 0]
    if weak:
        diffs.append(f"注意: {'/'.join(weak)}条件不匹配")
    return diffs

def match_supports(target: dict, cases: list[dict], top_n: int = 5) -> dict:
    """纯函数: 输入目标工况 dict + 候选案例 list, 返回 {"total": int, "items": [...]}。
    不访问 DB; 不修改调用方传入的对象(内部拷贝)。"""
    target = dict(target)
    cases = [dict(c) for c in cases]
    target["_eff_h"] = effective_height(target)
    for c in cases:
        c["_eff_h"] = effective_height(c)

    if not cases:
        return {"total": 0, "items": []}

    scalers = {f: MinMaxScaler([c.get(f) for c in cases]) for f in NUM_FEATS}
    t_vec = np.array([v if v is not None else 0.5
                      for v in (scalers[f].transform(target.get(f)) for f in NUM_FEATS)])
    # 注: 重构前权重在循环内逐例计算, 输入恒为同一 cases, 结果相同; 提到循环外消除冗余, 行为不变
    w = get_num_weights(cases)

    results = []
    for c in cases:
        c_vec = np.array([v if v is not None else 0.5
                          for v in (scalers[f].transform(c.get(f)) for f in NUM_FEATS)])
        num_dist = float(np.sqrt((w * (c_vec - t_vec) ** 2).sum()))
        # W29-D1: 顶板/瓦斯改用归一列(标准等级直接评分, NULL→中性0.5, 不猜野生文本);
        # 矿压无归一列, 沿用 PRESSURE_MAP; GAS_MAP/ROOF_MAP 自此退出匹配链路
        cat_scores = [
            categorical_score(roof_class_to_level(c.get("case_roof_class")),
                              roof_class_to_level(target.get("roof_class")), ROOF_LEVELS),
            categorical_score(normalize_categorical(c.get("mine_pressure"), PRESSURE_MAP),
                              normalize_categorical(target.get("mine_pressure"), PRESSURE_MAP), PRESSURE_LEVELS),
            categorical_score(c.get("case_gas_norm"),
                              target.get("gas_level_norm"), GAS_LEVELS),
        ]
        sim = round(0.7 * (1 - min(num_dist, 1)) + 0.3 * float(np.mean(cat_scores)), 4)
        results.append({**c, "similarity": sim,
                        "cat_detail": {"顶板": cat_scores[0], "矿压": cat_scores[1], "瓦斯": cat_scores[2]},
                        "diffs": build_diffs(target, c, cat_scores)})

    results.sort(key=lambda x: x["similarity"], reverse=True)
    seen, top = set(), []
    for r in results:
        if r["support_model_id"] not in seen:
            seen.add(r["support_model_id"])
            top.append(r)
        if len(top) >= top_n:
            break
    for it in top:
        it["source"] = f"案例库: {it['area_name']}·{it['working_face_name']}"
    return {"total": len(results), "items": top}

def match_by_params(coal_thickness: float, dip_angle: float = 0.0,
                    top_n: int = 5) -> dict:
    """REPL 便捷入口: python 里直接 match_by_params(3.5, 8) 即可"""
    target = {"coal_thickness": coal_thickness, "dip_angle": dip_angle or 0,
              "hardness_f": None, "depth": None, "roof_category": None,
              "mine_pressure": None, "gas_level": None}
    return match_supports(target, load_cases(), top_n)
