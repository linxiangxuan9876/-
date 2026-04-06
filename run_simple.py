"""
本地运行脚本 - 用于本地测试
"""
import os
import sys

# 设置本地环境变量
os.environ["DATABASE_URL"] = "sqlite:///./knowledge_base_local.db"
os.environ["UPLOAD_DIR"] = os.path.join(os.path.dirname(__file__), "uploads", "docs")
os.environ["QA_UPLOAD_DIR"] = os.path.join(os.path.dirname(__file__), "uploads", "qa")
os.environ["SECRET_KEY"] = "local-test-secret-key"

# 确保上传目录存在
os.makedirs(os.environ["UPLOAD_DIR"], exist_ok=True)
os.makedirs(os.environ["QA_UPLOAD_DIR"], exist_ok=True)

print("=" * 60)
print("本地测试服务器启动")
print("=" * 60)
print(f"数据库: {os.environ['DATABASE_URL']}")
print(f"文档上传目录: {os.environ['UPLOAD_DIR']}")
print(f"QA上传目录: {os.environ['QA_UPLOAD_DIR']}")
print("=" * 60)
print("访问地址: http://localhost:8000")
print("管理员账号: admin / admin123")
print("门店账号: store1 / store123")
print("=" * 60)

# 导入并运行应用
from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
