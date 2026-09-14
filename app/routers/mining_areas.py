"""地图选区路由(W29-D4)。薄壳: SQL 在 services/queries.py。
坐标口径: 地级市近似位置(页脚与响应字段双重声明)。"""
from fastapi import APIRouter, HTTPException
from app.core.response import ok
from app.services import queries

router = APIRouter()

@router.get("/")
def list_map_areas():
    rows = queries.map_areas()
    return ok({"total": len(rows), "coord_note": "坐标为地级市近似位置", "items": rows})

@router.get("/{area_id}/supports")
def get_area_supports(area_id: int):
    area = queries.get_area(area_id)
    if not area:
        raise HTTPException(404, f"矿区 id={area_id} 不存在")
    rows = queries.area_supports(area_id)
    return ok({"area": area["area_name"], "total": len(rows), "items": rows})
