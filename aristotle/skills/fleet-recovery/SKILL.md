---
name: fleet-recovery
description: Bidirectional SSH recovery for the AI agent fleet. Use when asked to check on, diagnose, or recover another agent (Aristotle, Plato, Empiricus). Covers health checks, full/soft recovery, and remote diagnostics via SSH. Triggers on phrases like "fix Aristotle", "fix Plato", "check on Aristotle", "is Aristotle alive", "recover the fleet", "agent down", or any request to restart/diagnose another agent's gateway.
---

# Fleet Recovery

Bidirectional SSH-based recovery for the AI agent fleet. Any agent can diagnose and recover any other agent remotely.

## Fleet Map

| Agent | Machine | LAN IP | Tailscale IP | SSH User | Gateway Port | Recovery Script |
|-------|---------|--------|-------------|----------|-------------|-----------------|
| Aristotle | Omni-AlienWare2025 | 10.0.0.49 | 100.108.47.36 | aaron | 18792 | `C:\Users\aaron\clawd-shared\aristotle_recover.py` |
| Plato | NIETZSCHE2025 | 10.0.0.50 | 100.73.106.82 | Aaron | 18789 | `C:\Users\Aaron\clawd\scripts\plato_recover.py` |

**Python paths (SSH sessions don't inherit full PATH):**
- AlienWare: `C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe`
- NIETZSCHE2025: `python` (on PATH)

## SSH Keys

| From | To | Key |
|------|----|-----|
| Plato → AlienWare | aaron@10.0.0.49 | `C:\Users\Aaron\.ssh\plato_to_alienware_key` |
| Aristotle → Plato | Aaron@10.0.0.50 | `C:\Users\aaron\.ssh\plato_recovery_key` |

## Quick Reference

### Health Check (no changes, safe to run anytime)

```powershell
# Plato checking Aristotle:
ssh -i C:\Users\Aaron\.ssh\plato_to_alienware_key -o StrictHostKeyChecking=no -o ConnectTimeout=15 aaron@10.0.0.49 "C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe C:\Users\aaron\clawd-shared\aristotle_recover.py --check --json"

# Aristotle checking Plato:
ssh -i C:\Users\aaron\.ssh\plato_recovery_key -o StrictHostKeyChecking=no -o ConnectTimeout=15 Aaron@10.0.0.50 "python C:\Users\Aaron\clawd\scripts\plato_recover.py --check --json"
```

### Soft Recovery (restart only broken pieces)

Append `--soft` instead of `--check`.

### Full Recovery (teardown + rebuild)

Run without `--check` or `--soft` (default mode).

### Verbose Human-Readable Output

Add `-v` and remove `--json`.

## JSON Output Schema

All recovery scripts return this structure with `--json`:

```json
{
  "status": "healthy|degraded|down",
  "gateway": {
    "port": true,
    "http": true,
    "pid": 12345
  },
  "ngrok": {
    "process": true,
    "tunnel": true,
    "url": "https://...",
    "url_changed": false
  },
  "action_taken": "none|soft_restart|full_recovery",
  "timestamp": "ISO-8601"
}
```

## Decision Logic

1. Run `--check --json` first. Parse JSON.
2. If `status == "healthy"` → report all green, done.
3. If `status == "degraded"` → try `--soft` first. If still degraded → full recovery.
4. If `status == "down"` → full recovery immediately.
5. After recovery, run `--check --json` again to confirm.
6. Report result to Aaron. If still down after full recovery, escalate — likely needs physical access or provider-level issue.

## Connectivity Fallbacks

1. **LAN IP first** (10.0.0.x) — fastest, most reliable on same network
2. **Tailscale IP** (100.x.x.x) — works across networks, may have NAT issues
3. **If SSH fails on both** — agent is truly unreachable. Check:
   - Is the machine powered on? (ping the IP)
   - Is sshd running? (port 22 open?)
   - VPN/firewall interference? (ProtonVPN on Plato can affect routing)
   - Escalate to Aaron for physical access

## Known Quirks

- **AlienWare Python:** Must use full path `C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe` — the WindowsApps stub fails in SSH context.
- **Plato ngrok URL is dynamic:** Changes on ngrok restart. Script detects this and sets `ngrok.url_changed: true` in JSON. Google Chat webhook config needs updating if URL changes.
- **Aristotle ngrok URL is static:** Reserved domain `uneffective-unprepossessingly-september.ngrok-free.dev`.
- **E2E tunnel probe from AlienWare:** May show SSL NAT loopback error — this is expected and non-critical. The script marks it `public_skip_reason: "loopback"`.
- **Plato has no supervisor loop:** If gateway crashes, it stays down until the scheduled task is re-triggered. Aristotle has `gateway-resilient.cmd` with infinite restart.

## Architecture References

For deep dives into each agent's full architecture, failure modes, and recovery procedures:
- **Aristotle:** See `references/aristotle-architecture.md`
- **Plato:** See `references/plato-architecture.md`
