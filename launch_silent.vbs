Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the installation directory where this script is located
installDir = fso.GetParentFolderName(WScript.ScriptFullName)

appScript = """" & installDir & "\app.py"""
trayScript = """" & installDir & "\win_widget\PowerPulseTray.ps1"""

' Launch Python telemetry server silently (No black console window)
WshShell.Run "pythonw " & appScript, 0, False

' Launch Native Windows System Tray Live Widget silently
WshShell.Run "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File " & trayScript, 0, False
