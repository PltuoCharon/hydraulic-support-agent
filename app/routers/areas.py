from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.db import get_db

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
    return {"total": len(rows), "items": rows}

@router.get("/dbcheck")
def db_check(db=Depends(get_db)):
    with db.cursor() as cur:
        cur.execute("SELECT NOW() AS now, DATABASE() AS db_name")
        return cur.fetchone()
