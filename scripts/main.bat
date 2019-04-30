@echo off
:: check if there are flagged files to transfer
echo Checking for files to transfer.
"C:\Users\User\AppData\Local\Programs\Python\Python37\python.exe" "C:\Users\User\projects\dataflow\dataflow\check_for_bruker_transfer.py"
echo Done checking for files to transfer.

:: check if files were transfered by python ftp
set /p FOUND_FILES=<"batch_communicate\found_files.txt"
if "%FOUND_FILES%"=="True" (goto process_files)
if "%FOUND_FILES%"=="False" (goto no_files_transfered)

:: if python transfered files, continue to process them
:process_files
echo Processing Files.
set /p FOLDER_NAME=<"batch_communicate\folder_name.txt"

:: vbs file allows this window to run in the background without popping up
start ripper_watcher.vbs

echo Started ripper.
echo Ripping from folder %FOLDER_NAME%.
"C:\Program Files\Prairie 5.4.64.600\Prairie View\Utilities\Image-Block Ripping Utility.exe" -isf -arfwsf "%FOLDER_NAME%" -cnv
echo Finished ripping.

echo Starting tiff to nii conversion.
"C:\Users\User\AppData\Local\Programs\Python\Python37\python.exe" "C:\Users\User\projects\dataflow\dataflow\tiff_to_nii.py" %FOLDER_NAME%
echo Finished tiff to nii conversion.

echo Moving to Oak.
"C:\Users\User\AppData\Local\Programs\Python\Python37\python.exe" "C:\Users\User\projects\dataflow\dataflow\transfer_to_oak.py" %FOLDER_NAME%
echo Done moving to Oak.
echo All complete.
pause

:: if no files were transfered, exit
:no_files_transfered
echo Batch found no files. terminating.
exit


::START /WAIT Install.exe
::https://stackoverflow.com/questions/13257571/call-command-vs-start-with-wait-option
echo done
pause