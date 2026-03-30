from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QAItemBase(BaseModel):
    question: str
    answer: str

class QAItemCreate(QAItemBase):
    pass

class QAItemResponse(QAItemBase):
    id: int
    store_id: str
    main_category: str
    sub_category: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class QAItemUpdate(BaseModel):
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    status: Optional[str] = None

class BatchQAResponse(BaseModel):
    success_count: int
    failed_count: int
    total_count: int
    items: list[QAItemResponse]
