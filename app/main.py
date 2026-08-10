from fastapi import FastAPI
from app.routers import areas, supports, match, chat

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
