@echo off
REM ============================================================
REM  aristotle-gateway-task.cmd
REM  Wrapper invoked by the Windows Scheduled Task
REM  "Aristotle Gateway" at user logon.
REM
REM  Defense in depth:
REM    1) Kill any pre-existing gateway-resilient.cmd supervisor
REM       (prevents the duplicate-supervisor crash-loop bug).
REM    2) Wait for port 18792 to clear.
REM    3) Launch gateway-resilient.cmd in the foreground so the
REM       Scheduled Task can monitor and restart it on crash.
REM
REM  Log: C:\tmp\clawdbot-aristotle\task-gateway.log
REM ============================================================

set "LOG=C:\tmp\clawdbot-aristotle\task-gateway.log"
if not exist "C:\tmp\clawdbot-aristotle" mkdir "C:\tmp\clawdbot-aristotle" >nul 2>&1

echo. >> "%LOG%"
echo [%date% %time%] === aristotle-gateway-task starting === >> "%LOG%"

REM --- F2: Early-return if gateway already healthy (L45) ---
REM Don't kill-and-relaunch a perfectly healthy gateway.
curl.exe -s -o NUL -w "%%{http_code}" --max-time 3 http://127.0.0.1:18792/api/status > "%TEMP%\arist_health.txt" 2>&1
set /p HEALTH=<"%TEMP%\arist_health.txt"
if "%HEALTH%"=="200" (
    echo [%date% %time%] Gateway already healthy ^(HTTP 200^). Skipping wrapper. >> "%LOG%"
    exit /b 0
)

REM --- 1) Kill any existing gateway-resilient supervisors ---
set _killed_any=0
for /f "tokens=2 delims=," %%p in ('tasklist /v /fo csv /nh ^| findstr /i "gateway-resilient"') do (
    set "spid=%%~p"
    setlocal enabledelayedexpansion
    echo [%date% %time%] killing existing supervisor PID !spid! >> "%LOG%"
    taskkill /PID !spid! /T /F >> "%LOG%" 2>&1
    endlocal
    set _killed_any=1
)

REM --- 2) Free port 18792 if anything is still on it ---
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":18792" ^| findstr "LISTENING"') do (
    echo [%date% %time%] killing port 18792 holder PID %%a >> "%LOG%"
    taskkill /PID %%a /F >> "%LOG%" 2>&1
    set _killed_any=1
)

REM Brief pause only if we actually killed something.
if "%_killed_any%"=="1" timeout /t 3 /nobreak >nul

echo [%date% %time%] launching gateway-resilient.cmd >> "%LOG%"
cd /d C:\Users\aaron\.clawdbot-aristotle
call gateway-resilient.cmd >> "%LOG%" 2>&1

echo [%date% %time%] gateway-resilient.cmd exited with code %errorlevel% >> "%LOG%"
exit /b %errorlevel%
