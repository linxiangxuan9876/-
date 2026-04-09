"""
数据库连接与会话管理模块
"""
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
from typing import Generator
from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话的依赖注入函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)


def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def get_table_columns(table_name: str) -> list[str]:
    """获取表的所有列名"""
    inspector = inspect(engine)
    return [col["name"] for col in inspector.get_columns(table_name)]


def add_column_if_not_exists(table_name: str, column_name: str, column_definition: str) -> bool:
    """
    如果列不存在则添加

    Args:
        table_name: 表名
        column_name: 列名
        column_definition: 列定义（如 'INTEGER DEFAULT 0'）

    Returns:
        True if added, False if already exists
    """
    inspector = inspect(engine)
    existing_columns = [col["name"] for col in inspector.get_columns(table_name)]

    if column_name not in existing_columns:
        with engine.connect() as conn:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
            conn.commit()
        return True
    return False
