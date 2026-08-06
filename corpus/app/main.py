from fastapi import FastAPI

app = FastAPI(
    title="液压支架智能选型 API",
    description="毕设项目后端：支架库查询 / 选型推荐 / RAG 问答",
    version="0.1.0",
)

@app.get("/")
def root():
    return {"msg": "hs-agent backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

