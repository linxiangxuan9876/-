from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import os
import traceback
import logging

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models import User, UserRole
from app.api import store_router, admin_router, auth_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def init_default_users():
    """初始化默认用户账号"""
    db = SessionLocal()
    try:
        # 创建管理员账号 - 密码不超过72字节
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                store_id="HQ001",
                store_name="总部",
                role=UserRole.admin
            )
            db.add(admin)
            print("✅ 创建管理员账号: admin / admin123")

        # 创建门店账号
        existing_store = db.query(User).filter(User.username == "store1").first()
        if not existing_store:
            store_user = User(
                username="store1",
                hashed_password=get_password_hash("store123"),
                store_id="STORE001",
                store_name="北京朝阳区门店",
                role=UserRole.store
            )
            db.add(store_user)
            print("✅ 创建门店账号: store1 / store123")

        db.commit()
    except Exception as e:
        print(f"初始化用户失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.QA_UPLOAD_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    init_default_users()  # 初始化默认用户
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# 解析 CORS_ORIGINS 环境变量
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 全局异常处理器
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"验证错误: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "请求参数验证失败", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "服务器内部错误，请稍后重试"}
    )

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(store_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)

def read_html(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "templates", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=read_html("index.html"))

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(content=read_html("login.html"))

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return HTMLResponse(content=read_html("admin.html"))

@app.get("/store", response_class=HTMLResponse)
async def store_page():
    return HTMLResponse(content=read_html("store.html"))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug/users")
async def list_users():
    """调试接口：列出所有用户"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return {
            "count": len(users),
            "users": [{"id": u.id, "username": u.username, "role": u.role.value} for u in users]
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@app.get("/debug/create-test-users")
async def create_test_users():
    """调试接口：创建测试用户"""
    db = SessionLocal()
    result = []
    try:
        # 创建管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                store_id="HQ001",
                store_name="总部",
                role=UserRole.admin
            )
            db.add(admin)
            result.append("创建 admin 用户成功")
        
        # 创建门店用户
        store = db.query(User).filter(User.username == "store1").first()
        if not store:
            store = User(
                username="store1",
                hashed_password=get_password_hash("store123"),
                store_id="STORE001",
                store_name="北京朝阳区门店",
                role=UserRole.store
            )
            db.add(store)
            result.append("创建 store1 用户成功")
        
        db.commit()
        
        if not result:
            result.append("用户已存在，无需创建")
            
        return {"status": "success", "message": result}
    except Exception as e:
        db.rollback()
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}
    finally:
        db.close()

@app.get("/debug/config")
async def show_config():
    """调试接口：显示配置信息"""
    return {
        "database_url": settings.DATABASE_URL,
        "upload_dir": settings.UPLOAD_DIR,
        "qa_upload_dir": settings.QA_UPLOAD_DIR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
