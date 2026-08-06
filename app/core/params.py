import pymysql
from app.config import settings

class Params:
    """计算参数从 param_dependencies 表加载：改库即改行为，公式入库闭环"""
    _DEFAULTS = {"eta": 0.9, "safety_factor": 1.2}

    def __init__(self):
        self._data = dict(self._DEFAULTS)
        try:
            conn = pymysql.connect(
                host=settings.DB_HOST, user=settings.DB_USER,
                password=settings.DB_PASSWORD, database=settings.DB_NAME,
                charset="utf8mb4")
            with conn.cursor() as cur:
                cur.execute("SELECT param_name, param_value FROM param_dependencies")
                for k, v in cur.fetchall():
                    self._data[k] = self._to_number(v)
            conn.close()
        except Exception as e:
            print(f"[warn] 参数表读取失败,使用默认值: {e}")

    @staticmethod
    def _to_number(v):
        """库里param_value是varchar：能转数字就转，否则保留原字符串"""
        try:
            f = float(v)
            return int(f) if f == int(f) else f
        except (TypeError, ValueError):
            return v

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"未知参数: {name}")
