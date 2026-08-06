import pymysql
from app.config import settings

def get_conn():
    return pymysql.connect(
        host=settings.DB_HOST, user=settings.DB_USER,
        password=settings.DB_PASSWORD, database=settings.DB_NAME,
        charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
    )

def get_db():
    """FastAPI依赖：每个请求自动开连接，请求结束自动关闭"""
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()
