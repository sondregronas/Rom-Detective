@echo off
::===============================================================================================
:: create_shortcut() might require admin privileges in order to create symlinks ROMs
:: Limitation: Only works when destination folder supports symlinks (NTFS or UDF)
::===============================================================================================
if not "%1"=="am_admin" (
    powershell -Command "Start-Process -Verb RunAs -FilePath '%0' -ArgumentList 'am_admin'"
    exit /b
)
::===============================================================================================
:: Remove echo and replace the DRIVELETTER from the following if you need to use a network share
echo net use S: \\nas\share /persistent:no
::===============================================================================================

python "%~dp0\src\main.py"
pause
