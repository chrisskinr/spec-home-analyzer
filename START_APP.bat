@echo off
echo ==========================================
echo   Spec Home Analyzer - Starting...
echo ==========================================
echo.

cd /d "%~dp0"
cd app

pip install flask requests --quiet 2>nul

start http://localhost:5050
python app.py

pause
