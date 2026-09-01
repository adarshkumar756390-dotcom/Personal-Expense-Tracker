@echo off
title FinTrack - Personal Expense Tracker
echo ========================================================
echo        FinTrack - Personal Expense & Budget Tracker
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not detected in your PATH!
    echo Please install Python 3.x and check 'Add Python to PATH'.
    pause
    exit /b
)

:: Install requirements
echo [1/2] Checking dependencies...
pip install -r requirements.txt --quiet

:: Launch Browser after a short delay in background
start "" http://127.0.0.1:5000

:: Start Flask App
echo [2/2] Starting server at http://127.0.0.1:5000 ...
echo Press Ctrl+C in this window to stop the server.
echo.
python app.py
pause
