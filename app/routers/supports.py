from fastapi import APIRouter
from typing import Optional
from app.models.schemas import RecommendReq

router = APIRouter()

@router.get("/{model_id}")
def get_support(model_id: int):
    return {"model_id": model_id, "model": "ZY12000/28/62D", "intensity": 1.31}

@router.get("/")
def list_supports(type: Optional[str] = None, min_force: int = 0):
    return {"type": type, "min_force": min_force, "items": []}

@router.post("/recommend")
def recommend(req: RecommendReq):
    return {"input": req, "candidates": []}
