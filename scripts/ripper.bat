@echo off
echo Started ripper.
set FOLDER_NAME=%1
echo Ripping from folder %FOLDER_NAME%.
"C:\Program Files\Prairie\Prairie View\Utilities\Image-Block Ripping Utility.exe" -isf -arfwsf "%FOLDER_NAME%" -cnv
echo Finished ripping.