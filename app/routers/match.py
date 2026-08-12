"""CBR 匹配路由（W17-D7 瘦身为委托）。核心逻辑在 app/services/matcher.py。"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.response import ok
from app.db import get_db
from app.services.matcher import run_match

router = APIRouter()

class MatchReq(BaseModel):
    area_id: int | None = None
    coal_thickness: float | None = Field(None, gt=0.5, lt=25)
    dip_angle: float | None = Field(None, ge=0, le=45)
    top_n: int = Field(5, ge=1, le=20)

@router.post("/")
def match(req: MatchReq, db=Depends(get_db)):
    try:
        data = run_match(req.area_id, req.coal_thickness, req.dip_angle, req.top_n)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except LookupError as e:
        raise HTTPException(404, str(e))
    if data["total"] == 0:
        return ok(data, msg="案例库为空")
    return ok(data)
