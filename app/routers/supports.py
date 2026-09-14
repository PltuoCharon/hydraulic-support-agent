"""支架路由(W28-D3 瘦身): SQL 已全部下沉 app/services/queries.py。
变更: 删除僵尸占位 POST /recommend(原"D4 接入真实筛选"从未实现)。"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from app.core.response import ok
from app.services import queries
from app.services.filter import filter_supports

router = APIRouter()

@router.get("/")
def list_supports(
    type: Optional[str] = Query(None, pattern="^(掩护式|支撑掩护式|支撑式|放顶煤)$",
                                description="基本架型，自动包含括号变体"),
    min_force: int = Query(0, ge=0, description="最小工作阻力/kN"),
    max_force: int = Query(99999, description="最大工作阻力/kN"),
    only_verified: bool = Query(True, description="排除存疑数据"),
):
    rows = queries.list_supports(type, min_force, max_force, only_verified)
    return ok({"total": len(rows), "items": rows})

@router.get("/spectrum")
def spectrum():
    """W30-D1 架型谱系(必须注册在 /{model_id} 之前, 否则被动态段吞成 422)"""
    items = queries.spectrum()
    return ok({"total": len(items),
               "axis_note": "阻力/采高均来自公开型谱值; 控顶距/支护强度等字段估算情况见 est_fields",
               "items": items})


@router.get("/vendors")
def vendors():
    """W30-D2 厂商分布(必须注册在 /{model_id} 之前)"""
    return ok(queries.vendor_dist())


@router.get("/{model_id}")
def get_support(model_id: int):
    row = queries.get_support(model_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"支架 id={model_id} 不存在")
    return ok(row)

class FilterReq(BaseModel):
    area_id: int | None = Field(None, description="矿区id，工况从库里取")
    coal_thickness: float | None = Field(None, gt=0.5, lt=12)
    dip_angle: float | None = Field(None, ge=0, le=45)

@router.post("/filter")
def filter_endpoint(req: FilterReq):
    if req.area_id:
        area = queries.get_area(req.area_id)
        if not area:
            raise HTTPException(404, f"矿区 id={req.area_id} 不存在")
    else:
        area = {"coal_thickness": req.coal_thickness, "dip_angle": req.dip_angle or 0}
    result = filter_supports(area, queries.verified_supports())
    return ok({"total_passed": len(result["passed"]),
               "required_intensity": result["required_intensity"],
               "passed": result["passed"],
               "rejected_count": len(result["rejected"])})
