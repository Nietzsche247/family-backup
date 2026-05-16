---
name: probe-fleet-health
description: "Quick fleet health check across all agents. Checks gateway, Ledger, Comms Hub, remote agents, scheduled tasks."
---

# Probe Fleet Health

## Quick Checks
- **Gateway:** `netstat -ano | findstr "18792.*LISTENING"`
- **Ledger:** `curl.exe -s http://127.0.0.1:3003/events?limit=1`
- **Comms Hub:** `curl.exe -s http://127.0.0.1:3001/api/status`
- **Plato:** `curl.exe -s --connect-timeout 5 http://10.0.0.50:18789/status`
- **Tasks:** `Get-ScheduledTask -TaskName "Aristotle*" | Select-Object TaskName,State`

## Report Format
```
Aristotle: [✅|❌] pid=X port=18792
Ledger:    [✅|❌] events=N
CommsHub:  [✅|❌] bridge=bravo-team
Plato:     [✅|❌] last_commit=HASH
Empiricus: [✅|❌] last_sync=TIMESTAMP
```

## Escalation
- Gateway down → `recover-aristotle-gateway` skill
- Plato unreachable → SSH or notify Aaron
- Ledger down → `pm2 restart ledger` (elevated)
