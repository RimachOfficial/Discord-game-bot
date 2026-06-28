@echo off
title Discord Fish Bot - Production Mode
cd /d "%~dp0"

:: Activate your virtual environment
call "PythonGame\Scripts\activate.bat"

:: Run Python with the -O (Optimize) flag
echo 🚀 Launching bot in optimized production mode...
python -O main.py

pause