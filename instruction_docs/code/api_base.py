"""
API 路由基础类与通用响应包装
"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    class Config:
        from_attributes = True


class PageResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    total: int
    items: list[T]
    page: int
    page_size: int
    total_pages: int


def get_router(prefix: str = "", tags: list[str] = None) -> APIRouter:
    """创建 API 路由"""
    return APIRouter(prefix=prefix, tags=tags or [])


def success_response(data: T = None, message: str = "success") -> dict:
    """成功响应"""
    return {
        "code": 200,
        "message": message,
        "data": data
    }


def error_response(message: str, code: int = 400) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": None
    }


def paginate_query(query, page: int = 1, page_size: int = 100):
    """
    分页查询辅助函数

    Args:
        query: SQLAlchemy 查询对象
        page: 页码（从 1 开始）
        page_size: 每页数量

    Returns:
        (items, total, total_pages)
    """
    total = query.count()
    total_pages = (total + page_size - 1) // page_size

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return items, total, total_pages
