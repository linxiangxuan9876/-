@echo off
echo ==========================================
echo 启动门店知识库本地测试服务器
echo ==========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请安装Python 3.8+
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
)

:: 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate.bat

:: 安装依赖
echo 安装依赖...
pip install -q -r requirements.txt

:: 启动服务器
echo.
echo ==========================================
echo 启动服务器...
echo 访问地址: http://localhost:8000
echo 管理员: admin / admin123
echo 门店: store001 / store123
echo ==========================================
echo.

python run_local.py

pause
