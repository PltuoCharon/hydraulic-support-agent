from typing import Optional
from pydantic import BaseModel

# ---------- 1. 路径参数：参数嵌在 URL 路径里 ----------
@app.get("/supports/{model_id}")
def get_support(model_id: int):
    return {"model_id": model_id, "model": "ZY12000/28/62D", "intensity": 1.31}

# ---------- 2. 查询参数：URL 里 ?key=value 的形式 ----------
@app.get("/supports")
def list_supports(type: Optional[str] = None, min_force: int = 0):
    return {"type": type, "min_force": min_force, "items": []}

# ---------- 3. 请求体：POST 提交的 JSON ----------
class RecommendReq(BaseModel):
    seam_thickness: float        # 采高/m，必填
    gas_level: str               # 瓦斯等级，必填
    dip_angle: float = 0         # 倾角/°，有默认值=选填

@app.post("/recommend")
def recommend(req: RecommendReq):
    return {"input": req, "candidates": []}
