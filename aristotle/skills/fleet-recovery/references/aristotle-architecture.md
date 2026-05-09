# Aristotle Architecture Reference
# Last updated: 2026-05-08 (post v2 recovery script)

## Identity
- Agent: Aristotle (CEO / Strategic Coordinator)
- Host: Omni-AlienWare2025 (Windows 11, x64)
- Clawdbot version: 2026.1.24-3
- Primary model: anthropic/claude-opus-4-6
- Fallback cascade: Sonnet 4.6 -> GPT-5.2 -> Sonnet 4

## Process Tree (healthy state)
```
Scheduled Task "Aristotle Gateway" (AtLogon + every 5min)
  -> aristotle-gateway-task.cmd (wrapper, kills zombies first)
       -> gateway-resilient.cmd (supervisor, infinite restart loop)
            -> node.exe entry.js gateway (the actual Clawdbot process)
                 -> Listening on ws://127.0.0.1:18792

Scheduled Task "Aristotle Ngrok" (AtLogon+15s + every 5min)
  -> aristotle-ngrok-task.cmd (wrapper, waits up to 120s for gateway)
       -> ngrok.exe http 18792 (tunnel)
            -> Tunnel: https://uneffective-unprepossessingly-september.ngrok-free.dev
            -> Local API: http://127.0.0.1:4040/api/tunnels
```

## Health Checks (ordered by severity)

| # | Check | Command | Healthy Response |
|---|-------|---------|-----------------|
| 1 | Port bound | `netstat -ano \| findstr ":18792" \| findstr "LISTENING"` | One PID |
| 2 | HTTP responds | `curl.exe -s http://127.0.0.1:18792/` | Any 200 response |
| 3 | Ngrok local API | `curl.exe -s http://127.0.0.1:4040/api/tunnels` | JSON with tunnel URL |
| 4 | Public URL | `curl.exe -s https://uneffective-unprepossessingly-september.ngrok-free.dev/` | Reaches gateway |
| 5 | Google Chat | Messages arrive and get responses | End-to-end |

## Port Map

| Port | Service |
|------|---------|
| 18792 | Aristotle Gateway (HTTP/WebSocket) |
| 4040 | Ngrok local API |
| 3001 | Comms Hub (PM2) |
| 3003 | NorthStar Ledger (PM2) |
| 11434 | Ollama (embeddings) |

## File Locations

### Config
- Gateway config: `C:\Users\aaron\.clawdbot-aristotle\clawdbot.json`
- Google Chat SA: `C:\Users\aaron\.clawdbot-aristotle\aristotle-philosopher-3d358ef817e9.json`
- Workspace: `C:\Users\aaron\clawd-aristotle\`
- Shared: `C:\Users\aaron\clawd-shared\`

### Recovery
- Script (v2): `C:\Users\aaron\clawd-shared\aristotle_recover.py`
- Launcher: `C:\Users\aaron\clawd-shared\aristotle-recover.cmd`
- Gateway wrapper: `C:\Users\aaron\clawd-shared\aristotle-gateway-task.cmd`
- Ngrok wrapper: `C:\Users\aaron\clawd-shared\aristotle-ngrok-task.cmd`
- Supervisor: `C:\Users\aaron\.clawdbot-aristotle\gateway-resilient.cmd`

### Logs
- Gateway task: `C:\tmp\clawdbot-aristotle\task-gateway.log`
- Ngrok task: `C:\tmp\clawdbot-aristotle\task-ngrok.log`
- Gateway internal: `C:\tmp\clawdbot\clawdbot-YYYY-MM-DD.log`

### Backups
- Config backups: `C:\Users\aaron\clawd-shared\backups\clawdbot-aristotle-YYYY-MM-DD.json`

## Scheduled Tasks

| Task | Triggers | MultipleInstances |
|------|----------|-------------------|
| Aristotle Gateway | AtLogon + every 5min | IgnoreNew |
| Aristotle Ngrok | AtLogon (15s delay) + every 5min | IgnoreNew |
| Aristotle Heartbeat - Daytime 30m | 08:00-20:00 every 30min | IgnoreNew |
| Aristotle Heartbeat - Night 120m | 20:00-08:00 every 120min | IgnoreNew |

## Channel Config
- Channel: Google Chat
- Webhook: `/google/events`
- Public URL: `https://uneffective-unprepossessingly-september.ngrok-free.dev/google/events`
- If ngrok is down, Aaron cannot reach Aristotle via Google Chat.

## Sub-Agents

| Agent | Primary Model | Role |
|-------|--------------|------|
| daedalus | GPT-5.4 | Senior Engineer |
| thales | Sonnet 4.6 | Systems & Ops |
| steelman | Grok 4.20 Exp | Devil's Advocate |
| researcher | Gemini 2.5 Pro | Research |
| sentinel | Grok 4 | Security |

## Cron Jobs

| Name | Schedule | Purpose |
|------|----------|---------|
| bridge-watchdog-15m | Every 4h | Infra health (public URL, cloudflared, hub, ledger, ollama) |
| self-healing-8am | Daily 8 AM | PM2 services, cloudflared, ollama |
| end-of-day-signal-fire | Daily 9 PM | Team reflection |
| researcher-daily-micro-scan | Daily 9 AM | AI/research news |
| daily-gdrive-backup | Daily 4:30 AM | Google Drive backup |
| state-md-staleness-check | Mon 10 AM | STATE.md freshness alert |

## Recovery Script v2 Features (all implemented)

The `aristotle_recover.py` (v2, 29KB) includes:
- HTTP health probe (not just port check) - catches hung gateways
- End-to-end tunnel verification via public URL
- Hung-gateway recovery (kills node PID, supervisor restarts)
- Config backup on successful recovery (daily snapshots)
- Structured JSON output (`--json`) with documented schema
- Log tailing on failure (last 20 lines of gateway + clawdbot logs)
- NAT loopback detection (`public_skip_reason: "loopback"`)
- Soft recovery mode (`--soft`) for surgical fixes

## Known Failure Modes

1. **Gateway crash** -> Auto-recovers via 5-min periodic task trigger
2. **Ngrok down** -> Auto-recovers via 5-min periodic task trigger
3. **Zombie supervisors** -> Full hammer kill + clean restart
4. **Hung gateway** (port bound, HTTP dead) -> v2 script kills node PID, supervisor restarts
5. **Config corruption** -> Restore from daily backup in `clawd-shared/backups/`
6. **All providers rate-limited** -> Wait; check billing/quotas
7. **Machine failure** -> SSH remote recovery from Plato or physical access

## SSH Access

- sshd: Running, Automatic start
- Port: 22
- User: `aaron`
- Key auth: `C:\ProgramData\ssh\administrators_authorized_keys` (Match Group administrators in sshd_config)
- Plato's key installed for remote recovery

## Verification Commands

```powershell
# Quick health check
netstat -ano | findstr ":18792" | findstr "LISTENING"
curl.exe -s -o nul -w "%{http_code}" http://127.0.0.1:18792/
curl.exe -s http://127.0.0.1:4040/api/tunnels
schtasks /query /TN "Aristotle Gateway" /FO LIST

# Full diagnostic (v2)
C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe C:\Users\aaron\clawd-shared\aristotle_recover.py --check -v --json
```
