"""
服务器部署脚本
用于在 VPS 或云服务器上部署应用
"""
import os
import subprocess
import sys

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - 成功")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} - 失败")
        if result.stderr:
            print(result.stderr)
        return False

def main():
    print("\n" + "="*60)
    print("  4S 店售后知识库 - 服务器部署脚本")
    print("="*60)
    
    # 1. 检查 Python 版本
    print("\n[1/6] 检查 Python 环境...")
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print("❌ Python 版本过低，需要 Python 3.8+")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 2. 创建虚拟环境（可选）
    print("\n[2/6] 创建虚拟环境...")
    if not os.path.exists('.venv'):
        run_command(f"{sys.executable} -m venv .venv", "创建虚拟环境")
        print("✅ 虚拟环境已创建")
    else:
        print("⚠️  虚拟环境已存在，跳过")
    
    # 3. 激活虚拟环境并安装依赖
    print("\n[3/6] 安装依赖...")
    if os.name == 'nt':  # Windows
        pip_path = '.venv\\Scripts\\pip.exe'
        python_path = '.venv\\Scripts\\python.exe'
    else:  # Linux/Mac
        pip_path = '.venv/bin/pip'
        python_path = '.venv/bin/python'
    
    if not run_command(f'"{pip_path}" install --upgrade pip', "升级 pip"):
        return False
    
    if not run_command(f'"{pip_path}" install -r requirements.txt', "安装项目依赖"):
        return False
    
    # 4. 初始化数据库
    print("\n[4/6] 初始化数据库...")
    if not run_command(f'"{python_path}" init_db.py', "初始化数据库"):
        return False
    
    # 5. 创建上传目录
    print("\n[5/6] 创建上传目录...")
    os.makedirs('uploads/docs', exist_ok=True)
    os.makedirs('uploads/qa', exist_ok=True)
    print("✅ 上传目录已创建")
    
    # 6. 启动服务
    print("\n[6/6] 启动服务...")
    print("\n" + "="*60)
    print("  部署完成！")
    print("="*60)
    print("\n启动命令:")
    print(f"  {python_path} -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("\n或使用后台运行:")
    print(f"  nohup {python_path} -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &")
    print("\n访问地址:")
    print("  http://your-server-ip:8000")
    print("  API 文档：http://your-server-ip:8000/docs")
    print("\n默认账号:")
    print("  管理员：admin / admin123")
    print("  门店：store1 / store123")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
