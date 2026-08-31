@echo off
title PowerPulse - Computer Power Monitor
cd /d "%~dp0"
echo Starting PowerPulse Power Monitor...
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python app.py
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        py app.py
    ) else (
        echo [ERROR] Python is not found. Please install Python from https://www.python.org/
        pause
    )
)
pause
