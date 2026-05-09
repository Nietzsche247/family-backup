# PLATO RECOVERY REFERENCE
# For: Aristotle, Empiricus, or any external agent performing recovery
# Last updated: 2026-05-08 by Plato
# Location: clawd-shared / shared file server

---

## IDENTITY

- **Agent:** Plato (Rationalist / Builder)
- **Host machine:** NIETZSCHE2025 (Windows 11 x64, build 10.0.26200)
- **Clawdbot version:** 2026.1.24-3
- **Primary model:** anthropic/claude-opus-4-6
- **Fallback cascade:** Opus 4.5 → Sonnet 4.5 → Sonnet 4
- **User:** Aaron (not admin-elevated, standard user context)

---

## NETWORK

| Interface | IP | Notes |
|-----------|-----|-------|
| Wi-Fi (LAN) | 10.0.0.50 | Primary — always prefer this |
| Tailscale | 100.73.106.82 | Backup — mesh VPN |
| ProtonVPN | 10.2.0.2 | VPN tunnel (may interfere with LAN routing) |

**Gateway port:** 18789
**Gateway token:** `ad8703220cdfa6fcf6a9589dec3100c90be32537bc47cb28`
**Ngrok tunnel:** `https://liny-tien-pleuritic.ngrok-free.dev` → localhost:18789
**Ngrok local API:** `http://127.0.0.1:4040/api/tunnels`

---

## ARCHITECTURE — What Must Be Running

### Process Tree (healthy state)
```
Scheduled Task "Clawdbot Gateway"
  └─ gateway.cmd (wrapper — sets env vars, launches node)
       └─ node.exe entry.js gateway --port 18789 (the actual Clawdbot process)
            └─ Listening on ws://127.0.0.1:18789

ngrok.exe http 18789 (separate process, NOT task-managed)
  └─ Tunnel: https://liny-tien-pleuritic.ngrok-free.dev
  └─ Local API: http://127.0.0.1:4040/api/tunnels
```

**⚠️ KEY DIFFERENCE FROM ARISTOTLE:** Plato does NOT have a supervisor/resilient loop. The scheduled task launches `gateway.cmd` directly, which runs `node.exe` once. If node crashes, the task must be re-triggered manually or by recovery script. There is no infinite restart loop.

**⚠️ NGROK:** Started manually (not via scheduled task). If ngrok dies, it must be restarted manually. The ngrok process (PID varies) runs independently.

### Health Checks (in order of severity)

| Check | Command | Healthy Response |
|-------|---------|-----------------|
| 1. Port bound | `netstat -ano \| findstr ":18789" \| findstr "LISTENING"` | One or two PIDs listening |
| 2. HTTP responds | `curl.exe -s http://127.0.0.1:18789/api/status` | Returns JSON or HTML (any 200) |
| 3. Ngrok tunnel | `curl.exe -s http://127.0.0.1:4040/api/tunnels` | JSON with tunnel URL |
| 4. Public URL | `curl.exe -s https://liny-tien-pleuritic.ngrok-free.dev/api/status` | Reaches through tunnel to gateway |

### Port Map

| Port | Service | Protocol |
|------|---------|----------|
| 18789 | Plato Gateway | HTTP/WebSocket |
| 4040 | Ngrok local API | HTTP |
| 12345 | Ollama (local LLM) | HTTP (may not be running) |
| 22 | OpenSSH Server | SSH |

---

## FILES — Where Everything Lives

### Config
- **Gateway config:** `C:\Users\Aaron\.clawdbot\clawdbot.json`
- **Config backups:** `C:\Users\Aaron\.clawdbot\clawdbot.json.bak` (+ .bak.1 through .bak.4)
- **Gateway launcher:** `C:\Users\Aaron\.clawdbot\gateway.cmd`
- **Workspace:** `C:\Users\Aaron\clawd\`
- **Shared workspace:** `C:\Users\Aaron\clawd-shared\`

### Logs
- **Gateway log:** `C:\tmp\clawdbot\clawdbot-YYYY-MM-DD.log` (date-rotated)
- **Today's log:** `C:\tmp\clawdbot\clawdbot-2026-05-08.log`

### Memory / State
- **MEMORY.md:** `C:\Users\Aaron\clawd\MEMORY.md` (long-term curated memory)
- **Daily notes:** `C:\Users\Aaron\clawd\memory\YYYY-MM-DD.md`
- **SOUL.md:** `C:\Users\Aaron\clawd\SOUL.md` (personality, role definition)
- **HEARTBEAT.md:** `C:\Users\Aaron\clawd\HEARTBEAT.md` (heartbeat patrol instructions)
- **SESSION-STATE.md:** `C:\Users\Aaron\clawd\SESSION-STATE.md` (hot RAM)
- **Inbox:** `C:\Users\Aaron\clawd\inbox\` (async message drop)

---

## SCHEDULED TASKS

| Task Name | Trigger | What It Does |
|-----------|---------|--------------|
| Clawdbot Gateway | AtLogon / manual | Runs `gateway.cmd` → launches node gateway on :18789 |

**No heartbeat scheduled tasks** — heartbeats are managed internally by Clawdbot cron system.
**No ngrok scheduled task** — ngrok is started manually.

---

## SSH ACCESS

- **OpenSSH Server:** ✅ Running (Status: Running, StartType: Automatic)
- **Port:** 22 (default)
- **Firewall rules:** 
  - "OpenSSH SSH Server (sshd)" — Inbound, Enabled
  - "SSHD (Tailnet only)" — Inbound, Enabled (x2)
- **User:** `Aaron` (same as interactive user)
- **Auth:** Password auth available, pubkey auth available
- **LAN:** `ssh Aaron@10.0.0.50`
- **Tailscale:** `ssh Aaron@100.73.106.82`

**To set up key auth from AlienWare:**
```powershell
# On AlienWare, generate key if needed:
ssh-keygen -t ed25519 -f C:\Users\aaron\.ssh\plato_recovery_key -N ""

# Copy public key to Plato:
scp C:\Users\aaron\.ssh\plato_recovery_key.pub Aaron@10.0.0.50:C:\Users\Aaron\.ssh\

# On Plato (or via SSH), append to authorized_keys:
type C:\Users\Aaron\.ssh\plato_recovery_key.pub >> C:\ProgramData\ssh\administrators_authorized_keys
# (Aaron is in Administrators group, so Windows OpenSSH uses ProgramData path)
```

---

## CHANNEL CONFIG — How Aaron Reaches Plato

**Channel:** Google Chat
**Webhook path:** `/google/events`
**Full public URL:** `https://liny-tien-pleuritic.ngrok-free.dev/google/events`

**Implication for recovery:** If ngrok is down, Aaron cannot reach Plato through Google Chat. Must use SSH or local access.

---

## KNOWN FAILURE MODES & RECOVERY

### 1. Gateway process crashed (most common)
**Symptom:** Port 18789 not listening, Google Chat messages unanswered
**Recovery:** Re-trigger the scheduled task:
```powershell
schtasks /run /TN "Clawdbot Gateway"
```
**Note:** No supervisor loop — if the task is already "Running" but node died, you may need to end the task first:
```powershell
schtasks /end /TN "Clawdbot Gateway"
Start-Sleep -Seconds 3
schtasks /run /TN "Clawdbot Gateway"
```

### 2. Duplicate gateway processes
**Symptom:** Two node.exe processes both on port 18789 (seen in current state — PIDs 16032 + 18620)
**Recovery:** Kill all node gateway processes, wait for port to free, restart:
```powershell
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like '*entry.js*gateway*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 5
schtasks /run /TN "Clawdbot Gateway"
```

### 3. Ngrok tunnel down
**Symptom:** Gateway responds locally but not via public URL
**Recovery:** Kill and restart ngrok:
```powershell
Stop-Process -Name ngrok -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Start-Process ngrok -ArgumentList "http 18789" -WindowStyle Hidden
```
**⚠️ The public URL will change** unless Aaron has a reserved domain on ngrok. This means the Google Chat webhook configuration would need updating.

### 4. Gateway hung (process alive, port bound, not responding)
**Symptom:** Port 18789 shows LISTENING but `curl http://127.0.0.1:18789` hangs
**Recovery:** Kill the specific node.exe PID holding the port:
```powershell
$pid = (netstat -ano | Select-String ":18789.*LISTENING" | ForEach-Object { ($_ -split '\s+')[-1] } | Select-Object -First 1)
taskkill /T /F /PID $pid
Start-Sleep -Seconds 5
schtasks /run /TN "Clawdbot Gateway"
```

### 5. Config corruption
**Symptom:** Gateway starts but crashes immediately
**Recovery:** Restore from backup:
```powershell
Copy-Item "C:\Users\Aaron\.clawdbot\clawdbot.json.bak" "C:\Users\Aaron\.clawdbot\clawdbot.json" -Force
schtasks /run /TN "Clawdbot Gateway"
```

### 6. ProtonVPN interference
**Symptom:** LAN access works but Tailscale/external fails, or vice versa
**Note:** ProtonVPN (10.2.0.2 interface) may interfere with routing. If LAN probe fails but Tailscale works (or vice versa), VPN routing is likely the issue. Not fixable remotely — Aaron must toggle VPN.

### 7. All providers rate-limited
**Symptom:** Gateway running, tunnel up, but responses fail
**Recovery:** Check logs for 429 errors. Wait for rate limits to clear. Check API billing.

---

## VERIFICATION COMMANDS (quick health check)

```powershell
# Is the gateway process running?
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like '*entry.js*gateway*' } | Select-Object ProcessId

# Is port 18789 listening?
netstat -ano | findstr ":18789" | findstr "LISTENING"

# Does the gateway respond to HTTP?
curl.exe -s -o nul -w "%{http_code}" http://127.0.0.1:18789/api/status

# Is ngrok running with a tunnel?
curl.exe -s http://127.0.0.1:4040/api/tunnels

# Does the public URL work end-to-end?
curl.exe -s -o nul -w "%{http_code}" https://liny-tien-pleuritic.ngrok-free.dev/api/status

# Scheduled task status
schtasks /query /TN "Clawdbot Gateway" /FO LIST

# Full restart sequence
schtasks /end /TN "Clawdbot Gateway"
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like '*entry.js*gateway*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 5
schtasks /run /TN "Clawdbot Gateway"
```

---

## SERVICES ON THIS MACHINE

| Service | Status | Start | Notes |
|---------|--------|-------|-------|
| OpenSSH Server (sshd) | ✅ Running | Automatic | Port 22 |
| Clawdbot Gateway | ✅ Running | Scheduled Task | Port 18789 |
| Ngrok | ✅ Running | Manual | Port 4040 (API), tunnel on :18789 |
| Ollama | ❌ Not running | Manual | Port 12345 (when active) |
| ProtonVPN | ✅ Running | — | May affect routing |

---

## DIFFERENCES FROM ARISTOTLE ARCHITECTURE

| Aspect | Aristotle (AlienWare) | Plato (NIETZSCHE2025) |
|--------|----------------------|----------------------|
| Port | 18792 | 18789 |
| Supervisor | gateway-resilient.cmd (infinite restart) | None (single-run task) |
| Ngrok task | Scheduled task with auto-restart | Manual process |
| PM2 | Comms Hub + other services | Not installed |
| SSH | Needs install | ✅ Already running |
| Config path | `.clawdbot-aristotle\` | `.clawdbot\` |
| Ngrok URL | Static (reserved domain) | Dynamic (changes on restart) |
| Heartbeat tasks | Windows Scheduled Tasks (30m/120m) | Internal Clawdbot cron |

**Key risk:** Plato's ngrok URL is NOT reserved — it changes every restart. This means ngrok restart = broken Google Chat webhook until config is updated. Aristotle's is stable.
