@echo off
REM ============================================================
REM  aristotle-gateway-task.cmd
REM  Wrapper invoked by the Windows Scheduled Task
REM  "Aristotle Gateway" at user logon.
REM
REM  Defense in depth:
REM    1) Refuse to start over an unknown/stale port holder.
REM    2) Launch gateway-resilient.cmd in the foreground so the
REM       Scheduled Task can monitor and restart it on crash.
REM
REM  Log: C:\tmp\clawdbot-aristotle\task-gateway.log
REM ============================================================

set "LOG=C:\tmp\clawdbot-aristotle\task-gateway.log"
if not exist "C:\tmp\clawdbot-aristotle" mkdir "C:\tmp\clawdbot-aristotle" >nul 2>&1

echo. >> "%LOG%"
echo [%date% %time%] === aristotle-gateway-task starting === >> "%LOG%"

REM --- F2: Early-return if gateway already healthy (L45) ---
REM Use the same HTTP probe family as the reviewed recovery verifier.
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -NonInteractive -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:18792/api/status' -TimeoutSec 10; if ($r.StatusCode -eq 200) { exit 0 } } catch { }; exit 1"
if not errorlevel 1 (
    echo [%date% %time%] Gateway already healthy ^(HTTP 200^). Skipping wrapper. >> "%LOG%"
    exit /b 0
)

REM --- Refuse an ambiguous start; recovery code owns verified cleanup. ---
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":18792" ^| findstr "LISTENING"') do (
    echo [%date% %time%] REFUSING_START: port 18792 is held by PID %%a and health check failed. >> "%LOG%"
    exit /b 1
)

echo [%date% %time%] launching gateway-resilient.cmd >> "%LOG%"
cd /d C:\Users\aaron\.clawdbot-aristotle
call gateway-resilient.cmd >> "%LOG%" 2>&1

echo [%date% %time%] gateway-resilient.cmd exited with code %errorlevel% >> "%LOG%"
exit /b %errorlevel%
