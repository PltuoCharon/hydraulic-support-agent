from fastapi import FastAPI

app = FastAPI(
    title="液压支架智能体 API",
    description="毕设项目：液压支架选型与知识问答后端",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"msg": "液压支架智能体 API 运行中", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
