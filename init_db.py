import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models import User, UserRole, Document, QA_Item

def init_db():
    print("正在初始化数据库...")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
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
        else:
            print("ℹ️ 管理员账号已存在")

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
        else:
            print("ℹ️ 门店账号已存在")

        existing_store2 = db.query(User).filter(User.username == "store2").first()
        if not existing_store2:
            store_user2 = User(
                username="store2",
                hashed_password=get_password_hash("store123"),
                store_id="STORE002",
                store_name="上海浦东门店",
                role=UserRole.store
            )
            db.add(store_user2)
            print("✅ 创建门店账号: store2 / store123")
        else:
            print("ℹ️ 门店2账号已存在")

        db.commit()
        print("\n🎉 数据库初始化完成！")
        print("\n登录信息：")
        print("  管理员: admin / admin123")
        print("  门店1: store1 / store123")
        print("  门店2: store2 / store123")

    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
