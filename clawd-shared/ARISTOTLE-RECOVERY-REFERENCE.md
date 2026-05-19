# ARISTOTLE RECOVERY REFERENCE
# For: Desktop Commander (Claude Code), Plato, or any external agent performing recovery
# Last updated: 2026-05-08 by Aristotle
# Location: C:\Users\aaron\clawd-shared\ARISTOTLE-RECOVERY-REFERENCE.md

---

## IDENTITY

- **Agent:** Aristotle (CEO / Strategic Coordinator)
- **Host machine:** Omni-AlienWare2025 (Windows 11, x64)
- **Clawdbot version:** 2026.1.24-3
- **Primary model:** anthropic/claude-opus-4-6
- **Fallback cascade:** Sonnet 4.6 → GPT-5.2 → Sonnet 4

---

## ARCHITECTURE — What Must Be Running

### Process Tree (healthy state)
```
Scheduled Task "Aristotle Gateway"
  └─ aristotle-gateway-task.cmd (wrapper)
       └─ gateway-resilient.cmd (supervisor, infinite restart loop)
            └─ node.exe entry.js gateway (the actual Clawdbot process)
                 └─ Listening on ws://127.0.0.1:18792

Scheduled Task "Aristotle Ngrok"
  └─ aristotle-ngrok-task.cmd (wrapper)
       └─ ngrok.exe http 18792 (tunnel)
            └─ Tunnel: https://uneffective-unprepossessingly-september.ngrok-free.dev
            └─ Local API: http://127.0.0.1:4040/api/tunnels
```

### Health Checks (in order of severity)

| Check | Command | Healthy Response |
|-------|---------|-----------------|
| 1. Port bound | `netstat -ano \| findstr ":18792" \| findstr "LISTENING"` | One PID listening |
| 2. HTTP responds | `curl.exe -s http://127.0.0.1:18792/api/status` | Returns JSON or HTML (any 200) |
| 3. Ngrok tunnel | `curl.exe -s http://127.0.0.1:4040/api/tunnels` | JSON with tunnel URL |
| 4. Public URL | `curl.exe -s https://uneffective-unprepossessingly-september.ngrok-free.dev/api/status` | Reaches through tunnel to gateway |
| 5. Google Chat webhook | Google Chat messages arrive and Aristotle responds | End-to-end verification |

**CRITICAL:** Check #2 is the gap the current recovery script doesn't cover. A process can hold a port without responding to HTTP. If port is LISTENING but HTTP probe fails → the gateway is hung → kill the node.exe process and let the supervisor restart it.

### Port Map

| Port | Service | Protocol |
|------|---------|----------|
| 18792 | Aristotle Gateway | HTTP/WebSocket |
| 4040 | Ngrok local API | HTTP |
| 3001 | Comms Hub | HTTP (separate PM2 process) |
| 3003 | NorthStar Ledger | HTTP (separate PM2 process) |
| 11434 | Ollama | HTTP (embeddings) |

---

## FILES — Where Everything Lives

### Config
- **Gateway config:** `C:\Users\aaron\.clawdbot-aristotle\clawdbot.json`
- **Google Chat service account:** `C:\Users\aaron\.clawdbot-aristotle\aristotle-philosopher-3d358ef817e9.json`
- **Workspace:** `C:\Users\aaron\clawd-aristotle\`
- **Shared workspace:** `C:\Users\aaron\clawd-shared\`

### Recovery Scripts
- **Recovery script:** `C:\Users\aaron\clawd-shared\aristotle_recover.py` (stdlib Python, no pip)
- **Recovery launcher:** `C:\Users\aaron\clawd-shared\aristotle-recover.cmd`
- **Gateway task wrapper:** `C:\Users\aaron\clawd-shared\aristotle-gateway-task.cmd`
- **Ngrok task wrapper:** `C:\Users\aaron\clawd-shared\aristotle-ngrok-task.cmd`
- **Gateway supervisor:** `C:\Users\aaron\.clawdbot-aristotle\gateway-resilient.cmd`

### Logs
- **Gateway task log:** `C:\tmp\clawdbot-aristotle\task-gateway.log`
- **Ngrok task log:** `C:\tmp\clawdbot-aristotle\task-ngrok.log`
- **Gateway internal log:** `C:\tmp\clawdbot\clawdbot-2026-MM-DD.log`

### Memory / State
- **STATE.md:** `C:\Users\aaron\clawd-aristotle\STATE.md` (current task, blockers)
- **MEMORY.md:** `C:\Users\aaron\clawd-aristotle\MEMORY.md` (long-term curated memory)
- **Daily notes:** `C:\Users\aaron\clawd-aristotle\memory\YYYY-MM-DD.md`
- **SOUL.md:** `C:\Users\aaron\clawd-aristotle\SOUL.md` (personality, role definition)
- **HEARTBEAT.md:** `C:\Users\aaron\clawd-aristotle\HEARTBEAT.md` (heartbeat patrol instructions)

---

## SCHEDULED TASKS

| Task Name | Triggers | What It Does |
|-----------|----------|--------------|
| Aristotle Gateway | AtLogon + Every 5 min | Kills zombies, clears port, launches gateway-resilient.cmd |
| Aristotle Ngrok | AtLogon (15s delay) + Every 5 min | Waits up to 120s for gateway on :18792, then launches ngrok |
| Aristotle Heartbeat - Daytime 30m | 08:00-20:00 every 30m | Lightweight health poll (Sonnet 4) |
| Aristotle Heartbeat - Night 120m | 20:00-08:00 every 120m | Same but less frequent |

Both gateway/ngrok tasks use `MultipleInstances=IgnoreNew` — safe to re-trigger; won't duplicate.

---

## CHANNEL CONFIG — How Aaron Reaches Aristotle

**Channel:** Google Chat
**Webhook path:** `/google/events`
**Full public URL:** `https://uneffective-unprepossessingly-september.ngrok-free.dev/google/events`
**Auth:** Google Chat → service account JWT → Clawdbot validates against `audienceType: app-url`

**Implication for recovery:** If ngrok is down, Aaron cannot reach Aristotle through Google Chat. He must use the local machine directly (Desktop Commander, RDP, or physical access).

---

## AGENT ROSTER (sub-agents Aristotle can spawn)

| Agent | Primary Model | Fallbacks | Role |
|-------|--------------|-----------|------|
| daedalus | GPT-5.4 | GPT-5.3 Codex → Sonnet 4.6 | Senior Engineer |
| thales | Sonnet 4.6 | Sonnet 4 | Systems & Ops |
| steelman | Grok 4.20 Experimental | Grok 4 → Sonnet 4.6 | Devil's Advocate |
| researcher | Gemini 2.5 Pro | Sonnet 4.6 | Research & Analysis |
| sentinel | Grok 4 | Grok 3 | Security/Monitoring |

---

## CRON JOBS (managed by Clawdbot internally)

| Name | Schedule | Purpose |
|------|----------|---------|
| bridge-watchdog-15m | Every 4h | Infrastructure health: public URL, cloudflared, hub, ledger, ollama |
| self-healing-8am | Daily 8 AM | Verify PM2 services, cloudflared, ollama |
| end-of-day-signal-fire | Daily 9 PM | Team reflection check-in |
| researcher-daily-micro-scan | Daily 9 AM | AI/research news scan |
| daily-gdrive-backup | Daily 4:30 AM | Google Drive family backup |
| webb-opensource-watch | Mon/Thu 9 AM | Watch for Webb open-source release |
| state-md-staleness-check | Mon 10 AM | Alert if STATE.md >7 days stale |

---

## KNOWN FAILURE MODES & RECOVERY

### 1. Gateway process crashed (most common)
**Symptom:** Port 18792 not listening, Google Chat messages unanswered
**Auto-recovery:** 5-min periodic task trigger restarts within 5 min
**Manual:** `aristotle-recover.cmd --soft`

### 2. Ngrok tunnel down
**Symptom:** Port 18792 listening locally but public URL unreachable
**Auto-recovery:** 5-min periodic task trigger
**Manual:** `aristotle-recover.cmd --soft`

### 3. Zombie supervisor accumulation
**Symptom:** Multiple cmd.exe processes with gateway-resilient in command line, Bonjour name conflicts in logs
**Cause:** Manual clicks on aristotle start.cmd while tasks are already running
**Manual:** `aristotle-recover.cmd` (full hammer)

### 4. Gateway hung (process alive, port bound, not responding) — NOT YET COVERED
**Symptom:** Port 18792 shows LISTENING but `curl http://127.0.0.1:18792` hangs or times out
**Recovery:** Kill the node.exe PID holding port 18792, supervisor will restart it
**Script gap:** Current script only checks port, not HTTP response

### 5. Config corruption
**Symptom:** Gateway starts but crashes immediately with JSON parse errors in log
**Recovery:** Restore from known-good config backup
**Script gap:** No config backup/restore in current tooling

### 6. All providers rate-limited
**Symptom:** Gateway running, tunnel up, but all responses fail with model errors
**Recovery:** Wait for rate limits to clear; check API billing/quotas
**Script gap:** Not detectable from outside — requires reading gateway internal log

### 7. Machine-level failure (cannot access locally)
**Symptom:** No response on LAN IP, no response on Tailscale IP, no public URL
**Recovery:** Physical access or remote reboot via Tailscale/iLO
**Plato option:** If Plato has SSH/WinRM access to Omni-AlienWare2025, it could run the recovery script remotely

---

## RECOMMENDED IMPROVEMENTS TO aristotle_recover.py

### HIGH PRIORITY

1. **HTTP health probe (not just port check)**
   After confirming port 18792 is LISTENING, make an actual HTTP GET to `http://127.0.0.1:18792/api/status` with a 10-second timeout.
   If port is up but HTTP fails → kill the node.exe PID and let supervisor restart.
   This catches hung gateways that the port-only check misses.

2. **End-to-end tunnel probe**
   After confirming ngrok is up at localhost:4040, make an HTTP GET through the public tunnel URL:
   `https://uneffective-unprepossessingly-september.ngrok-free.dev/api/status`
   This catches: ngrok running but tunnel not connected, DNS issues, ngrok session expired.

3. **Config backup on every successful recovery**
   After verify() passes, copy `C:\Users\aaron\.clawdbot-aristotle\clawdbot.json` to
   `C:\Users\aaron\clawd-shared\backups\clawdbot-aristotle-YYYY-MM-DD.json`
   On recovery failure with JSON parse errors, offer to restore from latest backup.

4. **Structured JSON output mode (--json)**
   For programmatic callers (Plato, cron, monitoring):
   ```json
   {
     "status": "healthy|degraded|down",
     "gateway": {"port": true, "http": true, "pid": 357644},
     "ngrok": {"process": true, "tunnel": true, "url": "https://..."},
     "action_taken": "none|soft_restart|full_recovery",
     "timestamp": "2026-05-08T13:15:00-07:00"
   }
   ```

### MEDIUM PRIORITY

5. **Log tail on failure**
   When recovery fails or detects a problem, automatically tail the last 20 lines of:
   - `C:\tmp\clawdbot-aristotle\task-gateway.log`
   - `C:\tmp\clawdbot\clawdbot-2026-MM-DD.log`
   Print them in the diagnostic output. Saves a manual step every time.

6. **Notification on recovery**
   After a successful recovery (not --check), attempt to POST a message to the Comms Hub:
   `POST http://127.0.0.1:3001/api/bridge/message`
   `{"to": "aristotle", "from": "recovery-script", "body": "Auto-recovery completed: [details]"}`
   Also attempt: `POST http://127.0.0.1:3001/api/signal-fire`
   `{"agent": "recovery-script", "entry": "Aristotle recovered at [time]. Cause: [reason]."}`

7. **Stale ngrok URL detection**
   The expected URL is hardcoded (`EXPECTED_NGROK_URL`). If ngrok assigns a different URL after restart,
   the Google Chat webhook breaks because the audience URL in clawdbot.json won't match.
   The script should detect URL mismatch and warn loudly (or optionally update the config).

### NICE TO HAVE

8. **Windows Event Log integration**
   Write recovery events to Windows Application Event Log. Useful for correlating with system reboots,
   blue screens, power events.

9. **Cron job health check**
   Query `http://127.0.0.1:18792` for cron job status (next run times, last run status).
   Flag any cron job whose last run was >2x its interval ago.

10. **Remote execution mode (--remote)**
    Accept a target hostname/IP + credentials (or SSH key path) and execute the recovery on a remote machine.
    This is the Plato-can-recover-Aristotle path.

---

## FOR PLATO: Remote Recovery Setup (Not Yet Implemented)

If you want Plato (10.0.0.50) to be able to recover Aristotle:

**Option A: SSH/WinRM**
- Install OpenSSH Server on Omni-AlienWare2025 (Windows feature)
- Give Plato's SSH key access
- Plato runs: `ssh aaron@10.0.0.198 "python C:\Users\aaron\clawd-shared\aristotle_recover.py --json"`
- Parse JSON output, alert Aaron if recovery fails

**Option B: Shared file signal**
- Plato writes a recovery request to `\\100.108.47.36\clawd-shared\recovery-requests\aristotle.json`
- A local scheduled task on AlienWare watches that directory and triggers recovery
- Lower complexity, no SSH needed, but slower (polling interval)

**Option C: Comms Hub relay**
- Plato POSTs to `http://127.0.0.1:3001/api/bridge/message` (via Tailscale IP)
- But if the hub is also down, this fails — not a good primary recovery path

Recommendation: Option A (SSH) is most reliable for actual failures. Option B as backup.

---

## VERIFICATION COMMANDS (quick health check)

```powershell
# Is the gateway process running?
Get-Process | Where-Object {$_.ProcessName -eq 'node' -and $_.MainWindowTitle -match 'gateway'} | Format-Table Id,StartTime

# Is port 18792 listening?
netstat -ano | findstr ":18792" | findstr "LISTENING"

# Does the gateway respond to HTTP?
curl.exe -s -o nul -w "%{http_code}" http://127.0.0.1:18792/api/status

# Is ngrok running with a tunnel?
curl.exe -s http://127.0.0.1:4040/api/tunnels | python -m json.tool

# Does the public URL work end-to-end?
curl.exe -s -o nul -w "%{http_code}" https://uneffective-unprepossessingly-september.ngrok-free.dev/api/status

# Scheduled task status
schtasks /query /TN "Aristotle Gateway" /FO LIST
schtasks /query /TN "Aristotle Ngrok" /FO LIST

# Full diagnostic (no changes)
python C:\Users\aaron\clawd-shared\aristotle_recover.py --check -v
```


---
---

# SUPPLEMENT — 2026-05-11/12 (field-tested additions)

*Added 2026-05-11/12 by Plato session in collaboration with Aristotle, after a multi-hour wedged-gateway recovery and the NorthStar Bridge emitter injection work. The original document above is unchanged.*

## Failure Mode 8: WEDGED GATEWAY (supervisor + periodic trigger loop)

**Symptom pattern (this is what tonight looked like):**
- Port 18792 shows LISTENING but HTTP requests hang/timeout
- `Stop-Process -Id <pid>` returns "Cannot find process" almost immediately because the PID is rotating — the supervisor respawns it within seconds
- Even after killing all visible processes, the port re-binds to a new PID
- `Disable-ScheduledTask` shows `State: Running` afterwards — that field is cached, ignore it, the disable took effect
- The recovery script's `bring_up_gateway()` times out because triggering the task respawns the same broken state
- Sub-agents are unreachable because the gateway is wedged
- The `aristotle-gateway-task.cmd` wrapper itself can hang in its own kill-existing-supervisors loop when zombie cmd.exe processes are present — log shows multiple "task starting" entries without the corresponding "launching gateway-resilient.cmd" follow-up

**Root cause:** The supervisor (`gateway-resilient.cmd`) is in an infinite restart loop with stale in-memory state. The 5-minute periodic trigger on the scheduled task adds another respawn vector. The wrapper script's own zombie cleanup adds a third.

**L30 (recorded 2026-05-11):** Grafted code in the loaded plugin file does not take effect until the gateway PROCESS restarts — not just task restart, not just SIGUSR1. The supervisor protects against simple `taskkill /IM`. Use `Stop-ScheduledTask` / `Start-ScheduledTask` (supervisor-aware), or escalate to Mode 8.

**L31 (recorded 2026-05-11):** When L30 alone is not enough — wrapper script hangs, supervisor in tight respawn — the bypass is to launch `gateway.cmd` DIRECTLY without going through the scheduled task or its wrapper. The scheduled task is a convenience layer; `gateway.cmd` is the actual launch mechanism.

**L41 (recorded 2026-05-13, from Opus investigation):** The cycling was a PORT-CONFLICT LOOP, not a plugin self-exit. When a stale gateway PID holds port 18792, new instances can't bind → exit cleanly (no crash signature) → supervisor pauses 5s → retry → same failure = ~20-second cycle. The supervisor (gateway-resilient.cmd) was blind-retrying without clearing stale port holders. PATCHED 2026-05-13: supervisor now kills stale port holders inside the retry loop before each `call gateway.cmd`. Manual recovery works because it explicitly kills port holders before relaunch. Failure Mode 8 (wedged-state where gateway hangs without exiting) remains the residual case.

**Recovery procedure (verified 2026-05-11):**

```powershell
# STEP 1: Disable auto-respawn. Ignore "State: Running" output -- disable took effect.
Disable-ScheduledTask -TaskName "Aristotle Gateway"

# STEP 2: Kill all supervisor / wrapper / gateway-cmd processes.
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*gateway-resilient*" -or
    $_.CommandLine -like "*aristotle-gateway-task*" -or
    $_.CommandLine -like "*gateway.cmd*"
} | ForEach-Object {
    Write-Host "Killing PID $($_.ProcessId): $($_.CommandLine)"
    Stop-Process -Id $_.ProcessId -Force
}

# STEP 3: Kill whoever currently owns port 18792.
$portPid = (Get-NetTCPConnection -LocalPort 18792 -State Listen -ErrorAction SilentlyContinue |
            Select-Object -First 1).OwningProcess
if ($portPid) { Stop-Process -Id $portPid -Force }

# STEP 4: Verify port stays empty for 30+ seconds. If something rebinds, repeat 1-3.
Start-Sleep 30
Get-NetTCPConnection -LocalPort 18792 -State Listen -ErrorAction SilentlyContinue
# Must return NOTHING.

# STEP 5: Launch gateway DIRECTLY (the L31 bypass).
cd C:\Users\aaron\.clawdbot-aristotle
.\gateway.cmd
# Gateway runs foreground. Wait for "listening on ws://127.0.0.1:18792 (PID NNNNNN)".
# This will be a fresh PID running the patched dist/ (or index.ts) code.

# STEP 6: From a second PowerShell window, verify HTTP responds.
Invoke-WebRequest -Uri "http://127.0.0.1:18792/api/status" -TimeoutSec 5 -UseBasicParsing

# STEP 7: Once healthy, RE-ENABLE auto-recovery. DO NOT FORGET THIS.
Enable-ScheduledTask -TaskName "Aristotle Gateway"
```

**⚠️ Critical:** Step 7 is what tonight's recovery missed and is why the gateway was found down on the next session. The task was disabled in Step 1 and never re-enabled. Without it, the supervisor + 5-min periodic auto-recovery is permanently lost until someone notices and re-enables.

The recovery script (`aristotle_recover.py`) was patched on 2026-05-11/12 to automate this — `teardown()` now disables the task, and `bring_up_gateway()` re-enables it and falls back to direct `gateway.cmd` launch if the task path fails to bind. See "Recovery script status" below.

## The plugin load-path discovery (memos-local-openclaw-plugin)

After 5+ hours editing `extensions/memos-local/dist/index.js` with no effect, Daedalus found the actual load path. **For any future plugin work:**

- The gateway loads `extensions/memos-local/index.ts` directly via jiti, **not** `dist/index.js`.
- The resolution comes from `package.json`'s `clawdbot.extensions` field. The `clawdbot.plugin.json` file is ignored by discovery.
- jiti caches the compiled TS→CJS output in `%TEMP%\jiti\memos-local-index.<contenthash>.cjs`. **Edits to `index.ts` have zero effect until the jiti cache entry is deleted AND the gateway process restarts.**
- The content hash in the filename is computed from the ORIGINAL source. Edits produce a different hash, but the old cache file persists and may be preferentially loaded — always delete the existing cache file rather than assuming it gets invalidated.

**Procedure for any extension edit:**
1. Edit the `.ts` source (not `dist/`)
2. `Remove-Item "$env:TEMP\jiti\memos-local-index.*.cjs" -Force`
3. Restart the gateway process (SIGUSR1 reload is NOT enough — needs a full process restart)
4. Verify the edit is loaded with a diagnostic `console.error` line and grep today's gateway log

## NorthStar Bridge emitter — verified end-to-end 2026-05-12

The MemOS → Ledger event bridge is operational. Verification trace:
- `extensions/memos-local/index.ts` line ~2315, after `worker.enqueue(captured)`, emits `[EMITTER_INJECTION_REACHED] <iso-time> agent=<id> chunks=<count>` and POSTs to Ledger `/events`.
- 2026-05-12T01:35:23.323Z — first emitter fire after the jiti cache clear + full restart
- 2026-05-12T01:35:24.458Z — corresponding Ledger event `01KRCX659ACYWK7S6A8K60BQDP` (event_type=memory_capture)
- 1.1s round-trip, no retry queue needed

**Note:** The emitter logs `agent=agent` (raw `captureAgentId`), not `agent=main` (normalized). The L26 normalization happens elsewhere in the agentId pipeline. Cosmetic, not a blocker — the event still lands.

## MemOS subsystem (added since 2026-05-08)

| Component | Location |
|-----------|----------|
| Database | `C:\Users\aaron\.openclaw\memos-local\memos.db` |
| Extension dir | `C:\Users\aaron\.clawdbot-aristotle\extensions\memos-local\` |
| Compiled plugin entry (the file actually loaded) | `extensions/memos-local/index.ts` (via jiti, NOT `dist/index.js`) |
| Memory Viewer UI | `http://127.0.0.1:18799` (when plugin loaded) |
| Plugin patches log | `extensions/memos-local/PATCHES.md` (5 patches applied 2026-05-10/11) |

## Recovery script status (post-2026-05-11/12)

`aristotle_recover.py` (the 823-line file, header says `(v2)`) now implements all 7 "Recommended Improvements" from the original doc:

| Improvement | Status |
|-------------|--------|
| 1. HTTP health probe | ✅ Implemented (`gateway_http_health()`) |
| 2. End-to-end tunnel probe | ✅ Implemented (with NAT loopback handling) |
| 3. Config backup on success | ✅ Implemented (writes to `clawd-shared\backups\`) |
| 4. Structured JSON output | ✅ Implemented (`--json` flag) |
| 5. Log tail on failure | ✅ Implemented |
| 6. Notification to Comms Hub | ✅ Implemented |
| 7. Stale ngrok URL detection | ✅ Implemented |

Additional patches applied 2026-05-11/12 from this session:
- `teardown()` now calls `Disable-ScheduledTask` first to prevent respawn-during-teardown
- `bring_up_gateway()` now calls `Enable-ScheduledTask` first and falls back to direct `gateway.cmd` launch if the task path fails to bind in `GATEWAY_BIND_TIMEOUT_S`

## Plato-side fork notice (2026-05-11)

There is a separate `aristotle_recover_v2.py` and a 377-line `ARISTOTLE-RECOVERY-REFERENCE.md` on Plato's clawd-shared (NIETZSCHE2025) that were created during this work before the canonical files on Aristotle's machine were known. They are FORKS. The canonical versions are here, on Aristotle's machine. Plato-side cleanup needed when next on that host:
- Delete `aristotle_recover_v2.py` from Plato's clawd-shared (canonical is `aristotle_recover.py` here)
- Replace Plato's `ARISTOTLE-RECOVERY-REFERENCE.md` with this canonical version

clawd-shared has a local `.git` repo but no remote, so there is no automatic sync between machines. Cross-machine consistency requires manual copy or a sync mechanism (SSH copy, Tailscale share, etc.) — not yet set up.


---

## L41 — Port-conflict cycling looks like a clean exit (2026-05-13)

**Symptom:** Gateway restarts every ~15-20 seconds in `task-gateway.log`. ZERO crash markers in the application log: no `EADDRINUSE`, no `FATAL`, no `uncaughtException`, no `SIGTERM`. Each gateway lifecycle is short (~15s active, then 5s supervisor pause).

**Surprise:** `clawdbot` treats `Port 18792 is already in use` as a graceful exit, not a crash. The actual exit reason hides inside log lines tagged `ERROR` level by clawdbot's own console logger — not by the process exit signal. So a `Select-String` for crash patterns finds nothing, while a `Select-String` for `Port .* already in use` finds the truth.

**Root cause:** A stale process (zombie node.exe from a previous hung lifecycle) was holding port 18792. `gateway-resilient.cmd` blindly retried `call gateway.cmd` after each exit, but the freshly-launched gateway found the port still occupied and exited immediately with the "graceful" port-conflict error. The supervisor saw this as a normal exit and looped forever at ~20-second cadence.

**The wrapper script (`aristotle-gateway-task.cmd`) DOES clear the port — but only once at the top of its lifecycle, NOT inside the supervisor's inner loop.** Since the wrapper's `call gateway-resilient.cmd` is blocking, the port-clearing logic only runs at wrapper startup, never per-iteration.

**Fix applied 2026-05-13:** Patched `gateway-resilient.cmd` to clear stale port-18792 holders inside the supervisor loop, BEFORE each `call gateway.cmd`. Backup at `gateway-resilient.cmd.bak-2026-05-13`. The patched supervisor activates on next process restart (organic — don't force).

**Diagnostic hint:** When investigating "node.exe restarts repeatedly with no crash signature in app log," check `task-gateway.log` cadence AND grep the app log for `Port .* already in use` or `another gateway instance is already listening`. Don't trust the absence of crash markers as evidence of healthy operation.

---

## L42 — The running SQLite DB is source of truth for schema, not source code (2026-05-13)

**Symptom:** The bridge-emitter Phase 3 work added `event_subtype` and `memory_chunk_id` columns to `events` table via `ALTER TABLE` in `db.js`. Aristotle in-session reported that events were landing but the new columns weren't persisting (`undefined` / `null`). Theory at the time: jiti cache served the old `db.js`.

**Reality:** The Ledger has TWO live SQLite databases on this machine:
- `C:\North_Star_Projects\ledger\ledger.db` — older/legacy, last write May 12, ~155 events
- `C:\North_Star_Projects\ledger\ledger-staging.db` — the LIVE one currently receiving Phase 3 events, ~700+ events, multi-MB

The in-session diagnosis was reading from the wrong DB. The live DB already had both new columns AND was populating `event_subtype` correctly for every routine-session-capture event. The "schema not persisting" conclusion was a false alarm.

**General principle:** `ALTER TABLE` in source files (`db.js`, `dist/db.js`) only runs on fresh-DB initialization — it never migrates live databases. If a schema change is intended for an existing database, run the ALTER directly against the live `.db` file using `sqlite3` CLI or a Python script with `sqlite3` stdlib. Then update the source for clean future installs. This is the same family of confusion as the jiti cache: a compiled / source artifact is not the runtime state.

**Diagnostic hint:** Before concluding "ALTER didn't run," (a) confirm WHICH database file the running process is actually opening (check connection strings or process file handles), (b) read column list from that exact file via `PRAGMA table_info(events)`, and (c) verify by row inspection — `SELECT id, event_subtype FROM events ORDER BY id DESC LIMIT 5`. The `memory_chunk_id` column DID exist in the live DB but was null for routine captures — that's an emitter-payload issue, not a schema issue.

---

## Mini-changelog: 2026-05-13 evening session

- **gateway-resilient.cmd patched** with port-clearing logic (L41). Backup preserved.
- **clawd-shared-sync.ps1 patched** in three places with `commit.gpgsign=false` + `tag.gpgsign=false` config (L37 defense-in-depth). Source in `clawd-aristotle\scripts\`, variants in `clawd-shared\sync-scripts\`. Future variant generation inherits the fix.
- **Bridge confirmed operational**: ledger-staging.db has 700+ events; 48/48 memory_capture events have `event_subtype` populated correctly. Only `memory_chunk_id` is null for routine captures (emitter-side gap, not schema).
- **Wedged-gateway recovery validated end-to-end**: manual 7-step procedure (Failure Mode 8) successfully cleared the cycling loop at 17:36 PDT.


---

## L43 — MemOS plugin rebuilds are a wedge risk vector (2026-05-13)

**Forensic finding from the 5-day cycling investigation (May 8-13):**

Cycling began at 2026-05-08 20:00 PDT. The only nontrivial system change in the preceding 4-hour window was a complete rebuild of the MemOS plugin's `dist/` directory at 2026-05-08 16:52 PDT (every TypeScript file recompiled in a single second — `tsc` or `npm run build` pattern), followed by a `memos-config.json` edit at 17:19 PDT. No reboots, no network changes, no other extension changes, no significant Application or System event log entries in that window.

The 2-3 hour gap between rebuild and cycling onset is consistent with: gateway kept running the old code until a heartbeat-driven or scheduled-task-driven restart loaded the new build, at which point the new code wedged. PID 29124 was the first squatter (held port 18792 from midnight May 8 onward); 4 more wedged-successor PIDs cycled across the following 5 days until manual recovery on May 13 17:36 PDT.

**Cannot pinpoint the exact change**: MemOS plugin has no `.git` directory, and `index.ts` has been overwritten multiple times since (most recently for Phase 3 bridge-emitter work). The May 8 source state is not recoverable. So the strongest claim we can make: MemOS rebuilds correlate with wedge risk.

**Operational rule:**
After any MemOS plugin rebuild, treat it as a risky deploy:
1. Immediately restart the gateway (don't wait for a heartbeat/cron to do it on your behalf later — that delays the moment you'd see a failure).
2. Watch `task-gateway.log` for at least 30 minutes — if you see "Starting Aristotle gateway..." entries closer together than ~5 minutes apart, cycling has started.
3. The supervisor patch (L41, port-clearing in the loop) plus the watchdog scheduled task (`Aristotle Watchdog`) will auto-recover from a wedge, but you still want to see the symptom early so you can roll back the rebuild rather than relying on auto-recovery indefinitely.

**Note on hermes-lossless-claw async registration warning** (`plugin register returned a promise; async registration is ignored`): this is a real bug — the plugin uses `await import(...)` for absolute-path module imports, so its `register()` function is legitimately async, but the clawdbot plugin loader doesn't await it. Plugin registration completes after the loader's phase ends. In practice it completes ~milliseconds before the gateway starts listening, so tools have always been available by the time real traffic arrives. NOT the trigger for the May 8 wedge (this bug predates the wedge by 16 days). Worth fixing for hygiene; not urgent.

Fix path (low priority): replace dynamic `await import(absPath)` calls in `extensions/hermes-lossless-claw/index.ts` with `createRequire(import.meta.url)` + sync `require()` calls; remove the `async` keyword; clawdbot's sync loader will then complete registration before moving on.

---

## L45 — WEDGE TAXONOMY: 1 LESSON + N SKILLS + M PATCHES

**Date:** 2026-05-18 | **Companion:** L30, L31, L41, L43, L44

### The principle
Every wedge should produce: **one lesson** (durable architectural insight), **one or more skills** (invocable diagnostic/recovery procedures), and **zero or more patches** (infrastructure fixes). Never one giant doc.

- **Lessons** want preservation. The principle doesn't change.
- **Skills** want maintenance. Paths, commands, log formats evolve.
- **Patches** are code. They live in the codebase, not in docs.

### Case study: May 15-18 wedge (62 hours)
**Reproducible crash + auto-restart = wedge.** Defense-in-depth assumes failures are non-deterministic. When a bug fires on every restart, three respawn vectors (supervisor, 5-min task, watchdog) amplify the crash instead of recovering from it. 807 recovery cycles, zero successful recoveries.

**Specific cause:** L44 patch (skill-manage.ts) — `require(better-sqlite3)` threw through jiti's transpile layer. Every restart loaded the same broken code.

**What it produced:**
- Lesson: L45 (this — the taxonomy principle + "reproducible crash + auto-restart = wedge")
- Skill: `diagnose-wedge-cycle` (P1-P4 forensics procedure)
- Patches: F1 (crash-loop detection), F2 (wrapper early-return), F3 (try/catch hardening, applied 2026-05-18)

### Verification protocol update
L43 watch window must include **≥1 full heartbeat cycle** after any plugin edit. The L44 roundtrip test passed (8→9→8) but the first heartbeat after Aaron left is when the wedge began.

### L45.SUB.6 — RestartOnFailure is a hidden respawn vector
Scheduled task `RestartOnFailure` with `Count=999` and `Interval=PT1M` is a FOURTH respawn vector that bypasses the supervisor's crash-loop ceiling (F1a). It fires 1-min restarts from OUTSIDE the supervisor, resetting the crash-loop counter each time. Discovered 2026-05-18 when the task auto-re-enabled itself after Aaron disabled it during Failure Mode 8 recovery.

**Complete respawn vector inventory (audit ALL before declaring safe):**
1. Supervisor restart loop (gateway-resilient.cmd) — F1a ceiling
2. Scheduled task periodic trigger (PT5M) — F2 early-return
3. Scheduled task RestartOnFailure — **REMOVED 2026-05-18** (was Count=999/PT1M)
4. Watchdog escalation chain — F1b guard

**Fix:** RestartOnFailure removed from both Aristotle Gateway and Watchdog tasks. The 5-min periodic trigger is the single task-level respawn vector, coordinated with F1a. Backups in `clawd-shared/backups/`.

### L45.SUB.1 — F1b TryParse validation
F1b had a silent PowerShell 7+ `[DateTime]::TryParse` overload bug that made the crash-loop counter always return 0. Caught by manual pre-deploy validation. **Safety-net code requires execution validation, not just syntax checks.**

### Hard rules
1. **Reproducible crash + auto-restart = wedge.** Fix reproducibility (F3) AND add crash-loop detection (F1).
2. **Health checks must include uptime.** Gateway with uptime < 2× poll interval is suspicious.
3. **New wedge → 1 lesson + N skills + M patches.** Never inline procedures in lesson docs.
4. **Count ALL respawn vectors.** We had FOUR stacked, not three. Each needs an independent audit pass.

