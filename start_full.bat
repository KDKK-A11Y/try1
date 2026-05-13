@echo off
title 智能语音交互控制系统 - 完整版
echo.
echo ================================
echo  智能语音交互控制系统 - 完整版
echo ================================
echo.

set PYTHON_PATH=C:/Users/hesha/anaconda3/python.exe
set PIP_PATH=C:/Users/hesha/anaconda3/Scripts/pip.exe

echo 1. 安装/更新依赖...
echo ------------------------
"%PIP_PATH%" install PyQt5 SpeechRecognition mediapipe pyaudio numpy opencv-python

if %errorlevel% equ 0 (
    echo.
    echo ✓ 依赖安装成功
    echo.
    echo 2. 启动应用程序...
    echo ------------------------
    "%PYTHON_PATH%" main.py
) else (
    echo.
    echo ✗ 依赖安装失败
    echo 尝试使用 conda 安装 pyaudio...
    C:/Users/hesha/anaconda3/Scripts/conda.exe install -c anaconda pyaudio -y
    
    if %errorlevel% equ 0 (
        echo.
        echo ✓ pyaudio 安装成功
        echo.
        echo 2. 启动应用程序...
        echo ------------------------
        "%PYTHON_PATH%" main.py
    ) else (
        echo.
        echo ✗ 安装失败，请手动安装依赖
        pause
    )
)