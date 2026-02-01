"""应用配置"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置项"""
    # 数据库
    DATABASE_URL: str = "sqlite:///./rbac.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings()
