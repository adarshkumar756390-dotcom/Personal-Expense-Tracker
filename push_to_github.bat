@echo off
title Push FinTrack to GitHub
echo ========================================================
echo         Push FinTrack to GitHub Repository
echo ========================================================
echo.
echo Make sure you have created the empty repository on GitHub:
echo https://github.com/new with name: Personal-Expense-Tracker
echo.
echo Pushing branch 'main' to https://github.com/adarshkumar756390-dotcom/Personal-Expense-Tracker.git ...
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  SUCCESS! Your project is now live on GitHub:
    echo  https://github.com/adarshkumar756390-dotcom/Personal-Expense-Tracker
    echo ========================================================
) else (
    echo.
    echo If this failed:
    echo 1. Check that you created the repo 'Personal-Expense-Tracker' on https://github.com/new
    echo 2. Make sure you are logged in to your GitHub account when the browser prompt appears.
)
echo.
pause
