@echo off
:: ==============================================================================
:: CYBER_VOLT // Windows One-Click Installer & System Tray Widget Setup
:: Developed for Yahia Bin Zaman
:: ==============================================================================
title CYBER_VOLT Installer - Yahia Bin Zaman

echo ==========================================================
echo ⚡ CYBER_VOLT // Windows Installer & System Tray Widget Setup
echo    System Architect: Yahia Bin Zaman
echo ==========================================================
echo.

set "INSTALL_DIR=%LocalAppData%\PowerPulse"
mkdir "%INSTALL_DIR%" 2>nul

echo [1/3] Copying Application Files to %INSTALL_DIR%...
xcopy /E /I /Y "%~dp0*" "%INSTALL_DIR%\" >nul

echo [2/3] Creating Desktop Shortcut...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\CYBER_VOLT.lnk'); $s.TargetPath = '%INSTALL_DIR%\run_windows.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Save()"

echo [3/3] Setting up Windows Auto-Start on Boot...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Startup') + '\CYBER_VOLT_AutoStart.lnk'); $s.TargetPath = '%INSTALL_DIR%\run_windows.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Save()"

echo.
echo ==========================================================
echo ✅ INSTALLATION COMPLETE FOR WINDOWS!
echo    • App installed to: %INSTALL_DIR%
echo    • Desktop Shortcut created: CYBER_VOLT.lnk
echo    • Auto-Start on Windows Boot enabled!
echo ==========================================================
echo.
echo Starting CYBER_VOLT now...
start "" "%INSTALL_DIR%\run_windows.bat"
pause
