Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strDesktop = WshShell.SpecialFolders("Desktop")
strCurrentDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Create debug shortcut (shows console)
Set oShellLink1 = WshShell.CreateShortcut(strDesktop & "\STAR Analysis System (Debug).lnk")
oShellLink1.TargetPath = strCurrentDir & "\debug_startup.bat"
oShellLink1.WorkingDirectory = strCurrentDir
oShellLink1.Description = "STAR Analysis System - Debug Mode (shows console)"
oShellLink1.IconLocation = "shell32.dll,21"
oShellLink1.Save

' Create silent shortcut
Set oShellLink2 = WshShell.CreateShortcut(strDesktop & "\STAR Analysis System (Silent).lnk")
oShellLink2.TargetPath = strCurrentDir & "\debug_startup_silent.vbs"
oShellLink2.WorkingDirectory = strCurrentDir
oShellLink2.Description = "STAR Analysis System - Silent Mode"
oShellLink2.IconLocation = "shell32.dll,21"
oShellLink2.Save

' Create direct Python shortcut
Set oShellLink3 = WshShell.CreateShortcut(strDesktop & "\STAR Analysis System (Direct).lnk")
oShellLink3.TargetPath = "python"
oShellLink3.Arguments = Chr(34) & strCurrentDir & "\star_gui.py" & Chr(34)
oShellLink3.WorkingDirectory = strCurrentDir
oShellLink3.Description = "STAR Analysis System - Direct Python"
oShellLink3.IconLocation = "shell32.dll,21"
oShellLink3.Save

' Create safe startup shortcut
Set oShellLink4 = WshShell.CreateShortcut(strDesktop & "\STAR Analysis System (Safe).lnk")
oShellLink4.TargetPath = strCurrentDir & "\start_safe.bat"
oShellLink4.WorkingDirectory = strCurrentDir
oShellLink4.Description = "STAR Analysis System - Safe Startup with Error Handling"
oShellLink4.IconLocation = "shell32.dll,21"
oShellLink4.Save

MsgBox "Created 4 desktop shortcuts:" & vbCrLf & vbCrLf & _
       "1. STAR Analysis System (Debug) - Shows detailed startup info" & vbCrLf & _
       "2. STAR Analysis System (Silent) - Creates debug log" & vbCrLf & _
       "3. STAR Analysis System (Direct) - Direct Python execution" & vbCrLf & _
       "4. STAR Analysis System (Safe) - Safe startup with error handling" & vbCrLf & vbCrLf & _
       "Try the Safe version first for best compatibility!", _
       vbInformation, "Shortcuts Created"