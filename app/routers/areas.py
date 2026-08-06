from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_areas():
    return {"items": [], "note": "D6 接入真实 MySQL"}
