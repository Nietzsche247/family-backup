---
name: agent-recovery
description: Mutual agent recovery for the Bravo Team multi-agent system. Use when any agent (Aristotle, Plato, or future agents) is unresponsive, needs health checks, or requires restart. Covers local recovery (gateway/ngrok/tunnel), remote recovery via SSH, health diagnostics, and config backup/restore. Triggers on phrases like "fix Plato", "Aristotle is down", "recover", "health check", "restart gateway", or any mention of agent infrastructure being broken.
---

# Agent Recovery Skill

Bidirectional recovery system for the Bravo Team agent network. Any agent can diagnose and recover any other agent — or itself.

## Agent Registry

| Agent | Host | LAN IP | Gateway Port | SSH User | Recovery Script |
|-------|------|--------|-------------|----------|-----------------|
| Aristotle | Omni-AlienWare2025 | 10.0.0.49 | 18792 | aaron | `C:\Users\aaron\clawd-shared\aristotle_recover.py` |
| Plato | NIETZSCHE2025 | 10.0.0.50 | 18789 | Aaron | `C:\Users\Aaron\clawd-shared\plato_recover.py` |

For full architecture details, read `references/aristotle-architecture.md` or `references/plato-architecture.md`.

## Quick Reference: "Fix X"

### Aristotle fixing Plato
```powershell
# Diagnose
ssh -i C:\Users\aaron\.ssh\plato_recovery_key -o BatchMode=yes Aaron@10.0.0.50 "C:\Users\Aaron\AppData\Local\Programs\Python\Python312\python.exe C:\Users\Aaron\clawd-shared\plato_recover.py --check --json"

# Soft fix (restart only broken parts)
ssh -i C:\Users\aaron\.ssh\plato_recovery_key -o BatchMode=yes Aaron@10.0.0.50 "C:\Users\Aaron\AppData\Local\Programs\Python\Python312\python.exe C:\Users\Aaron\clawd-shared\plato_recover.py --soft --json"

# Full hammer
ssh -i C:\Users\aaron\.ssh\plato_recovery_key -o BatchMode=yes Aaron@10.0.0.50 "C:\Users\Aaron\AppData\Local\Programs\Python\Python312\python.exe C:\Users\Aaron\clawd-shared\plato_recover.py --json"
```

### Plato fixing Aristotle
```powershell
# Diagnose
ssh -i C:\Users\Aaron\.ssh\plato_to_alienware_key -o BatchMode=yes aaron@10.0.0.49 "C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe C:\Users\aaron\clawd-shared\aristotle_recover.py --check --json"

# Soft fix
ssh -i C:\Users\Aaron\.ssh\plato_to_alienware_key -o BatchMode=yes aaron@10.0.0.49 "C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe C:\Users\aaron\clawd-shared\aristotle_recover.py --soft --json"

# Full hammer
ssh -i C:\Users\Aaron\.ssh\plato_to_alienware_key -o BatchMode=yes aaron@10.0.0.49 "C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe C:\Users\aaron\clawd-shared\aristotle_recover.py --json"
```

## JSON Output Format

Both scripts return structured JSON with `--json`:
```json
{
  "status": "healthy|degraded|down",
  "gateway": {"port_listening": true, "pid": 357644, "http_ok": true, "http_status": 200, "supervisors": 1},
  "ngrok": {"tunnel_registered": true, "urls": ["https://..."], "public_probe_ok": false, "public_skip_reason": "loopback"},
  "action_taken": "none|check|soft_restart|full_recovery",
  "timestamp": "2026-05-08T15:49:53-07:00"
}
```

**Interpreting results:**
- `status: healthy` → all good, report to Aaron
- `status: degraded` + `public_skip_reason: loopback` → NAT hairpin, NOT a real outage
- `status: degraded` (other) → partial recovery, report which component is down
- `status: down` → full recovery failed, escalate to Aaron with log tails

## Recovery Procedures

### Self-Recovery (local, no SSH)
```
python {recover_script} --check --json     # diagnose only
python {recover_script} --soft             # restart broken parts
python {recover_script}                    # full hammer
```

### Remote Recovery Decision Tree
```
Agent unresponsive?
├─ Probe HTTP on LAN IP (curl.exe -s --connect-timeout 10 http://{IP}:{PORT}/)
│  ├─ Responds → not down, check channel/tunnel layer
│  └─ No response → SSH in, run recovery
│     ├─ --soft --json first (5-30s, preserves healthy parts)
│     │  ├─ status: healthy → Done
│     │  ├─ status: degraded → Try full hammer
│     │  └─ status: down → Escalate to Aaron
│     └─ Cannot SSH → Escalate to Aaron (physical access needed)
```

## Critical Gotchas (learned the hard way)

### Python PATH in SSH sessions
Windows Store `python.exe` stub fails over SSH. Always use full path:
- **AlienWare:** `C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe`
- **Nietzsche:** `C:\Users\Aaron\AppData\Local\Programs\Python\Python312\python.exe`

### NAT loopback / TLS hairpin
Probing your own ngrok URL from the same network fails (SSL errors). This is NOT proof the tunnel is broken. The scripts handle this correctly with `public_skip_reason: "loopback"`. Don't treat it as an outage.

### Windows OpenSSH authorized_keys for admin users
- **AlienWare:** sshd_config has `Match Group administrators` → reads `C:\ProgramData\ssh\administrators_authorized_keys`
- **Nietzsche:** sshd_config does NOT have this block → reads `C:\Users\Aaron\.ssh\authorized_keys`
- If adding keys, check which file sshd actually reads: `Select-String -Path "C:\ProgramData\ssh\sshd_config" -Pattern "Match|AuthorizedKeysFile|administrators"`
- The `administrators_authorized_keys` file MUST have restrictive ACLs: only SYSTEM + Administrators. Fix with: `icacls $path /inheritance:r /grant "NT AUTHORITY\SYSTEM:(F)" /grant "BUILTIN\Administrators:(F)"`
- PowerShell's `Add-Content` can create files WITHOUT trailing newlines, concatenating keys on one line. Always verify with `Get-Content $path | ForEach-Object { "LINE: $_" }`

### Plato's ngrok URL is dynamic
Changes on every restart. If ngrok restarts, Google Chat webhook breaks until config is updated. Aristotle's URL is static (reserved domain). The recovery script warns about URL changes but cannot auto-update the webhook config.

### No supervisor loop on Plato
Aristotle has `gateway-resilient.cmd` (infinite restart). Plato's gateway.cmd runs node once — if it crashes, the scheduled task must be re-triggered. Recovery script handles this.

## SSH Key Locations

| Key | Location | Purpose |
|-----|----------|---------|
| Aristotle → Plato (private) | `C:\Users\aaron\.ssh\plato_recovery_key` | SSH into Nietzsche |
| Aristotle → Plato (public) | Installed on Nietzsche `~/.ssh/authorized_keys` | Auth |
| Plato → Aristotle (private) | `C:\Users\Aaron\.ssh\plato_to_alienware_key` | SSH into AlienWare |
| Plato → Aristotle (public) | Installed on AlienWare `C:\ProgramData\ssh\administrators_authorized_keys` | Auth |

## Adding New Agents

1. Write a recovery script — copy `aristotle_recover.py` as template, update CONFIG section
2. Write an architecture reference — document process tree, ports, files, failure modes
3. Set up SSH — install sshd, check which authorized_keys file sshd reads, install recovery keys
4. Set up auto-restart — Scheduled Tasks with periodic triggers (AtLogon + every 5 min)
5. Test `--check --json` locally AND remotely via SSH
6. Update this skill — add to registry table, add reference file

## Companion Files

- `references/aristotle-architecture.md` — full Aristotle architecture
- `references/plato-architecture.md` — full Plato architecture
- Fleet knowledge base: `C:\Users\aaron\clawd-shared\NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md`
