@echo off
echo Running PCU Folder Search and Zip Script (ENHANCED Long Path Support)
echo ===================================================================
echo This script searches for PCU folders and zips either:
echo - "EOR Submittals-Responses" folders
echo - "Submittals and Responses" folders
echo.

set "SEARCH_PATH=U:\UTIL_ENG\Project Files- Private Development\Projects - Private Dev Under Review"
set "CSV_FILE=C:\Users\cruskowski\Desktop\pcu only not zipped 3rd time.csv"
set "OUTPUT_PATH=c:\temp\zipped folders"

echo Search Path: %SEARCH_PATH%
echo CSV File: %CSV_FILE%
echo Output Path: %OUTPUT_PATH%
echo.

powershell.exe -ExecutionPolicy Bypass -File "c:\temp\folder_search_and_zip.ps1" -SearchPath "%SEARCH_PATH%" -CsvFilePath "%CSV_FILE%" -OutputPath "%OUTPUT_PATH%"

echo.
echo Script execution completed.
pause
