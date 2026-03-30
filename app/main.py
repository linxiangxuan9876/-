from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models import User, UserRole
from app.api import store_router, admin_router, auth_router

def init_default_users():
    """初始化默认用户账号"""
    db = SessionLocal()
    try:
        # 创建管理员账号
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        return {"status": "error", "message": str(e)}
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
