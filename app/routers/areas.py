"""矿区路由(W28-D3 瘦身): 业务SQL下沉 services/queries.py。
顺带修复: db_check 原 return ok(cur.fetchone) 漏写括号, 返回方法对象的bug"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from app.db import get_db
from app.core.response import ok
from app.services import queries

router = APIRouter()

@router.get("/")
def list_areas(keyword: Optional[str] = Query(None, description="按矿区名称模糊搜索")):
    """矿区列表：默认排除测试数据(is_test=1)，支持 ?keyword= 模糊查询"""
    rows = queries.list_areas(keyword=keyword)
    return ok({"total": len(rows), "items": rows})

@router.get("/dbcheck")
def db_check(db=Depends(get_db)):
    """健康检查: 不查业务表, SQL 保留在 router 属约定例外"""
    with db.cursor() as cur:
        cur.execute("SELECT NOW() AS now, DATABASE() AS db_name")
        return ok(cur.fetchone())

@router.get("/{area_id}")
def get_area(area_id: int):
    """矿区详情：不存在返回404而非空数据"""
    row = queries.get_area(area_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"矿区 id={area_id} 不存在")
    return ok(row)
