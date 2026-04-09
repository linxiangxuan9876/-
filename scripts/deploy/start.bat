@echo off
echo ========================================
echo   4S店售后知识库 - 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

echo [2/3] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo [3/3] 初始化数据库...
python init_db.py

echo.
echo ========================================
echo   启动服务...
echo   访问地址: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo ========================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
