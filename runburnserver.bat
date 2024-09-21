@echo off
:: Check if the script is running as administrator
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Requesting administrator privileges...
    :: Create a temporary VBScript to prompt for UAC elevation
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "cmd.exe", "/c cd /d %~dp0 ^& %~s0", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit
)

:: Change to the directory where the script is located
cd /d "%~dp0"

:: Run the Python script
python burnserver.py

:: Prevent the window from closing immediately
echo.
echo Script execution completed. Press any key to exit.
pause
