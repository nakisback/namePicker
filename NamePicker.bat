@echo off
REM Double-click this file to run namePicker.
REM No need to open a command prompt or type anything yourself.

setlocal
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python main.py
    goto :done
)

where py >nul 2>nul
if %errorlevel%==0 (
    py main.py
    goto :done
)

echo.
echo Could not find Python on this computer.
echo Install it from https://python.org (check "Add Python to PATH" during
echo setup), then double-click this file again.
pause
exit /b 1

:done
echo.
pause
