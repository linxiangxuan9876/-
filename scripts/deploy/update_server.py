"""
服务器更新脚本
用于在服务器上拉取最新代码并重启服务
"""
import subprocess
import sys
import os

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
    print("  4S 店售后知识库 - 服务器更新脚本")
    print("="*60)
    
    # 1. Git 拉取最新代码
    print("\n[1/4] 拉取最新代码...")
    if not run_command("git pull origin main", "拉取代码"):
        print("\n⚠️  代码更新失败，请检查网络连接")
        return False
    
    # 2. 安装依赖
    print("\n[2/4] 检查依赖...")
    if not run_command("pip install -r requirements.txt", "安装依赖"):
        print("\n⚠️  依赖安装失败")
        return False
    
    # 3. 数据库迁移
    print("\n[3/4] 数据库迁移...")
    if os.path.exists('migrate_db.py'):
        if not run_command("python migrate_db.py", "数据库迁移"):
            print("\n⚠️  数据库迁移失败")
            return False
    else:
        print("  ℹ️  未找到迁移脚本，跳过")
    
    # 4. 重启服务
    print("\n[4/4] 重启服务...")
    print("\n" + "="*60)
    print("  更新完成！")
    print("="*60)
    print("\n请手动重启服务:")
    print("  # 如果使用 systemd:")
    print("  sudo systemctl restart store-knowledge-base")
    print("\n  # 如果直接运行:")
    print("  # 先停止当前服务，然后重新运行:")
    print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("\n" + "="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
