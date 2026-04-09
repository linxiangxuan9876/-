"""
Aiven PostgreSQL 数据库配置脚本
"""
import os

print("=" * 60)
print("Aiven PostgreSQL 数据库配置")
print("=" * 60)
print("""
请按以下步骤获取 Aiven 数据库连接信息：

1. 访问 https://console.aiven.io
2. 登录你的账号
3. 点击 "Create Service"
4. 选择：
   - Service: PostgreSQL
   - Plan: Free-1-1gb (1GB免费)
   - Region: Asia Pacific
5. 点击 "Create Service"
6. 等待服务启动完成
7. 点击 "Overview" → "Connection Info"
8. 选择 "Python" 或 "SQLAlchemy"
9. 复制连接字符串

连接字符串格式：
postgresql://username:password@host:port/defaultdb?sslmode=require

请把连接字符串发给我（密码用****代替）
""")
print("=" * 60)
