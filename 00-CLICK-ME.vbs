Option Explicit
Dim fso, shell, here, ps1
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
here = fso.GetParentFolderName(WScript.ScriptFullName)
ps1 = fso.BuildPath(here, "tools\load-into-meld.ps1")

If Not fso.FileExists(fso.BuildPath(here, "meld\Rise-Above-Meld.json")) Then
  MsgBox "WRONG FOLDER" & vbCrLf & vbCrLf & _
    "Extract the zip first (right-click -> Extract All)." & vbCrLf & _
    "Then open the Rise-Above-Meld FOLDER and double-click 1-OPEN-IN-MELD.bat" & vbCrLf & vbCrLf & _
    "Running from:" & vbCrLf & here, 16, "Rise Above"
  WScript.Quit 1
End If

MsgBox "Rise Above will open Meld and load the scenes." & vbCrLf & vbCrLf & _
  "Wait about 10 seconds. Leave the black overlay window open.", 64, "Rise Above"

shell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & ps1 & """", 1, True

MsgBox "If Meld shows STARTING SOON / GRID / RACE / BRB, you are done." & vbCrLf & vbCrLf & _
  "If it is empty: File -> Import Session -> Ctrl+V -> Open.", 64, "Rise Above"
