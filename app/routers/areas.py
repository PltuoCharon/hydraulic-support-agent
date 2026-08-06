from fastapi import APIRouter, Depends
from app.db import get_db

router = APIRouter()

@router.get("/")
def list_areas():
    return {"items": [], "note": "D6 接入真实 MySQL"}

@router.get("/dbcheck")
def db_check(db=Depends(get_db)):
    """依赖注入演练：查数据库当前时间，证明连接通路"""
    with db.cursor() as cur:
        cur.execute("SELECT NOW() AS now, DATABASE() AS db_name")
        return cur.fetchone()
