from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "4S店售后知识库"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # 数据库路径 - 优先使用环境变量，否则使用本地路径
    # 将 postgres:// 转换为 postgresql:// 以兼容 SQLAlchemy
    _raw_db_url: str = os.getenv("DATABASE_URL", "sqlite:///./knowledge_base.db")
    DATABASE_URL: str = _raw_db_url.replace("postgres://", "postgresql://", 1) if _raw_db_url.startswith("postgres://") else _raw_db_url

    # 上传目录 - 使用环境变量或默认路径
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "docs"))
    QA_UPLOAD_DIR: str = os.getenv("QA_UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "qa"))

    OPENAI_API_KEY: Optional[str] = "sk-ajyewwhwzachwalfelzyzjjupiqcjtmjvrzsjjqknyljlrfv"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_BASE_URL: str = "https://api.siliconflow.cn/v1"

    class Config:
        case_sensitive = True

settings = Settings()
