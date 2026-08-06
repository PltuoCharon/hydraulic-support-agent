from fastapi import FastAPI
from app.routers import areas, supports

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
