@echo off
:: ==============================================================================
:: CYBER_VOLT // PowerPulse One-Click Windows Setup (100% Virus-Free / Clean)
:: Developed for Yahia Bin Zaman
:: ==============================================================================
title PowerPulse Setup - Yahia Bin Zaman
color 0A

echo ==========================================================
echo   CYBER_VOLT // PowerPulse Windows Installer
echo   System Architect: Yahia Bin Zaman
echo ==========================================================
echo.

set "INSTALL_DIR=%LocalAppData%\PowerPulse"
echo [*] Installing PowerPulse to: %INSTALL_DIR%
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\static" 2>nul

echo [*] Copying core engine files...
copy /Y "%~dp0app.py" "%INSTALL_DIR%\" >nul
copy /Y "%~dp0power_engine.py" "%INSTALL_DIR%\" >nul
copy /Y "%~dp0README.md" "%INSTALL_DIR%\" >nul
copy /Y "%~dp0LICENSE" "%INSTALL_DIR%\" >nul
xcopy /E /I /Y "%~dp0static\*" "%INSTALL_DIR%\static\" >nul

:: Create silent background VBS runner (No black CMD box popup)
echo [*] Creating silent background daemon launcher...
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run "python """ ^& "%INSTALL_DIR%\app.py"""", 0, False
) > "%INSTALL_DIR%\launch_silent.vbs"

:: Create standard batch launcher
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo start "" python app.py
echo start http://127.0.0.1:8765
) > "%INSTALL_DIR%\run_windows.bat"

:: Create Desktop Shortcut via PowerShell
echo [*] Creating Desktop Shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ws = New-Object -ComObject WScript.Shell; " ^
"$s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\PowerPulse.lnk'); " ^
"$s.TargetPath = 'wscript.exe'; " ^
"$s.Arguments = '\"%INSTALL_DIR%\launch_silent.vbs\"'; " ^
"$s.WorkingDirectory = '%INSTALL_DIR%'; " ^
"$s.Description = 'CYBER_VOLT Power & Network Telemetry Cockpit'; " ^
"$s.Save()"

:: Create Windows Startup entry (Persists on reboot)
echo [*] Setting up Auto-Start on Windows Boot...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ws = New-Object -ComObject WScript.Shell; " ^
"$s = $ws.CreateShortcut([Environment]::GetFolderPath('Startup') + '\PowerPulse_AutoStart.lnk'); " ^
"$s.TargetPath = 'wscript.exe'; " ^
"$s.Arguments = '\"%INSTALL_DIR%\launch_silent.vbs\"'; " ^
"$s.WorkingDirectory = '%INSTALL_DIR%'; " ^
"$s.Description = 'PowerPulse Background Telemetry Service'; " ^
"$s.Save()"

echo.
echo ==========================================================
echo  [OK] INSTALLATION COMPLETE!
echo  - Installed to: %INSTALL_DIR%
echo  - Desktop Shortcut created: PowerPulse
echo  - Windows Auto-Start on Boot: ENABLED (No virus flags)
echo ==========================================================
echo.
echo Starting PowerPulse now...
start "" "%INSTALL_DIR%\launch_silent.vbs"
timeout /t 2 >nul
start http://127.0.0.1:8765
echo Done. Press any key to exit setup.
pause >nul
