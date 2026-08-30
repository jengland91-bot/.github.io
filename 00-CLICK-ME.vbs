Option Explicit
Dim fso, shell, here, ps1
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
here = fso.GetParentFolderName(WScript.ScriptFullName)
ps1 = fso.BuildPath(here, "tools\load-into-meld.ps1")

If Not fso.FileExists(fso.BuildPath(here, "meld\Rise-Above-Meld.json")) Then
  MsgBox "WRONG FOLDER" & vbCrLf & vbCrLf & _
    "Extract the zip first (right-click -> Extract All)." & vbCrLf & _
    "Then open the extracted FOLDER (look for FIND-ME.txt) and double-click 1-OPEN-IN-MELD.bat" & vbCrLf & vbCrLf & _
    "Running from:" & vbCrLf & here, 16, "Rise Above"
  WScript.Quit 1
End If

MsgBox "This copies Rise-Above.json to your Desktop and opens Meld." & vbCrLf & vbCrLf & _
  "It does NOT close Meld." & vbCrLf & vbCrLf & _
  "Then in Meld: File -> Import Session -> Desktop\Rise-Above.json", 64, "Rise Above"

shell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & ps1 & """", 1, True

MsgBox "In Meld: File -> Import Session -> Desktop\Rise-Above.json" & vbCrLf & vbCrLf & _
  "If Meld crashed before: File -> Restore from Backup first.", 64, "Rise Above"
