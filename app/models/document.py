from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class DocStatus(str, enum.Enum):
    pending = "pending"           # 待审核
    parsing = "parsing"           # 解析中
    parsed = "parsed"             # 已解析
    approved = "approved"         # 已通过
    rejected = "rejected"         # 已拒绝

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True, nullable=False)
    store_name = Column(String(100), nullable=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)  # 文件类型：pdf, docx, txt等
    car_model = Column(String(100), index=True, nullable=True)
    category = Column(String(100), index=True, nullable=True)
    status = Column(SQLEnum(DocStatus), default=DocStatus.pending, nullable=False)

    # 文档解析相关字段
    parsed_content = Column(Text, nullable=True)  # 解析后的完整文本内容
    parsed_metadata = Column(JSON, nullable=True)  # 解析后的元数据
    parse_error = Column(Text, nullable=True)  # 解析错误信息

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DocumentQA(Base):
    """从文档中提取的Q&A"""
    __tablename__ = "document_qas"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True, nullable=False)
    store_id = Column(String(50), index=True, nullable=False)

    # Q&A内容
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # 分类
    main_category = Column(String(100), nullable=True)
    sub_category = Column(String(100), nullable=True)

    # 状态
    status = Column(SQLEnum(DocStatus), default=DocStatus.pending, nullable=False)

    # 是否已合并到全量知识库
    is_merged = Column(Integer, default=0)  # 0=未合并, 1=已合并
    merged_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
