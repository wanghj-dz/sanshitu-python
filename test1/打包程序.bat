@echo off
chcp 65001 >nul
echo ========================================
echo 正投影与斜投影实验程序打包工具
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python环境
    echo 请先安装Python 3.11或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

echo [2/4] 安装依赖库...
pip install numpy matplotlib pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo 错误: 依赖库安装失败
    pause
    exit /b 1
)
echo.

echo [3/4] 开始打包程序...
pyinstaller --onefile --windowed --name "投影实验程序" projection_experiment.py
if %errorlevel% neq 0 (
    echo 错误: 打包失败
    pause
    exit /b 1
)
echo.

echo [4/4] 打包完成!
echo.
echo ========================================
echo 程序位置: dist\投影实验程序.exe
echo 文件大小: 约40-50MB
echo ========================================
echo.
echo 按任意键打开dist文件夹...
pause >nul
explorer dist
