@echo off
REM ============================================================
REM  aristotle-ngrok-task.cmd
REM  Wrapper invoked by the Windows Scheduled Task
REM  "Aristotle Ngrok" at user logon.
REM
REM  - Kills any pre-existing ngrok.exe (avoids dual tunnels).
REM  - Waits for the gateway to be reachable on :18792 before
REM    starting the tunnel (so the first request after logon
REM    doesn't hit a 502).
REM  - Launches ngrok in the foreground so the Scheduled Task
REM    can restart it on crash.
REM
REM  Log: C:\tmp\clawdbot-aristotle\task-ngrok.log
REM ============================================================

set "LOG=C:\tmp\clawdbot-aristotle\task-ngrok.log"
set "NGROK_DOMAIN=uneffective-unprepossessingly-september.ngrok-free.dev"
set "GATEWAY_PORT=18792"

if not exist "C:\tmp\clawdbot-aristotle" mkdir "C:\tmp\clawdbot-aristotle" >nul 2>&1

echo. >> "%LOG%"
echo [%date% %time%] === aristotle-ngrok-task starting === >> "%LOG%"

REM --- Kill existing ngrok ---
tasklist /FI "IMAGENAME eq ngrok.exe" 2>nul | find /I "ngrok.exe" >nul
if not errorlevel 1 (
    echo [%date% %time%] stopping existing ngrok >> "%LOG%"
    taskkill /IM ngrok.exe /F >> "%LOG%" 2>&1
    timeout /t 2 /nobreak >nul
)

REM --- Wait up to 120s for gateway to be listening on :18792 ---
set _wait=0
:waitloop
netstat -ano | findstr ":%GATEWAY_PORT%" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 goto gateway_ready
set /a _wait+=1
if %_wait% GEQ 120 (
    echo [%date% %time%] WARN: gateway not listening on :%GATEWAY_PORT% after 120s, launching ngrok anyway >> "%LOG%"
    goto launch
)
timeout /t 1 /nobreak >nul
goto waitloop

:gateway_ready
echo [%date% %time%] gateway is listening on :%GATEWAY_PORT% (waited %_wait%s) >> "%LOG%"

:launch
echo [%date% %time%] launching ngrok tunnel %NGROK_DOMAIN% -^> :%GATEWAY_PORT% >> "%LOG%"
ngrok http %GATEWAY_PORT% --url %NGROK_DOMAIN% --log stdout >> "%LOG%" 2>&1

echo [%date% %time%] ngrok exited with code %errorlevel% >> "%LOG%"
exit /b %errorlevel%
