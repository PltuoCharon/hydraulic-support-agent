from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.db import get_db
from app.core.response import ok

router = APIRouter()

@router.get("/")
def list_areas(
    keyword: Optional[str] = Query(None, description="按矿区名称模糊搜索"),
    db=Depends(get_db),
):
    """矿区列表：默认排除测试数据(is_test=1)，支持 ?keyword= 模糊查询"""
    sql = "SELECT * FROM mining_areas WHERE is_test = 0"
    params = []
    if keyword:
        sql += " AND area_name LIKE %s"
        params.append(f"%{keyword}%")
    sql += " ORDER BY id"
    with db.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return ok({"total": len(rows), "items": rows})

@router.get("/dbcheck")
def db_check(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT NOW() AS now, DATABASE() AS db_name")
        return ok(cur.fetchone)

@router.get("/{area_id}")
def get_area(area_id: int, db=Depends(get_db)):
    """矿区详情：不存在返回404而非空数据"""
    from fastapi import HTTPException
    with db.cursor() as cur:
        cur.execute("SELECT * FROM mining_areas WHERE id=%s AND is_test=0", (area_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"矿区 id={area_id} 不存在")
    return ok(row)
