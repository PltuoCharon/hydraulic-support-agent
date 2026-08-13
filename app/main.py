from fastapi import FastAPI
from app.routers import areas, supports, match, chat, guide

app = FastAPI(
    title="液压支架智能选型 API",
    description="毕设项目后端：支架库查询 / 选型推荐 / RAG 问答",
    version="0.1.0",
)

app.include_router(areas.router,    prefix="/api/areas",    tags=["矿区"])
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

_CFG = dict(host="localhost", user="hs_user", password="你的密码",
            database="hydraulic_support", charset="utf8mb4")
_PARAM_DEFAULTS = {"k1": 8.0, "rock_gamma": 25.0, "beam_length": 5.2,
                   "roof_end_distance": 0.7, "center_distance": 2.05,
                   "eta": 0.9, "setting_ratio": 0.7, "safety_factor": 1.2}

def _load_params():
    """从 param_dependencies 表读参数，未命中用默认值兜底（第8项 eta 闭环）"""
    p = dict(_PARAM_DEFAULTS)
    try:
        conn = pymysql.connect(**_CFG)
        with conn.cursor() as cur:
            cur.execute("SELECT param_name, param_value FROM param_dependencies")
            p.update({k: v for k, v in cur.fetchall()})
        conn.close()
    except Exception as e:
        print("[warn] param_dependencies 读取失败，用默认值:", e)
    return p

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
