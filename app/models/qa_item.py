from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class QAStatus(str, enum.Enum):
    pending_review = "pending_review"  # 待审核
    published = "published"            # 已发布
    rejected = "rejected"              # 已拒绝

class QA_Item(Base):
    __tablename__ = "qa_items"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, nullable=False)
    main_category = Column(String(100), index=True, nullable=False)
    sub_category = Column(String(100), index=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    status = Column(SQLEnum(QAStatus), default=QAStatus.pending_review, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)  # 软删除标记
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # 删除时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
