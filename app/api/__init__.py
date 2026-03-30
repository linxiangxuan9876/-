from app.api.store import router as store_router
from app.api.admin import router as admin_router
from app.api.auth import router as auth_router

__all__ = ["store_router", "admin_router", "auth_router"]
