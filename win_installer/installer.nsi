; ==============================================================================
; POWER_PULSE // Professional Native Windows .EXE Setup Installer (NSIS)
; System Architect: Yahia Bin Zaman
; ==============================================================================
!include "MUI2.nsh"
!include "FileFunc.nsh"

; General Definitions
!define PRODUCT_NAME "PowerPulse"
!define PRODUCT_VERSION "4.2.0.0"
!define PRODUCT_VERSION_STR "4.2"
!define PRODUCT_PUBLISHER "Yahia Bin Zaman"
!define PRODUCT_WEB_SITE "https://github.com/yahiabinzaman/power-pulse"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKCU"

; Version Information for Windows Explorer & Defender Trust
VIProductVersion "${PRODUCT_VERSION}"
VIFileVersion "${PRODUCT_VERSION}"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "Comments" "PowerPulse Hardware Power & Network Telemetry Cockpit"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "Copyright (C) 2026 Yahia Bin Zaman"
VIAddVersionKey "FileDescription" "PowerPulse Installer"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION_STR}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION_STR}"
VIAddVersionKey "OriginalFilename" "PowerPulse-Windows-Setup-v4.2.exe"

; Name and Output File
Name "${PRODUCT_NAME} ${PRODUCT_VERSION_STR}"
OutFile "..\PowerPulse-Windows-Setup-v4.2.exe"
InstallDir "$LOCALAPPDATA\PowerPulse"
RequestExecutionLevel user
SetCompressor /SOLID lzma

; Interface Configuration
!define MUI_ICON "..\assets\logo.ico"
!define MUI_UNICON "..\assets\logo.ico"
!define MUI_ABORTWARNING

; Modern UI Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

; Finish Page Options
!define MUI_FINISHPAGE_RUN "$INSTDIR\launch_silent.vbs"
!define MUI_FINISHPAGE_RUN_TEXT "Launch PowerPulse (Live Tray Widget & Daemon)"
!define MUI_FINISHPAGE_SHOWREADME "http://127.0.0.1:8765"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Open Web Cockpit in Browser"
!insertmacro MUI_PAGE_FINISH

; Uninstaller Pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Section
Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    SetOverwrite on

    ; Core Files
    File "..\app.py"
    File "..\power_engine.py"
    File "..\README.md"
    File "..\LICENSE"
    File "..\launch_silent.vbs"

    ; Assets & Static Web UI
    SetOutPath "$INSTDIR\static"
    File /r "..\static\*.*"

    SetOutPath "$INSTDIR\assets"
    File /r "..\assets\*.*"

    SetOutPath "$INSTDIR\win_widget"
    File /r "..\win_widget\*.*"

    SetOutPath "$INSTDIR"

    ; Create Shortcuts
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "wscript.exe" '"$INSTDIR\launch_silent.vbs"' "$INSTDIR\assets\logo.ico" 0
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME} Floating HUD.lnk" "pythonw.exe" '"$INSTDIR\win_widget\PowerPulse_Widget.pyw"' "$INSTDIR\assets\logo.ico" 0
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0

    ; Desktop Shortcuts
    CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "wscript.exe" '"$INSTDIR\launch_silent.vbs"' "$INSTDIR\assets\logo.ico" 0
    CreateShortCut "$DESKTOP\${PRODUCT_NAME} Floating HUD.lnk" "pythonw.exe" '"$INSTDIR\win_widget\PowerPulse_Widget.pyw"' "$INSTDIR\assets\logo.ico" 0

    ; Windows Startup (Auto-Start on Boot)
    CreateShortCut "$SMSTARTUP\${PRODUCT_NAME}_AutoStart.lnk" "wscript.exe" '"$INSTDIR\launch_silent.vbs"' "$INSTDIR\assets\logo.ico" 0

    ; Write Uninstaller & Registry Entries
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\assets\logo.ico"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Terminate running processes if any
    ExecWait 'taskkill /F /IM pythonw.exe'

    ; Delete Files & Folders
    RMDir /r "$INSTDIR\static"
    RMDir /r "$INSTDIR\assets"
    RMDir /r "$INSTDIR\win_widget"
    Delete "$INSTDIR\app.py"
    Delete "$INSTDIR\power_engine.py"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\launch_silent.vbs"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"

    ; Delete Shortcuts
    Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
    Delete "$DESKTOP\${PRODUCT_NAME} Floating HUD.lnk"
    Delete "$SMSTARTUP\${PRODUCT_NAME}_AutoStart.lnk"
    RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"

    ; Remove Registry Entry
    DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
SectionEnd
