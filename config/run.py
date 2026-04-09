#!/usr/bin/env python
import subprocess
import sys
import os

def main():
    print("=" * 50)
    print("  4S店售后知识库 - 启动脚本")
    print("=" * 50)
    print()

    print("[1/3] 检查Python环境...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"  ✅ {result.stdout.strip()}")
    except Exception as e:
        print(f"  ❌ Python检查失败: {e}")
        return

    print("\n[2/3] 安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("  ✅ 依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 依赖安装失败: {e}")
        return

    print("\n[3/3] 初始化数据库...")
    try:
        subprocess.check_call([sys.executable, "init_db.py"])
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️ 数据库初始化有些问题，继续启动...")

    print("\n" + "=" * 50)
    print("  🚀 启动服务...")
    print("  📍 访问地址: http://localhost:8000")
    print("  📖 API文档: http://localhost:8000/docs")
    print("=" * 50)
    print()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

if __name__ == "__main__":
    main()
