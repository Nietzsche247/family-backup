# NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md

> **For: future Claude sessions opened by Aaron on any fleet machine.**
> **Save / read this whole file before doing anything else.**
> **Source-of-truth path on each host:** `C:\Users\<user>\clawd-shared\NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md`
>
> Last updated: 2026-05-11/12 by Claude Opus 4.7 in collaboration with Aaron, Aristotle, and Plato.
> This document is **fleet-wide** but **not** auto-synced — `clawd-shared` has a local `.git` repo without a remote. Per-machine copies can drift. When updating, manually mirror to the other machine.
> Agent-specific details (process trees, exact paths, failure-mode procedures) live in `ARISTOTLE-RECOVERY-REFERENCE.md` (on Aristotle's clawd-shared) and `PLATO-ARCHITECTURE-INFO.md` (on Plato's clawd-shared).

---

## WHAT YOU ARE WORKING WITH

NorthStar OS is Aaron's multi-agent AI fleet. He calls himself the eighth agent. The agents are Claude / GPT / Grok / Gemini instances running as Clawdbot or OpenClaw gateways across three Windows machines on a Tailscale tailnet. Aaron uses Claude Desktop with Desktop Commander + Filesystem MCPs to administer them.

Each agent has its own:
- Gateway process (a Node.js HTTP/WebSocket server on a known port)
- ngrok tunnel (so external services like Google Chat or Slack can webhook in)
- Identity, memory, role
- Skills directory and tool set

When Aaron says "Aristotle stopped responding" or "Plato is down," he almost always means one of: gateway process died, ngrok tunnel went stale, or both. The 90% recovery is: kill stale processes, restart gateway, restart ngrok, verify.

The fleet has now been tooled with the **`fleet-recovery` skill**, co-authored by Aristotle and Plato, that lets any agent SSH into any other agent's machine and run that machine's recovery script. Use it.

## FLEET MAP

| Agent      | Host                | LAN IP    | Tailscale IP   | Gateway Port | Channel                | Notes |
|------------|---------------------|-----------|----------------|--------------|------------------------|-------|
| Aristotle  | Omni-AlienWare2025  | 10.0.0.49 | 100.108.47.36  | 18792        | Google Chat            | CEO/coordinator, has supervisor + reserved ngrok domain |
| Plato      | NIETZSCHE2025       | 10.0.0.50 | 100.73.106.82  | 18789        | Google Chat            | App builder, dynamic ngrok URL, no supervisor loop |
| Empiricus  | nietzsche-i9        | (LAN)     | (Tailscale)    | 18789        | Slack (OpenClaw, not Clawdbot) | QA / Validation |

The three machines share a folder via Tailscale: `clawd-shared` on each host. Files placed there are the canonical cross-machine surface (recovery scripts, fleet-wide docs, config backups). The skills are in each agent's local `clawd\skills\` (Plato) or `clawd-aristotle\skills\` (Aristotle).

Each agent has its **own** ngrok account / authtoken. They are NOT fleet-shared, despite what older docs claim. Tokens live in per-host `*start.cmd` files on each user's desktop. If a tunnel that "worked for months" suddenly fails authentication, see "ngrok config-path migration" under critical quirks below — that's the most common cause.

## STEP 0 EVERY SESSION

Before doing anything destructive, confirm:

1. **Which machine you're on:** `hostname` or `$env:COMPUTERNAME`
2. **Desktop Commander tools are loaded:** `get_config` returns
3. **Read the agent's authoritative reference docs**, in this order:
   - The agent's per-machine architecture file (e.g. `references/plato-architecture.md` or `references/aristotle-architecture.md` inside `fleet-recovery/`) — this is written by the agent itself and is ground truth for paths, ports, processes, and failure modes
   - The `fleet-recovery` SKILL.md for the cross-agent recovery workflow
   - This document for fleet-wide context

If those docs disagree with anything below, **trust them.** They are written by the agents on their own hosts.

## RECOVERY QUICK REFERENCE

Both agents use the same script architecture: `*_recover.py` with `--check`, `--soft`, default (full hammer), and `--json` modes. Same exit codes, same JSON schema.

### Diagnose only (safe, no changes)

| Target    | Command on local host | Command via SSH from peer |
|-----------|------------------------|---------------------------|
| Aristotle | `aristotle-recover.cmd --check` | See `fleet-recovery/SKILL.md` "Plato fixing Aristotle" |
| Plato     | `python C:\Users\Aaron\clawd\scripts\plato_recover.py --check` | See `fleet-recovery/SKILL.md` "Aristotle fixing Plato" |

### Fix only what's broken

Replace `--check` with `--soft` in any command above. Surgical: leaves healthy components alone.

### Full hammer (kill everything, restart all)

Remove `--check` / `--soft` entirely. Use when soft fix didn't take or when state is mysteriously wedged.

### Wedged-gateway recovery (Aristotle-specific, Mode 8)

If on Aristotle the port is LISTENING but HTTP hangs, and after running the full hammer the same problem persists with PIDs rotating every few seconds, you are in the "wedged gateway" state. This means the supervisor + 5-min periodic trigger are respawning a broken process faster than you can kill it.

The fix is supervisor-aware: `Disable-ScheduledTask` to stop the respawn, kill everything, verify the port stays free for 30+ seconds, then launch `gateway.cmd` DIRECTLY (bypassing the task wrapper which can itself hang in its zombie-cleanup loop). When healthy, `Enable-ScheduledTask` to restore crash auto-recovery.

The 2026-05-11/12 patches to `aristotle_recover.py` automate this: `teardown()` disables the task, `bring_up_gateway()` re-enables it and falls back to direct `gateway.cmd` launch if the task path stalls. So `aristotle-recover.cmd` alone now handles Mode 8 — manual recovery is only needed if the script itself fails.

**Full manual procedure:** `ARISTOTLE-RECOVERY-REFERENCE.md` → "Failure Mode 8". 7 PowerShell steps, verified 2026-05-11.

**L30 (recorded 2026-05-11):** Grafted code in a loaded plugin file does not take effect until the gateway PROCESS restarts, not just task restart, not SIGUSR1. Supervisor protects against `taskkill /IM`.

**L31 (recorded 2026-05-11):** When the supervisor + task wrapper combo blocks normal restart paths, bypass the entire scheduled-task layer by launching `gateway.cmd` directly. The task is a convenience layer, not the source of truth.

**L32 (recorded 2026-05-12):** Plugin discovery uses `package.json` `clawdbot.extensions` field, NOT `clawdbot.plugin.json`. The gateway loads `index.ts` via jiti, not `dist/index.js`. jiti caches compiled output in `%TEMP%\jiti\<name>-<contenthash>.cjs` — always delete the cache file after editing the .ts source, and do a full process restart (SIGUSR1 is not enough).

### Machine-readable output

Append `--json` to any of the above. JSON goes to stdout; human output to stderr. To capture only JSON: append `2>$null` (PowerShell) or `2>nul` (cmd).

## JSON CONTRACT (fleet-recovery skill)

All recovery scripts return this shape with `--json`:

```json
{
  "status": "healthy" | "degraded" | "down",
  "gateway": { "port": true, "http": true, "pid": 12345 },
  "ngrok":   { "process": true, "tunnel": true, "url": "https://...", "url_changed": false },
  "action_taken": "none" | "check" | "soft_restart" | "full_recovery",
  "timestamp": "2026-05-08T16:30:00-07:00"
}
```

Both scripts emit additional fields beyond the contract (`http_status`, `http_time_ms`, `public_skip_reason`, `supervisors`, `urls[]`, etc.) — they don't break the contract; consumers just ignore unknown keys.

**Interpretation rules:**
- `status: "healthy"` → green, report up.
- `status: "degraded"` + `ngrok.public_skip_reason: "loopback"` → NAT hairpin from inside Aaron's network, NOT a real outage. Tunnel is registered locally; verification was just unreliable from the same host.
- `status: "degraded"` (no loopback flag) → genuine partial outage; one of gateway/ngrok is broken. Try `--soft` first.
- `status: "down"` → both broken, run full hammer. If still down after, escalate to Aaron with log tails.

## DECISION TREE — "AGENT X IS DOWN"

1. Run `--check --json` (locally if you're already on the host; otherwise via SSH from a peer).
2. Parse `status`. If `"healthy"` and the symptoms persist → it's not actually the gateway. Likely a channel-level issue (Google Chat config, model rate-limit, etc.). Report what you found.
3. If `"degraded"` and `public_skip_reason: "loopback"` → that's the NAT hairpin, not an outage. Probe from outside the network or trust the local tunnel registration.
4. If `"degraded"` for any other reason → run `--soft --json`. Re-run `--check --json` to confirm.
5. If `"down"` or `--soft` didn't help → run full hammer (no flag) `--json`. Re-run `--check --json` to confirm.
6. If full recovery still doesn't reach `"healthy"` → escalate. Tail the relevant logs (the script does this automatically on failure) and present them to Aaron.

## CRITICAL TOOL QUIRKS (learn these before they bite you)

### Claude Desktop's Electron shell does not inherit system PATH

`python`, `ngrok`, `schtasks` may all fail with "not recognized" when invoked inline from PowerShell via Desktop Commander. Workarounds:

- ngrok: use `Start-Process -FilePath "ngrok" -ArgumentList @(...)` (Windows resolves App Execution Aliases for `Start-Process` even when the shell can't)
- python: hardcode `C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe`, or use `py` if installed, or launch via `cmd /c` (which inherits PATH)
- schtasks: use the `ScheduledTasks` PowerShell module (`Get-ScheduledTask`, `Start-ScheduledTask`) — first-party, doesn't depend on PATH

### Python PATH in SSH sessions

The Windows Store `python.exe` stub fails over SSH on Aristotle's box. The fleet-recovery skill's commands hardcode the full path: `C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe`. Plato's `python` works on PATH.

### Windows OpenSSH `authorized_keys` differs by sshd_config

For administrator users, sshd_config can route to either:
- `C:\ProgramData\ssh\administrators_authorized_keys` (if `Match Group administrators` is in sshd_config — Aristotle's default)
- `C:\Users\<user>\.ssh\authorized_keys` (if no such block — Plato's setup)

Always check which file sshd actually reads:
```powershell
Select-String -Path "C:\ProgramData\ssh\sshd_config" -Pattern "Match|AuthorizedKeysFile|administrators"
```

`administrators_authorized_keys` requires restrictive ACLs to be honored:
```powershell
icacls $path /inheritance:r /grant "NT AUTHORITY\SYSTEM:(F)" /grant "BUILTIN\Administrators:(F)"
```

### `Add-Content` concatenates keys onto one line

PowerShell `Add-Content` does not always append a trailing newline first, so two consecutive calls can merge keys. Verify after install:
```powershell
Get-Content $auth_keys_path | ForEach-Object { "LINE: $_" }
```

If you see two `ssh-ed25519` blobs on one line, fix manually.

### ngrok config-path migrated (early 2026)

Old MSIX-sandboxed config: `C:\Users\<user>\AppData\Local\Packages\ngrok.ngrok_<id>\LocalCache\Local\ngrok\ngrok.yml`
Current config: `C:\Users\<user>\AppData\Local\ngrok\ngrok.yml`

If a tunnel that "worked for months" suddenly fails authentication, **this is the first place to look.** The OLD config may still exist with the right authtoken — copy it over with `ngrok config add-authtoken <token>` (which writes to the new path).

### NAT loopback / TLS hairpin

Probing your own ngrok URL from inside the same network typically fails (TLS errors, connection-closed, status=000). This is **not** proof the tunnel is broken. The recovery script handles this correctly via `public_skip_reason: "loopback"` in the JSON. Authoritative check is `http://127.0.0.1:4040/api/tunnels` returning the expected URL.

### Plato's ngrok URL is dynamic

Despite appearances, Plato's `liny-tien-pleuritic` is NOT a reserved ngrok domain — it can change on restart. Aristotle's `uneffective-unprepossessingly-september` IS reserved. If Plato's tunnel restarts and `ngrok.url_changed: true` shows up in the JSON, the Google Chat webhook config likely needs updating.

### `aristotle-gateway-task.cmd` and `gateway-resilient.cmd` share one PID (Aristotle only)

Aristotle's wrapper uses `call gateway-resilient.cmd` (not `cmd /c`), so they run in the same cmd process. Killing PID X kills both. When counting "supervisors" on Aristotle, include cmd.exe processes whose CommandLine contains EITHER `aristotle-gateway-task` OR `gateway-resilient` — and dedupe by PID. Plato has no equivalent supervisor.

### Recursive `Get-ChildItem` over user home will hang

OneDrive sync paths and symlinks can put it in an infinite loop. Always scope to specific subdirectories. If you must search broadly, use `-Depth 4` or shorter.

### `wmic` is unreliable on Windows 11

Use `Get-CimInstance Win32_Process` instead. Faster, not deprecated, returns proper objects.

### Heartbeats use Sonnet, real interactions use Opus

Each agent's gateway is configured with `claude-opus-4-6` as primary, but heartbeat / cron jobs run on a cheaper model (Sonnet 4 / 4.6). When you wake an agent via Google Chat or DM, it switches to Opus. Don't be alarmed if today's log shows Sonnet — that's by design.

### PowerShell parses `& curl.exe -w "%{...}"` weirdly

The `%{` sequence trips PowerShell. If you need curl's `-w` format, run from `cmd /c` not PowerShell, or use `Invoke-WebRequest`/`Invoke-RestMethod` instead.

## STRUCTURAL DIFFERENCES BETWEEN AGENTS (don't conflate)

| Concern | Aristotle | Plato | Empiricus |
|---------|-----------|-------|-----------|
| Framework | Clawdbot | Clawdbot | OpenClaw (different product) |
| Channel | Google Chat | Google Chat | Slack |
| Gateway port | 18792 | 18789 | 18789 |
| Config dir | `C:\Users\aaron\.clawdbot-aristotle\` | `C:\Users\Aaron\.clawdbot\` | `C:\Users\aaron\.openclaw\` |
| Workspace | `C:\Users\aaron\clawd-aristotle\` | `C:\Users\Aaron\clawd\` | `C:\Users\aaron\.openclaw\workspace\` |
| Supervisor | `gateway-resilient.cmd` (infinite restart) | None — single-run task | (check on machine) |
| ngrok task | Scheduled task w/ auto-restart | Manual process | (check) |
| ngrok URL | Static (reserved domain) | Dynamic (changes on restart) | (check) |
| OpenSSH server | Needs install | Already running | (check) |
| Recovery script | `clawd-shared\aristotle_recover.py` | `clawd\scripts\plato_recover.py` | (none yet) |

## BEHAVIORS AARON CARES ABOUT

- He values brutal honesty. If you were wrong, say so directly. Don't softball.
- He noticed when I jumped to "this is the authtoken's wrong account" without investigating the config-path migration — and was right that I'd skipped the simplest "what changed recently" test. Always check that before invoking deeper theories.
- He prefers copy-paste-ready code blocks for things he might run again later.
- He is fine with destructive actions when reversible and well-explained, but does not want them done silently.
- "It worked for months" is a strong signal. Investigate what changed before claiming a configuration was always wrong.
- He is OK with broader trust models than a default-paranoid agent might want. If you find yourself relitigating a security tradeoff he's already decided, drop it.

## SSH RECOVERY — KEY LOCATIONS

| Direction | Private key on... | Public key installed at... |
|-----------|-------------------|----------------------------|
| Plato → Aristotle | `C:\Users\Aaron\.ssh\plato_to_alienware_key` (on nietzsche2025) | `C:\ProgramData\ssh\administrators_authorized_keys` on Aristotle |
| Aristotle → Plato | `C:\Users\aaron\.ssh\plato_recovery_key` (on Omni-AlienWare2025) | `C:\Users\Aaron\.ssh\authorized_keys` on Plato |

Note the **different authorized_keys paths** for each direction — see "Windows OpenSSH authorized_keys differs by sshd_config" above.

## IF YOU FIND A NEW QUIRK

Append it to this file. Aaron has explicitly asked for this to be a living knowledge base. The pattern: brief description of the symptom, the surprising root cause, and the workaround. Keep it tight — this file should remain readable in one sitting.

When you update one machine's copy, **mirror the change to all three machines.** This file is fleet-wide.
