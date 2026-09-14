from app.config import settings
from fastapi import FastAPI
from app.routers import areas, supports, match, chat, guide, mining_areas

app = FastAPI(
    title="液压支架智能选型 API",
    description="毕设项目后端：支架库查询 / 选型推荐 / RAG 问答",
    version="0.1.0",
)

app.include_router(areas.router,    prefix="/api/areas",    tags=["矿区"])
app.include_router(mining_areas.router, prefix="/api/mining-areas", tags=["地图选区"])
app.include_router(supports.router, prefix="/api/supports", tags=["支架"])

@app.get("/")
def root():
    return {"msg": "液压支架智能体 API 运行中", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.response import fail

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return JSONResponse(status_code=404, content=fail("资源不存在", code=404))

@app.exception_handler(Exception)
async def server_error(request: Request, exc):
    return JSONResponse(status_code=500, content=fail(f"服务器内部错误: {type(exc).__name__}", code=500))

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(match.router,    prefix="/api/match",    tags=["CBR匹配"])
app.include_router(chat.router,     prefix="/api/chat",     tags=["对话"])
app.include_router(guide.router,    prefix="/api/guide",   tags=["引导选型"])


# ===== W23-D4/D6 新增：工况需求值 + 部件重算（参数全部从 param_dependencies 读）=====
import pymysql
from pydantic import BaseModel
from app.core.params import Params


def _load_params():
    """委托 core.params.Params：唯一参数源，改库即改行为（W26-D6 合并双轨）"""
    return Params()

def _req_values(thickness):
    """工况需求支护强度与工作阻力（选型论文口径）"""
    par = _load_params()
    q = par["k1"] * thickness * par["rock_gamma"] / 1000.0          # MPa
    f = q * (par["beam_length"] + par["roof_end_distance"]) \
          * par["center_distance"] * 1000.0                          # kN
    return {"intensity": round(q, 3), "resistance": round(f, 1)}

@app.get("/api/requirement/")
def get_requirement(coal_thickness: float):
    return {"code": 0, "data": _req_values(coal_thickness), "msg": "ok"}


# ===== W23-D6 部件重算：改缸径/立柱数/泵压 → 链式重算参数 =====
import math
from pydantic import BaseModel

class RecalcReq(BaseModel):
    support_model: str
    bore: float
    column_count: int
    pump_pressure: float
    coal_thickness: float = 8.0

@app.post("/api/recalc/")
def recalc(req: RecalcReq):
    par = _load_params()

    # 链式：初撑力 -> 工作阻力 -> 支护强度
    setting_load = req.column_count * req.pump_pressure * math.pi \
        * (req.bore / 1000.0) ** 2 / 4.0 * 1000.0          # kN
    working_resistance = setting_load / par["setting_ratio"]  # kN
    top_area = (par["beam_length"] + par["roof_end_distance"]) * par["center_distance"]
    intensity = working_resistance * par["eta"] / top_area / 1000.0  # MPa

    req_v = _req_values(req.coal_thickness)
    alarms = []
    if working_resistance < req_v["resistance"]:
        alarms.append({"param": "工作阻力", "value": round(working_resistance, 1),
                       "required": req_v["resistance"]})
    if intensity < req_v["intensity"]:
        alarms.append({"param": "支护强度", "value": round(intensity, 3),
                       "required": req_v["intensity"]})

    return {"code": 0, "msg": "ok", "data": {
        "new_params": {
            "setting_load": round(setting_load, 1),
            "working_resistance": round(working_resistance, 1),
            "intensity": round(intensity, 3),
        },
        "required": req_v,
        "alarms": alarms,
        "inputs": {"bore": req.bore, "column_count": req.column_count,
                   "pump_pressure": req.pump_pressure},
    }}


# ===== W25-C2 首页总览统计接口(W29-D3 下沉 services/stats.py) =====
from app.services.stats import overview as _stats_overview

@app.get("/api/stats/")
def get_stats():
    return {"code": 0, "msg": "ok", "data": _stats_overview()}
