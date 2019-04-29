@echo off
echo ripper watcher opened
:loop
echo starter ripper watcher loop
timeout /t 5
:: check if ripper is finished converting files
"C:\Users\User\AppData\Local\Programs\Python\Python37\python.exe" "C:\Users\User\projects\dataflow\scripts\check_for_raw.py"
set /p RIPPER_DONE=<ripper_done.txt
if "%RIPPER_DONE%"=="True" (goto kill_ripper)
if "%RIPPER_DONE%"=="False" (goto loop)

:kill_ripper
taskkill /IM "Image-Block Ripping Utility.exe"
exit