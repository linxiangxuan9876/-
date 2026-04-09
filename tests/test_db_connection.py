"""
测试 Aiven PostgreSQL 数据库连接
使用环境变量 DATABASE_URL
"""
import os
import sys

# 从环境变量获取数据库连接字符串
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ 错误: 请设置环境变量 DATABASE_URL")
    print("示例: set DATABASE_URL=postgres://user:password@host:port/db?sslmode=require")
    sys.exit(1)

print("=" * 60)
print("测试 Aiven PostgreSQL 数据库连接")
print("=" * 60)

# 隐藏密码显示
url_display = DATABASE_URL
if ':' in DATABASE_URL and '@' in DATABASE_URL:
    parts = DATABASE_URL.split(':')
    if len(parts) >= 3:
        password_part = parts[2].split('@')[0]
        url_display = DATABASE_URL.replace(password_part, '****')

print(f"数据库URL: {url_display}")
print("=" * 60)

try:
    # 使用 psycopg3 直接连接
    import psycopg
    
    print("\n1. 测试 psycopg3 直接连接...")
    conn = psycopg.connect(DATABASE_URL)
    
    with conn.cursor() as cur:
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"✅ 连接成功!")
        print(f"数据库版本: {version[:100]}...")
        
        # 测试创建表
        print("\n2. 测试创建表...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                message VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ 测试表创建成功!")
        
        # 测试插入数据
        print("\n3. 测试插入数据...")
        cur.execute("""
            INSERT INTO test_connection (message) 
            VALUES ('Aiven PostgreSQL connection test successful!')
        """)
        conn.commit()
        print("✅ 数据插入成功!")
        
        # 测试查询
        print("\n4. 测试查询数据...")
        cur.execute("SELECT * FROM test_connection ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        print(f"✅ 查询成功: ID={row[0]}, Message={row[1]}, Time={row[2]}")
        
        # 清理测试数据
        print("\n5. 清理测试数据...")
        cur.execute("DROP TABLE IF EXISTS test_connection")
        conn.commit()
        print("✅ 测试数据已清理!")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过! Aiven 数据库连接正常!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
