from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core import get_db, verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models import User, UserRole
from app.schemas import Token, UserLogin, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["认证接口"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "store_id": user.store_id},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    hashed_password = get_password_hash(user_data.password)

    role = UserRole.store
    if user_data.role == "admin":
        role = UserRole.admin

    db_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        store_id=user_data.store_id,
        store_name=user_data.store_name,
        role=role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
