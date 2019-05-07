@echo off
:loop
"C:\Users\User\AppData\Local\Programs\Python\Python37\python.exe" "C:\Users\User\projects\dataflow\scripts\main.py"
"C:\Users\User\AppData\Local\Programs\Python\Python37\python.exe" "C:\Users\User\projects\dataflow\scripts\final_email.py"
::echo Sleeping for 5 min
::TIMEOUT /T 300
::goto loop