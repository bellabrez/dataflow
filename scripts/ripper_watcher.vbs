Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:/Users/User/projects/dataflow/scripts/ripper_watcher.bat" & Chr(34), 0
Set WshShell = Nothing