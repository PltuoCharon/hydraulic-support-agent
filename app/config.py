from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 自动从 .env 读取同名变量；类型不匹配或缺失 → 启动直接报错
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ZHIPUAI_API_KEY: str
    ZHIPUAI_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/"

    DB_HOST: str = "localhost"
    DB_USER: str = "hs_user"
    DB_PASSWORD: str                 # 无默认值 = 必填，.env 里没有就起不来
    DB_NAME: str = "hydraulic_support"

settings = Settings()   # 模块导入时即读取校验，全项目统一 from app.config import settings
