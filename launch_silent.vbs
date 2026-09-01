Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the installation directory where this script is located
installDir = fso.GetParentFolderName(WScript.ScriptFullName)
appScript = """" & installDir & "\app.py"""
trayScript = """" & installDir & "\win_widget\PowerPulseTray.ps1"""

' Smart Python Finder across all standard Windows locations
Function FindPython()
    Dim candidates, p, expanded
    candidates = Array(_
        "pythonw.exe", _
        "pyw.exe", _
        "python.exe", _
        "py.exe", _
        "%LocalAppData%\Programs\Python\Python313\pythonw.exe", _
        "%LocalAppData%\Programs\Python\Python312\pythonw.exe", _
        "%LocalAppData%\Programs\Python\Python311\pythonw.exe", _
        "%LocalAppData%\Programs\Python\Python310\pythonw.exe", _
        "%LocalAppData%\Programs\Python\Python39\pythonw.exe", _
        "%LocalAppData%\Programs\Python\Python38\pythonw.exe", _
        "C:\Python313\pythonw.exe", _
        "C:\Python312\pythonw.exe", _
        "C:\Python311\pythonw.exe", _
        "C:\Python310\pythonw.exe", _
        "C:\Program Files\Python313\pythonw.exe", _
        "C:\Program Files\Python312\pythonw.exe", _
        "C:\Program Files\Python311\pythonw.exe", _
        "C:\Program Files\Python310\pythonw.exe" _
    )
    
    For Each p In candidates
        expanded = WshShell.ExpandEnvironmentStrings(p)
        If InStr(expanded, "\") > 0 Then
            If fso.FileExists(expanded) Then
                FindPython = """" & expanded & """"
                Exit Function
            End If
        Else
            On Error Resume Next
            Dim ret
            ret = WshShell.Run("where " & p, 0, True)
            If Err.Number = 0 And ret = 0 Then
                FindPython = p
                On Error GoTo 0
                Exit Function
            End If
            On Error GoTo 0
        End If
    Next
    FindPython = ""
End Function

pyExe = FindPython()

If pyExe <> "" Then
    On Error Resume Next
    WshShell.Run pyExe & " " & appScript, 0, False
    On Error GoTo 0
Else
    ' Fallback to Windows Python Launcher
    On Error Resume Next
    WshShell.Run "pyw.exe " & appScript, 0, False
    If Err.Number <> 0 Then
        WshShell.Run "python.exe " & appScript, 0, False
    End If
    On Error GoTo 0
End If

' Launch Native Windows System Tray Live Widget silently
On Error Resume Next
WshShell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File " & trayScript, 0, False
On Error GoTo 0
