# SETUP-NEW-MACHINE.md
# Hourly clawd-shared sync — bootstrap for Plato and Empiricus
# Created: 2026-05-12 by Aristotle session
# Aristotle is already set up (this doc was created from there). This is for the OTHER two machines.

This document is the one-shot bootstrap to get hourly GitHub sync running on a new fleet machine. It assumes Aristotle's sync is already operational (which sets the canonical pattern). Allow about 10 minutes per machine.

---

## What this gives you

After running these steps on a machine, the following happens automatically every hour:

1. Anything in that machine's `clawd-shared/` directory gets mirrored to `github.com/Nietzsche247/family-backup/clawd-shared/`
2. Edits made on other machines flow back to this one
3. Conflicts on the same file resolve by precedence: **Aristotle wins, then Plato, then Empiricus**
4. Losing version is preserved as a `.conflict-<agent>-<timestamp>` sidecar file (auto-cleaned after 24 hours)
5. Bridge alerts fire only when something genuinely needs your attention (silent on routine syncs)

The sync ONLY runs on Aristotle for the comms-hub data (`C:\bravo-team\signal-fire/`, `reports/`, `state/*.yaml`). Plato and Empiricus skip that part — their job is just to sync their own clawd-shared.

---

## Prerequisites

- Git for Windows installed at `C:\Program Files\Git\bin\git.exe`. If installed somewhere else, edit `$GIT_EXE` in the script.
- Aaron is logged in interactively (the scheduled task runs in user context).
- The machine has internet access (the script pushes to github.com).
- The Comms Hub on Aristotle is running and reachable at `http://omni-alienware2025.tail2ccb03.ts.net:3001` — this is where bridge alerts go.

---

## Plato setup (do this in a Claude Desktop session on nietzsche2025)

### Step 1 — Pull the bootstrap script from the repo

```powershell
# If family-backup is already cloned somewhere, navigate there. Otherwise:
git clone https://github.com/Nietzsche247/family-backup.git C:\Users\Aaron\github\family-backup

# Copy the Plato variant to your scripts directory
$dest = "C:\Users\Aaron\clawd\scripts\clawd-shared-sync.ps1"
if (-not (Test-Path (Split-Path $dest))) { New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null }
Copy-Item "C:\Users\Aaron\github\family-backup\clawd-shared\sync-scripts\plato_clawd-shared-sync.ps1" $dest
```

### Step 2 — Insert the GitHub PAT (it's scrubbed from the synced version)

The script's `$GH_TOKEN` line will say `[REDACTED_GH_CLASSIC]`. Replace it with the actual classic PAT (Aaron has it, or grab it from Aristotle's running script at `C:\Users\aaron\clawd-aristotle\scripts\clawd-shared-sync.ps1` line ~15).

```powershell
# Quick replace:
$f = "C:\Users\Aaron\clawd\scripts\clawd-shared-sync.ps1"
$c = Get-Content $f -Raw
$c = $c -replace '\[REDACTED_GH_CLASSIC\]', '[REDACTED_GH_CLASSIC]_REAL_TOKEN_HERE'
Set-Content -Path $f -Value $c -NoNewline
```

### Step 3 — Verify Plato-specific paths

Open the script in an editor and confirm these are right for Plato:

```
$AGENT_NAME = "plato"
$AGENT_RANK = 2
$LOCAL_DIR  = "C:\Users\Aaron\clawd-shared"      # capital A on Plato
$REPO_DIR   = "C:\Users\Aaron\github\family-backup"
$LOG_FILE   = "C:\Users\Aaron\clawd\logs\clawd-shared-sync.log"
```

### Step 4 — Test-run manually

```powershell
& "C:\Users\Aaron\clawd\scripts\clawd-shared-sync.ps1"
Start-Sleep -Seconds 10
Get-Content "C:\Users\Aaron\clawd\logs\clawd-shared-sync.log" -Tail 10
```

Expect to see `pushed=N pulled=M conflicts=0` followed by `=== sync complete ===`. Check github.com/Nietzsche247/family-backup for new commits from "plato-sync".

### Step 5 — Create the scheduled task at HH:20

```powershell
$taskName = "Clawd-Shared Sync"
$scriptPath = "C:\Users\Aaron\clawd\scripts\clawd-shared-sync.ps1"

# Remove if exists
Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false

$action = New-ScheduledTaskAction `
    -Execute "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$scriptPath`""

# Plato's stagger: :20 past the hour
$now = Get-Date
$nextSlot = $now.Date.AddHours($now.Hour).AddMinutes(20)
if ($nextSlot -lt $now) { $nextSlot = $nextSlot.AddHours(1) }

$trigger = New-ScheduledTaskTrigger -Once -At $nextSlot -RepetitionInterval (New-TimeSpan -Hours 1)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings `
    -Description "Hourly mirror of clawd-shared to family-backup. Plato stagger position :20."

Get-ScheduledTaskInfo -TaskName $taskName | Format-List TaskName, NextRunTime
```

### Step 6 — Dispatch question (NEW context)

You mentioned Dispatch (Anthropic local bot) was recently added on nietzsche2025. The sync script touches everything under `C:\Users\Aaron\clawd-shared/`. **Does Dispatch read/write to that directory?**

- If yes — Dispatch's edits will propagate to the fleet at rank 2 (alongside Plato's edits). That may be desirable. Confirm via the next sync's commit log on GitHub.
- If no — no action needed.

Bridge an answer to Aristotle either way once confirmed, so this gets recorded in the fleet knowledge file.

---

## Empiricus setup (do this in a Claude Desktop session on nietzsche-i9)

### Step 1 — Pull the bootstrap script

```powershell
# Clone family-backup if not present
git clone https://github.com/Nietzsche247/family-backup.git C:\Users\aaron\github\family-backup

# Copy Empiricus variant
$dest = "C:\Users\aaron\.openclaw\scripts\clawd-shared-sync.ps1"
if (-not (Test-Path (Split-Path $dest))) { New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null }
Copy-Item "C:\Users\aaron\github\family-backup\clawd-shared\sync-scripts\empiricus_clawd-shared-sync.ps1" $dest
```

### Step 2 — Insert the PAT (same as Plato Step 2)

```powershell
$f = "C:\Users\aaron\.openclaw\scripts\clawd-shared-sync.ps1"
$c = Get-Content $f -Raw
$c = $c -replace '\[REDACTED_GH_CLASSIC\]', '[REDACTED_GH_CLASSIC]_REAL_TOKEN_HERE'
Set-Content -Path $f -Value $c -NoNewline
```

### Step 3 — Verify Empiricus-specific paths

```
$AGENT_NAME = "empiricus"
$AGENT_RANK = 3
$LOCAL_DIR  = "C:\Users\aaron\clawd-shared"      # lowercase aaron
$REPO_DIR   = "C:\Users\aaron\github\family-backup"
$LOG_FILE   = "C:\Users\aaron\.openclaw\logs\clawd-shared-sync.log"
```

**Important — Empiricus is OpenClaw, not Clawdbot.** The sync script doesn't touch OpenClaw subsystems, so it should work identically. But verify clawd-shared actually exists at `C:\Users\aaron\clawd-shared\` — if Empiricus uses `.openclaw\workspace\shared\` or similar, adjust `$LOCAL_DIR`.

### Step 4 — Test-run

Same as Plato Step 4 but with Empiricus's paths.

### Step 5 — Create scheduled task at HH:40

Same as Plato Step 5 but change `AddMinutes(20)` to `AddMinutes(40)` and the description to "Empiricus stagger position :40".

---

## Verification — after both machines are set up

1. On any machine, edit a file in `clawd-shared/` (e.g. add a line to a test file).
2. Within an hour, that change appears in github.com/Nietzsche247/family-backup.
3. Within another hour, that change appears in `clawd-shared/` on the OTHER two machines.
4. The Comms Hub bridge stays silent (no alerts) — sync ran clean.

## What to do if it breaks

- **Sync says "conflict"** — losing version saved as a `.conflict-*` sidecar in `clawd-shared/`. Inspect both, manually pick the right version, delete the sidecar.
- **Sync FAILED bridge alert** — check the log on that machine, then check git status in `C:\Users\<aaron>\github\family-backup\`. Most likely cause is network blip; usually self-recovers on next run.
- **PAT expired** — the script will fail and bridge-alert. Generate a new fine-grained PAT scoped to family-backup with Contents R/W + Metadata R/O, replace in the script on all three machines.
- **Want to pause syncing** — `Disable-ScheduledTask -TaskName "Clawd-Shared Sync"` on whichever machine. Re-enable with `Enable-ScheduledTask` when ready.

## TODOs left over (for future sessions)

- [ ] Rotate the classic PAT to a fine-grained one stored in Windows Credential Manager
- [ ] Add "minutes since last successful sync" health check to `aristotle_recover.py --check`
- [ ] Add weekly PAT-expiration check task (alerts 14 days before expiration)
- [ ] Verify Plato heartbeats are reaching the Comms Hub (currently showing offline)
- [ ] Verify Empiricus heartbeats are reaching the Comms Hub (currently showing offline)
- [ ] Confirm Dispatch's relationship to clawd-shared on Plato
