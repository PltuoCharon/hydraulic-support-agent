"""CBR：目标工况 → 案例相似度(留一法) → 相似案例实际用架 → Top-N（含diffs）"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import numpy as np
from app.db import get_db
from app.services.ahp import ahp_weights, JUDGE_MATRIX
from app.services.normalize import MinMaxScaler, categorical_score
from app.services.match_features import (ROOF_MAP, PRESSURE_MAP, GAS_MAP,
    GAS_LEVELS, ROOF_LEVELS, PRESSURE_LEVELS, normalize_categorical)
from app.core.numparse import parse_number
from app.core.response import ok

router = APIRouter()
W = np.array(ahp_weights(JUDGE_MATRIX)["weights"])
NUM_FEATS = ["_eff_h", "coal_thickness", "dip_angle", "hardness_f", "depth"]
# 数值特征权重（源自AHP向量重排：采高0.4203, 阻力0.2644->煤层厚度代理, 顶板0.1489->硬度, 矿压0.099->埋深, 倾角0.0674）
NUM_W = {"_eff_h": 0.4203, "coal_thickness": 0.2644, "hardness_f": 0.1489,
         "depth": 0.0990, "dip_angle": 0.0674}

def get_num_weights(cases):
    """按 MATCH_WEIGHTS 环境变量返回数值特征权重向量: ahp(默认)/entropy/combo"""
    import os
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
       a.hardness_f, a.depth, a.mine_pressure, a.area_name,
       s.model AS support_model, s.type, s.working_resistance, s.intensity, s.weight
FROM working_conditions wc
LEFT JOIN mining_areas a ON wc.area_id = a.id
LEFT JOIN support_models s ON wc.support_model_id = s.id
WHERE wc.support_model_id IS NOT NULL
"""

class MatchReq(BaseModel):
    area_id: int | None = None
    coal_thickness: float | None = Field(None, gt=0.5, lt=12)
    dip_angle: float | None = Field(None, ge=0, le=45)
    top_n: int = Field(5, ge=1, le=20)

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

@router.post("/")
def match(req: MatchReq, db=Depends(get_db)):
    if req.area_id and req.coal_thickness:
        raise HTTPException(422, "area_id 与手动工况只能二选一")
    with db.cursor() as cur:
        if req.area_id:
            cur.execute("SELECT * FROM mining_areas WHERE id=%s", (req.area_id,))
            target = cur.fetchone()
            if not target:
                raise HTTPException(404, f"矿区 id={req.area_id} 不存在")
        else:
            target = {"coal_thickness": req.coal_thickness, "dip_angle": req.dip_angle or 0,
                      "hardness_f": None, "depth": None, "roof_category": None,
                      "mine_pressure": None, "gas_level": None}
        # 留一法(LOO)：目标矿区自身的案例不参与匹配，防止"自己匹配自己"
        if req.area_id:
            cur.execute(CASE_SQL + " AND wc.area_id != %s", (req.area_id,))
        else:
            cur.execute(CASE_SQL)
        cases = cur.fetchall()
    from app.services.filter import effective_height
    target["_eff_h"] = effective_height(target)
    for c in cases:
        c["_eff_h"] = effective_height(c)

    if not cases:
        return ok({"total": 0, "items": []}, msg="案例库为空")

    scalers = {f: MinMaxScaler([c.get(f) for c in cases]) for f in NUM_FEATS}
    t_vec = np.array([v if v is not None else 0.5
                      for v in (scalers[f].transform(target.get(f)) for f in NUM_FEATS)])

    results = []
    for c in cases:
        c_vec = np.array([v if v is not None else 0.5
                          for v in (scalers[f].transform(c.get(f)) for f in NUM_FEATS)])
        w = get_num_weights(cases)
        num_dist = float(np.sqrt((w * (c_vec - t_vec) ** 2).sum()))
        cat_scores = [
            categorical_score(normalize_categorical(c.get("roof_condition"), ROOF_MAP),
                              normalize_categorical(target.get("roof_category"), ROOF_MAP), ROOF_LEVELS),
            categorical_score(normalize_categorical(c.get("mine_pressure"), PRESSURE_MAP),
                              normalize_categorical(target.get("mine_pressure"), PRESSURE_MAP), PRESSURE_LEVELS),
            categorical_score(normalize_categorical(c.get("gas_level"), GAS_MAP),
                              normalize_categorical(target.get("gas_level"), GAS_MAP), GAS_LEVELS),
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
        if len(top) >= req.top_n:
            break
    return ok({"total": len(results), "items": top})
