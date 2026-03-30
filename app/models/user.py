from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    store = "store"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    store_id = Column(String(50), index=True, nullable=True)
    store_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.store, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
