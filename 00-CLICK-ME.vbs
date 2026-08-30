Option Explicit
Dim fso, shell, here, src, dest, note, desktop, i, candidates
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
here = fso.GetParentFolderName(WScript.ScriptFullName)
src = fso.BuildPath(here, "meld\Rise-Above-Meld.json")

MsgBox "Rise Above" & vbCrLf & vbCrLf & _
  "This copies the Meld file to your Desktop, opens Notepad, and opens Explorer." & vbCrLf & vbCrLf & _
  "Then in Meld Studio: File -> Import Session -> Rise-Above-Meld.json", _
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

note = fso.BuildPath(desktop, "READ-THIS-THEN-OPEN-MELD.txt")
Dim ts
Set ts = fso.CreateTextFile(note, True)
ts.WriteLine "RISE ABOVE - next clicks in Meld Studio"
ts.WriteLine "1. Open Meld Studio (not OBS)"
ts.WriteLine "2. File"
ts.WriteLine "3. Import Session"
ts.WriteLine "4. Pick Rise-Above-Meld.json on your DESKTOP"
ts.WriteLine "   or IMPORT-THIS-IN-MELD.json in:"
ts.WriteLine here
ts.Close

shell.Run "notepad.exe """ & note & """", 1, False
shell.Run "explorer.exe /select,""" & dest & """", 1, False
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

MsgBox "Copied to Desktop:" & vbCrLf & dest & vbCrLf & vbCrLf & _
  "Now in Meld: File -> Import Session -> that file." & vbCrLf & _
  "Leave the black overlay window open.", 64, "Rise Above"
