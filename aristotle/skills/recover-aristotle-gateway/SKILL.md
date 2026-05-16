---
name: recover-aristotle-gateway
description: "7-step recovery procedure for Aristotle's wedged gateway (Failure Mode 8). Use when gateway is cycling, wedged, or unresponsive on port 18792."
---

# Recover Aristotle Gateway

## When to Use
- Port 18792 LISTENING but HTTP hangs/timeout
- Gateway cycling (~20s PID rotation)
- Sub-agents unreachable

## 7-Step Procedure

1. **Disable auto-respawn:** `Disable-ScheduledTask -TaskName "Aristotle Gateway"`
2. **Kill supervisor/wrapper processes:** Target gateway-resilient, aristotle-gateway-task, gateway.cmd via Get-CimInstance
3. **Kill port holder:** `Stop-Process` on the PID owning port 18792
4. **Wait 30s** — verify port stays empty
5. **Clear jiti cache:** `Remove-Item "$env:TEMP\jiti\memos*" -Force`
6. **Re-enable + start:** `Enable-ScheduledTask` then `Start-ScheduledTask`
7. **Verify:** Wait 45s, check port 18792 LISTENING + HTTP 200

## Key Learnings
- L30: dist/ edits need full process restart
- L31: Gateway loads index.ts via jiti. Delete jiti cache after edits.
- L41: Supervisor patched to kill stale port holders (2026-05-13)
- L43: MemOS rebuilds = wedge risk. Restart + watch 30 min.
