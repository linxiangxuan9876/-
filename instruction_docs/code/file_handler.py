"""
文件上传与验证模块
"""
import os
import uuid
import aiofiles
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.core.config import settings


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".csv"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


async def save_upload_file(upload_file: UploadFile, subfolder: str = "") -> tuple[str, str]:
    """
    保存上传文件

    Args:
        upload_file: FastAPI 上传文件对象
        subfolder: 子文件夹路径

    Returns:
        (file_path, original_filename)
    """
    # 验证文件扩展名
    filename = upload_file.filename or "unknown"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}，支持的类型: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.join(settings.UPLOAD_DIR, subfolder) if subfolder else settings.UPLOAD_DIR

    # 确保目录存在
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, unique_filename)

    # 保存文件
    async with aiofiles.open(file_path, "wb") as f:
        content = await upload_file.read()

        # 验证文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制: {MAX_FILE_SIZE // (1024*1024)}MB"
            )

        await f.write(content)

    return file_path, filename


async def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


class FileValidator:
    """文件验证器"""

    def __init__(self, max_size: int = MAX_FILE_SIZE, allowed_exts: set = ALLOWED_EXTENSIONS):
        self.max_size = max_size
        self.allowed_exts = allowed_exts

    def validate_extension(self, filename: str) -> bool:
        """验证文件扩展名"""
        ext = get_file_extension(filename)
        return ext in self.allowed_exts

    def validate_size(self, size: int) -> bool:
        """验证文件大小"""
        return size <= self.max_size

    def get_validation_error(self, filename: str, size: int) -> Optional[str]:
        """获取验证错误信息"""
        if not self.validate_extension(filename):
            return f"不支持的文件类型: {get_file_extension(filename)}"
        if not self.validate_size(size):
            return f"文件大小超过限制: {self.max_size // (1024*1024)}MB"
        return None
