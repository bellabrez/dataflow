@echo off

:: for naming log files
set CUR_HH=%time:~0,2%
if %CUR_HH% lss 10 (set CUR_HH=0%time:~1,1%)
set CUR_NN=%time:~3,2%
set CUR_SS=%time:~6,2%
set CUR_MS=%time:~9,2%
set SUBFILENAME=%CUR_YYYY%%CUR_MM%%CUR_DD%-%CUR_HH%%CUR_NN%%CUR_SS%
:: https://tecadmin.net/create-filename-with-datetime-windows-batch-script/

>"logs\log_%SUBFILENAME%.txt" (
:: https://stackoverflow.com/questions/20484151/redirecting-output-from-within-batch-file

:: check if there are flagged files to transfer, and transfer if so
echo Checking for Bruker files to transfer.
"C:\Users\User\AppData\Local\Programs\Python\Python37\python.exe" "C:\Users\User\projects\dataflow\dataflow\bruker_transfer.py"
echo Done checking Bruker for files to transfer.

:: check if files were transfered by python ftp
set /p TRANSFERED_FILES=<"batch_communicate\found_files.txt"
if "%TRANSFERED_FILES%"=="True" (goto process_files)
if "%TRANSFERED_FILES%"=="False" (goto no_files_transfered)

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
echo No new files. terminating.
exit
)