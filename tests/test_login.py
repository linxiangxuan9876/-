import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash, verify_password
from app.core.database import SessionLocal, engine, Base
from app.models import User, UserRole

def test_password():
    """测试密码哈希和验证"""
    print("=== 测试密码哈希 ===")
    
    test_password = "admin123"
    hashed = get_password_hash(test_password)
    print(f"原始密码: {test_password}")
    print(f"哈希密码: {hashed}")
    
    result = verify_password(test_password, hashed)
    print(f"验证结果: {result}")
    
    if result:
        print("✅ 密码哈希验证成功！")
    else:
        print("❌ 密码哈希验证失败！")
    
    return result

def test_db():
    """测试数据库初始化"""
    print("\n=== 测试数据库 ===")
    
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
            db.commit()
            print("✅ 创建管理员账号: admin / admin123")
            
            # 重新查询验证
            admin_verify = db.query(User).filter(User.username == "admin").first()
            print(f"用户名: {admin_verify.username}")
            print(f"角色: {admin_verify.role}")
            
            # 验证密码
            verify_result = verify_password("admin123", admin_verify.hashed_password)
            print(f"密码验证: {verify_result}")
        else:
            print("ℹ️ 管理员账号已存在")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("开始测试...")
    test_password()
    test_db()
    print("\n测试完成！")
