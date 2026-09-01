; ==============================================================================
; POWER_PULSE // Inno Setup Installer Script for Windows 10 & 11 (64-bit)
; Developed for Yahia Bin Zaman
; ==============================================================================
#define MyAppName "PowerPulse"
#define MyAppVersion "4.2"
#define MyAppPublisher "Yahia Bin Zaman"
#define MyAppURL "https://github.com/yahiabinzaman/power-pulse"
#define MyAppExeName "win_widget\PowerPulseTray.ps1"

[Setup]
AppId={{C8E12F4B-9B21-4F42-8765-POWERPULSE}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
PrivilegesRequired=lowest
OutputDir=..\dist_windows
OutputBaseFilename=PowerPulse-Windows-Setup-v4.2
SetupIconFile=..\assets\logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "Start PowerPulse automatically when Windows boots (Recommended)"; GroupDescription: "Startup Options:"

[Files]
Source: "..\app.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\power_engine.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\static\*"; DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\win_widget\*"; DestDir: "{app}\win_widget"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "wscript.exe"; Parameters: """{app}\launch_silent.vbs"""; WorkingDir: "{app}"; IconFilename: "{app}\assets\logo.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "wscript.exe"; Parameters: """{app}\launch_silent.vbs"""; WorkingDir: "{app}"; IconFilename: "{app}\assets\logo.ico"; Tasks: desktopicon
Name: "{autodesktop}\{#MyAppName} Floating HUD"; Filename: "pythonw.exe"; Parameters: """{app}\win_widget\PowerPulse_Widget.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\assets\logo.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}_AutoStart"; Filename: "wscript.exe"; Parameters: """{app}\launch_silent.vbs"""; WorkingDir: "{app}"; IconFilename: "{app}\assets\logo.ico"; Tasks: startupicon

[Code]
// Create silent VBS background launcher upon installation
procedure CurStepChanged(CurStep: TSetupStep);
var
  VBSContent: String;
  VBSPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    VBSPath := ExpandConstant('{app}\launch_silent.vbs');
    VBSContent := 'Set WshShell = CreateObject("WScript.Shell")' + #13#10 +
                  'WshShell.Run "pythonw """ & "' + ExpandConstant('{app}\app.py') + '"""", 0, False' + #13#10 +
                  'WshShell.Run "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & "' + ExpandConstant('{app}\win_widget\PowerPulseTray.ps1') + '"""", 0, False';
    SaveStringToFile(VBSPath, VBSContent, False);
  end;
end;

[Run]
Filename: "wscript.exe"; Parameters: """{app}\launch_silent.vbs"""; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}} (System Tray & Background Daemon)"; Flags: nowait postinstall skipifsilent
Filename: "http://127.0.0.1:8765"; Description: "Open Web Cockpit in Browser"; Flags: shellexec nowait postinstall skipifsilent
