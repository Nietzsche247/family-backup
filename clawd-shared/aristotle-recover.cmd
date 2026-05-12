@echo off
REM ============================================================
REM  aristotle-recover.cmd
REM  Launcher for aristotle_recover.py
REM
REM  Usage:
REM    aristotle-recover.cmd            full recovery
REM    aristotle-recover.cmd --check    diagnose only
REM    aristotle-recover.cmd --soft     surgical (fix only what's broken)
REM    aristotle-recover.cmd -v         verbose
REM ============================================================

setlocal

REM Find python.exe — try py launcher, then explicit Python 3.12, then PATH.
set "PYEXE="
where py >nul 2>&1 && set "PYEXE=py"
if "%PYEXE%"=="" if exist "C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe" set "PYEXE=C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe"
if "%PYEXE%"=="" if exist "C:\Users\aaron\AppData\Local\Programs\Python\Python311\python.exe" set "PYEXE=C:\Users\aaron\AppData\Local\Programs\Python\Python311\python.exe"
if "%PYEXE%"=="" where python >nul 2>&1 && set "PYEXE=python"

if "%PYEXE%"=="" (
    echo ERROR: could not find a Python interpreter.
    echo Install Python 3.10+ or set PYEXE manually in this script.
    pause
    exit /b 127
)

"%PYEXE%" "C:\Users\aaron\clawd-shared\aristotle_recover.py" %*
set _rc=%errorlevel%

REM Pause only on error or when launched by double-click (no console parent).
if not "%_rc%"=="0" pause
exit /b %_rc%
