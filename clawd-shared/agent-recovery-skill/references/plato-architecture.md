# Plato Architecture Reference

## Identity
- Agent: Plato (Rationalist / Builder)
- Host: NIETZSCHE2025 (Windows 11, x64)
- Clawdbot version: 2026.1.24-3
- Primary model: anthropic/claude-opus-4-6
- Fallback cascade: Opus 4.5 -> Sonnet 4.5 -> Sonnet 4
- User: Aaron (standard, not admin-elevated)

## Network
| Interface | IP |
|-----------|-----|
| Wi-Fi (LAN) | 10.0.0.50 (prefer this) |
| Tailscale | 100.73.106.82 |
| ProtonVPN | 10.2.0.2 (may interfere with routing) |

## Process Tree (healthy state)
```
Scheduled Task "Clawdbot Gateway" (AtLogon / manual)
  -> gateway.cmd (wrapper, sets env vars)
       -> node.exe entry.js gateway --port 18789
            -> Listening on ws://127.0.0.1:18789

ngrok.exe http 18789 (MANUAL process, NOT task-managed)
  -> Tunnel URL is DYNAMIC (changes every restart!)
  -> Local API: http://127.0.0.1:4040/api/tunnels
```

**KEY DIFFERENCES FROM ARISTOTLE:**
- NO supervisor loop (gateway.cmd runs node once, no infinite restart)
- NO ngrok scheduled task (started manually)
- Ngrok URL is DYNAMIC (not reserved) -- restart = broken webhook
- NO PM2

## Port Map
| Port | Service |
|------|---------|
| 18789 | Plato Gateway |
| 4040 | Ngrok local API |
| 22 | OpenSSH Server |
| 12345 | Ollama (when active) |

## File Locations

### Config
- Gateway config: `C:\Users\Aaron\.clawdbot\clawdbot.json`
- Config backups: `C:\Users\Aaron\.clawdbot\clawdbot.json.bak` (+ .bak.1 through .bak.4)
- Gateway launcher: `C:\Users\Aaron\.clawdbot\gateway.cmd`
- Workspace: `C:\Users\Aaron\clawd\`
- Shared: `C:\Users\Aaron\clawd-shared\`

### Logs
- Gateway internal: `C:\tmp\clawdbot\clawdbot-YYYY-MM-DD.log`

### Memory
- MEMORY.md: `C:\Users\Aaron\clawd\MEMORY.md`
- Daily notes: `C:\Users\Aaron\clawd\memory\YYYY-MM-DD.md`
- SESSION-STATE.md: `C:\Users\Aaron\clawd\SESSION-STATE.md`
- Inbox: `C:\Users\Aaron\clawd\inbox\`

## SSH Access
- sshd: Running, Automatic start
- Port: 22
- User: `Aaron`
- LAN: `ssh Aaron@10.0.0.50`
- Tailscale: `ssh Aaron@100.73.106.82`
- Pubkey + password auth both available

## Scheduled Tasks
| Task | Trigger | Notes |
|------|---------|-------|
| Clawdbot Gateway | AtLogon / manual | Single-run (no auto-restart on crash) |

No heartbeat tasks, no ngrok task.

## Channel Config
- Google Chat webhook: `/google/events`
- Public URL: Dynamic ngrok URL (check `http://127.0.0.1:4040/api/tunnels` for current)
- If ngrok restarts, webhook URL changes and config must be updated

## Known Failure Modes
1. **Gateway crash** -> Re-trigger: `schtasks /run /TN "Clawdbot Gateway"` (may need `/end` first)
2. **Duplicate nodes** -> Kill all, restart task
3. **Ngrok down** -> `Stop-Process -Name ngrok; Start-Process ngrok -ArgumentList "http 18789"`
4. **Hung gateway** -> Kill node PID holding port, retrigger task
5. **Config corruption** -> Restore from `.clawdbot\clawdbot.json.bak`
6. **ProtonVPN interference** -> Can't fix remotely, Aaron must toggle
7. **All providers rate-limited** -> Wait, check billing

## Recovery Script
- Location (on Plato): `C:\Users\Aaron\clawd-shared\plato_recover.py`
- Location (on AlienWare): `C:\Users\aaron\clawd-shared\plato_recover.py`
- Remote: `ssh Aaron@10.0.0.50 "python C:\Users\Aaron\clawd-shared\plato_recover.py --soft --json"`

## Verification Commands
```powershell
netstat -ano | findstr ":18789" | findstr "LISTENING"
curl.exe -s -o nul -w "%{http_code}" http://127.0.0.1:18789/
curl.exe -s http://127.0.0.1:4040/api/tunnels
schtasks /query /TN "Clawdbot Gateway" /FO LIST
python C:\Users\Aaron\clawd-shared\plato_recover.py --check -v --json
```
