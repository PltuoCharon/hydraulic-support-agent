"""设计计算路由 —— W33-D2
契约: docs/接口契约_W28.md 附录C。SQL 零, 纯计算内核调用。"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.calc.q_need import estimate

router = APIRouter()


class QNeedReq(BaseModel):
    hm: float = Field(..., description="采高 m")
    l1: float = Field(..., description="老顶初次来压步距 m")
    lp: float = Field(..., description="周期来压步距 m")
    bc: float = Field(..., description="控顶高度 m")
    n: float = Field(..., description="直接顶厚度与采高之比")
    gamma: float = Field(25.0, description="顶板岩层容重 kN/m³")
    k1: float = Field(6.0, description="影响系数(6~8倍采高岩柱)")
    k: float = Field(2.0, description="动载荷系数")


@router.post("/q-need")
def q_need(req: QNeedReq):
    try:
        data = estimate(req.hm, req.l1, req.lp, req.bc, req.n,
                        req.gamma, req.k1, req.k)
        return {"code": 0, "data": data}
    except ValueError as e:
        return {"code": 1, "msg": str(e)}
