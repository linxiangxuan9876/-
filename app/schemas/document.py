from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    car_model: Optional[str] = None
    category: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    store_id: str
    store_name: Optional[str]
    filename: str
    original_filename: str
    file_size: Optional[int]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    car_model: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
