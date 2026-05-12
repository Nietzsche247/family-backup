# SP-OLLAMA-START-001 — Ollama Autostart + Watchdog Durability

## Scenario ID
SP-OLLAMA-START-001

## Environment
Host: Omni-AlienWare2025
Binding target: 127.0.0.1:11434
Watchdog: Scheduled Tasks (OnBoot + EveryMinute)

## Preconditions
C:\Ollama\scripts\ollama-watchdog.ps1 exists
Scheduled tasks exist:
- OllamaWatchdog-OnBoot
- OllamaWatchdog-EveryMinute

## Steps

1) Confirm tasks exist
- Command:
  - schtasks /Query /TN "OllamaWatchdog-OnBoot" /FO LIST
  - schtasks /Query /TN "OllamaWatchdog-EveryMinute" /V /FO LIST
- Expected: both present, run as SYSTEM, highest privileges

2) Confirm Ollama healthy
- Command: `curl http://127.0.0.1:11434/api/tags`
- Expected: HTTP 200 + JSON

3) Reboot durability test
- Action: restart machine
- After boot, run:
  - netstat -ano | findstr :11434
  - `curl http://127.0.0.1:11434/api/tags`
- Expected: listener present + API healthy without manual start

4) Crash/restart test
- Action: kill owning PID of port 11434:
  - netstat -ano | findstr :11434 → get PID
  - taskkill /PID <PID> /F
- Expected: within 1 minute watchdog restores service
- Verify:
  - `curl http://127.0.0.1:11434/api/tags`

5) Binding security check
- Command:
  - Get-NetTCPConnection -State Listen -LocalPort 11434 | Format-List LocalAddress,LocalPort,OwningProcess
- Expected: LocalAddress is 127.0.0.1 (not 0.0.0.0 / ::)

## Evidence to capture
- Task query outputs
- netstat / Get-NetTCPConnection outputs
- curl outputs (or response hashes)
- Watchdog log: C:\Ollama\logs\ollama-watchdog.log

## Result
PASS only if all steps have evidence and binding is localhost-only.
Otherwise: INCONCLUSIVE or FAIL.

## Ledger pointer
(TBD by registrar after execution)
