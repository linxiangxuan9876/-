from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    store_id: Optional[str] = None
    store_name: Optional[str] = None
    role: str = "store"

class UserResponse(BaseModel):
    id: int
    username: str
    store_id: Optional[str]
    store_name: Optional[str]
    role: str

    class Config:
        from_attributes = True
