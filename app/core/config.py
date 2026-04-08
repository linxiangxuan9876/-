from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "4S店售后知识库"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-secret-key-do-not-use-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # 数据库路径 - 优先使用环境变量，否则使用本地路径
    # 将 postgres:// 转换为 postgresql:// 以兼容 SQLAlchemy
    _raw_db_url: str = os.getenv("DATABASE_URL", "sqlite:///./knowledge_base.db")
    DATABASE_URL: str = _raw_db_url.replace("postgres://", "postgresql://", 1) if _raw_db_url.startswith("postgres://") else _raw_db_url

    # 上传目录 - 使用环境变量或默认路径
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "docs"))
    QA_UPLOAD_DIR: str = os.getenv("QA_UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "qa"))

    # OpenAI API 配置 - 必须从环境变量读取，绝不能硬编码
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")

    # CORS 配置 - 允许的域名列表
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    # 文件上传配置
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 默认 50MB
    ALLOWED_FILE_EXTENSIONS: str = os.getenv("ALLOWED_FILE_EXTENSIONS", ".pdf,.docx,.doc,.xlsx,.xls,.txt,.csv")

    class Config:
        case_sensitive = True

settings = Settings()
