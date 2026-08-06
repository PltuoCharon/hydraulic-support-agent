from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from app.db import get_db
from app.models.schemas import RecommendReq

router = APIRouter()

@router.get("/")
def list_supports(
    type: Optional[str] = Query(None, pattern="^(掩护式|支撑掩护式|支撑式|放顶煤)$",
                                description="基本架型，自动包含括号变体"),
    min_force: int = Query(0, ge=0, description="最小工作阻力/kN"),
    max_force: int = Query(99999, description="最大工作阻力/kN"),
    only_verified: bool = Query(True, description="排除存疑数据"),
    db=Depends(get_db),
):
    """支架列表：架型(前缀匹配含变体)+阻力范围筛选，默认排除suspect"""
    sql = "SELECT * FROM support_models WHERE 1=1"
    params = []
    if only_verified:
        sql += " AND data_status='verified'"
    if type:
        sql += " AND type LIKE %s"
        params.append(f"{type}%")   # '掩护式%' 命中 掩护式/掩护式(急倾斜)/掩护式(轻型) 等
    sql += " AND working_resistance BETWEEN %s AND %s"
    params += [min_force, max_force]
    sql += " ORDER BY working_resistance"
    with db.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return {"total": len(rows), "items": rows}

@router.get("/{model_id}")
def get_support(model_id: int, db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM support_models WHERE id=%s", (model_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"支架 id={model_id} 不存在")
    return row

@router.post("/recommend")
def recommend(req: RecommendReq):
    return {"input": req, "candidates": [], "note": "D4 接入真实筛选"}

from app.services.filter import filter_supports
from pydantic import BaseModel, Field

class FilterReq(BaseModel):
    area_id: int | None = Field(None, description="矿区id，工况从库里取")
    coal_thickness: float | None = Field(None, gt=0.5, lt=12)
    dip_angle: float | None = Field(None, ge=0, le=45)

@router.post("/filter")
def filter_endpoint(req: FilterReq, db=Depends(get_db)):
    with db.cursor() as cur:
        if req.area_id:
            cur.execute("SELECT * FROM mining_areas WHERE id=%s AND is_test=0", (req.area_id,))
            area = cur.fetchone()
            if not area:
                raise HTTPException(404, f"矿区 id={req.area_id} 不存在")
        else:
            area = {"coal_thickness": req.coal_thickness, "dip_angle": req.dip_angle or 0}
        cur.execute("SELECT * FROM support_models WHERE data_status='verified'")
        supports = cur.fetchall()
    result = filter_supports(area, supports)
    return {"total_passed": len(result["passed"]),
            "required_intensity": result["required_intensity"],
            "passed": result["passed"],
            "rejected_count": len(result["rejected"])}
