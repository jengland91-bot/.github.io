Option Explicit
Dim fso, shell, here, src, dest, note, desktop, scenesSrc, scenesDest, i, candidates
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
here = fso.GetParentFolderName(WScript.ScriptFullName)
src = fso.BuildPath(here, "meld\Rise-Above-Meld.json")

MsgBox "Rise Above" & vbCrLf & vbCrLf & _
  "This copies the SCENES folder to your Desktop." & vbCrLf & vbCrLf & _
  "Then in Meld: File -> Import Session -> Rise Above scenes -> 0 ALL SCENES.json" & vbCrLf & _
  "(or 4 RACE.json to try just one look)", _
  64, "Rise Above"

If Not fso.FileExists(src) Then
  MsgBox "WRONG FOLDER" & vbCrLf & vbCrLf & _
    "Extract the zip first (right-click -> Extract All)." & vbCrLf & _
    "Then open the Rise-Above-Meld FOLDER and double-click this again." & vbCrLf & vbCrLf & _
    "Running from:" & vbCrLf & here, 16, "Rise Above"
  WScript.Quit 1
End If

On Error Resume Next
fso.CopyFile src, fso.BuildPath(here, "IMPORT-THIS-IN-MELD.json"), True
desktop = shell.SpecialFolders("Desktop")
If desktop = "" Then desktop = shell.ExpandEnvironmentStrings("%USERPROFILE%\Desktop")
dest = fso.BuildPath(desktop, "Rise-Above-Meld.json")
fso.CopyFile src, dest, True
fso.CopyFile src, shell.ExpandEnvironmentStrings("%USERPROFILE%\OneDrive\Desktop\Rise-Above-Meld.json"), True

scenesSrc = fso.BuildPath(here, "LOAD-THESE-SCENES")
scenesDest = fso.BuildPath(desktop, "Rise Above scenes")
If fso.FolderExists(scenesSrc) Then
  If fso.FolderExists(scenesDest) Then fso.DeleteFolder scenesDest, True
  fso.CopyFolder scenesSrc, scenesDest, True
End If

note = fso.BuildPath(desktop, "READ-THIS-THEN-OPEN-MELD.txt")
Dim ts
Set ts = fso.CreateTextFile(note, True)
ts.WriteLine "RISE ABOVE - load a scene in Meld Studio"
ts.WriteLine "1. Open Meld Studio (not OBS)"
ts.WriteLine "2. File -> Import Session"
ts.WriteLine "3. Open Desktop folder: Rise Above scenes"
ts.WriteLine "4. Pick 0 ALL SCENES.json for every scene"
ts.WriteLine "   or 4 RACE.json to try just the race look"
ts.WriteLine "Those files are also in:"
ts.WriteLine fso.BuildPath(here, "LOAD-THESE-SCENES")
ts.Close

shell.Run "notepad.exe """ & note & """", 1, False
If fso.FolderExists(scenesDest) Then
  shell.Run "explorer.exe """ & scenesDest & """", 1, False
Else
  shell.Run "explorer.exe """ & scenesSrc & """", 1, False
End If
shell.Run "cmd.exe /k """ & fso.BuildPath(here, "tools\Start-MeldLayout.bat") & """", 1, False

candidates = Array( _
  shell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Meld Studio\Meld Studio.exe"), _
  shell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Meld Studio\Meld Studio.exe"), _
  shell.ExpandEnvironmentStrings("%ProgramFiles%\Meld Studio\Meld Studio.exe"), _
  shell.ExpandEnvironmentStrings("%ProgramFiles(x86)%\Meld Studio\Meld Studio.exe") _
)
For i = 0 To UBound(candidates)
  If fso.FileExists(candidates(i)) Then
    shell.Run """" & candidates(i) & """", 1, False
    Exit For
  End If
Next

MsgBox "Scenes folder on Desktop: Rise Above scenes" & vbCrLf & vbCrLf & _
  "Meld -> File -> Import Session -> 0 ALL SCENES.json" & vbCrLf & _
  "Leave the black overlay window open.", 64, "Rise Above"
