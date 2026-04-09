"""
环境变量配置模块
直接从 .env 文件加载配置，支持环境变量覆盖
"""
import os
from functools import lru_cache
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-secret-key-do-not-use-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./knowledge_base.db")
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1) if DATABASE_URL.startswith("postgres://") else DATABASE_URL

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "docs"))
    QA_UPLOAD_DIR: str = os.getenv("QA_UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "qa"))

    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")

    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))
    ALLOWED_FILE_EXTENSIONS: str = os.getenv("ALLOWED_FILE_EXTENSIONS", ".pdf,.docx,.doc,.xlsx,.xls,.txt,.csv")

    @field_validator("MAX_FILE_SIZE", mode="before")
    @classmethod
    def parse_file_size(cls, v):
        if isinstance(v, str):
            return int(v)
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """将 CORS_ORIGINS 字符串转换为列表"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_extensions_set(self) -> set[str]:
        """将允许的扩展名字符串转换为集合"""
        return {ext.strip().lower() for ext in self.ALLOWED_FILE_EXTENSIONS.split(",")}


@lru_cache()
def get_settings() -> Settings:
    """获取缓存的配置实例"""
    return Settings()


settings = get_settings()
