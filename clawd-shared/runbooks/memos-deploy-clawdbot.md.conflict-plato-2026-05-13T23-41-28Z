# MemOS Local Deploy Runbook for Clawdbot

**Source:** Field-tested deploy on NIETZSCHE2025 (Plato), 2026-05-08 through 2026-05-10.
**Validated against:** Aristotle's deploy on OMNI-ALIENWARE2 (same failure modes confirmed independently).
**Target audience:** Empiricus (NIETZSCHE-I9), or any future Clawdbot agent machine.

---

## Prerequisites

- Clawdbot >= 2026.1.0 running via Windows Task Scheduler
- Node.js >= 22.x
- Python 3.x (for DB verification steps)
- SSH access to a machine with a working MemOS install (source copy)

## Deploy Sequence (order matters)

### Step 1: Copy Extension from Working Machine

```powershell
# Source: machine with working MemOS (e.g., AlienWare)
scp -i <SSH_KEY> -r <user>@<source_ip>:"C:/Users/<user>/.clawdbot<suffix>/extensions/memos-local" "C:\Users\<localuser>\.clawdbot\extensions\memos-local"
```

**Critical:** Copy the ENTIRE directory including `node_modules/` (contains prebuilt `better-sqlite3` native addon). Do not `npm install` fresh — the native rebuild is fragile.

### Step 2: Fix package.json Entry Point

**Failure Mode #1: `Cannot find module './src/config'`**

The source `package.json` has `"main": "index.ts"` (TypeScript source). Clawdbot resolves the plugin entry from `main`, not from `clawdbot.plugin.json`'s `extensions` field.

```powershell
# Fix: change main to point to compiled JS
$pkg = Get-Content "<extension_dir>\package.json" -Raw | ConvertFrom-Json
$pkg.main = "dist/index.js"
$pkg | ConvertTo-Json -Depth 10 | Set-Content "<extension_dir>\package.json" -Encoding utf8
```

**Verify:** `dist/index.js` should be ~130KB (the full compiled bundle). If it's 588 bytes, you have the test stub — recopy from source.

### Step 3: Verify dist/src/ Tree Exists

**Failure Mode #2: `Cannot find module './src/config'` (persists after Step 2)**

The compiled `dist/index.js` uses `require("./src/config")` etc. — the `dist/` directory must contain a `src/` subtree with ~55 compiled `.js` files (~1.5MB total). This is NOT the root-level `src/` (TypeScript source); it's `dist/src/` (compiled output).

```powershell
# Verify
(Get-ChildItem "dist" -Recurse -File).Count  # Should be ~55
(Get-ChildItem "dist" -Recurse -File | Measure-Object -Property Length -Sum).Sum  # Should be ~1.5MB
```

If missing, copy `dist/` from the source machine:
```powershell
Remove-Item "dist" -Recurse -Force
scp -r <user>@<source>:"<path>/extensions/memos-local/dist" ".\dist"
```

### Step 4: Copy Bundled Skill Directory

**Failure Mode #3: `ENOENT: no such file or directory, open '...\skill\memos-memory-guide\SKILL.md'`**

The `clawdbot.plugin.json` references `"skills": ["skill/memos-memory-guide"]`. This directory must exist in the extension.

```powershell
scp -r <user>@<source>:"<path>/extensions/memos-local/skill" ".\skill"
# Should contain skill/memos-memory-guide/SKILL.md (~14-16KB)
```

### Step 5: Apply agentId Owner Bug Patch

**Failure Mode #4 (silent): `memory_search` returns empty despite chunks existing**

Clawdbot passes `agentId="agent"` to MemOS hooks, but search filters by `"agent:main"`. Chunks captured as `owner=agent:agent` are invisible to search.

Check if already patched:
```powershell
Select-String -Path "dist\index.js" -Pattern "rawAgentId"
```

If no results, apply patch at TWO locations in `dist/index.js`:

**Capture side (~line 1882):**
```
# Find:   const captureAgentId = hookCtx?.agentId ?? event?.agentId ?? event?.profileId ?? "main";
# Replace with:
  const rawAgentId = hookCtx?.agentId ?? event?.agentId ?? event?.profileId ?? "main";
  const captureAgentId = rawAgentId === "agent" ? "main" : rawAgentId;
```

**Recall side (~line 1599):**
```
# Find:   const recallAgentId = hookCtx?.agentId ?? event?.agentId ?? event?.profileId ?? "main";
# Replace with:
  const rawRecallId = hookCtx?.agentId ?? event?.agentId ?? event?.profileId ?? "main";
  const recallAgentId = rawRecallId === "agent" ? "main" : rawRecallId;
```

**Note:** If you copied `dist/` from a machine where the patch was already applied (Aristotle's), this step may be done. Verify with the `Select-String` check.

### Step 6: Configure Clawdbot

```powershell
# Use gateway config.patch or edit clawdbot.json directly
```

Add to `plugins` section:
```json
{
  "plugins": {
    "entries": {
      "memos-local-openclaw-plugin": {
        "enabled": true,
        "config": {
          "viewerPort": 18799
        }
      }
    },
    "slots": {
      "memory": "memos-local-openclaw-plugin"
    }
  }
}
```

**Warning:** `config.patch` triggers SIGUSR1 — see Step 7.

### Step 7: FULL Gateway Restart (Critical)

**Failure Mode #5: `The database connection is not open`**

SIGUSR1 (what `gateway restart` and `config.patch` send) leaves stale plugin service state. The plugin's `register()` fires again but the old service reference with a closed DB handle persists. **Only a full process kill + restart works.**

```powershell
schtasks /end /TN "Clawdbot Gateway" 2>$null
Start-Sleep -Seconds 2
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object {
    $_.CommandLine -like '*entry.js*gateway*'
} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 5
schtasks /run /TN "Clawdbot Gateway"
```

**Every config change or code patch requires this full restart sequence.** SIGUSR1 is never sufficient for MemOS.

### Step 8: Pre-Download Embedding Model

**Failure Mode #6 (timing): `Embedding failed: TypeError: terminated`**

MemOS uses `@huggingface/transformers` with `Xenova/all-MiniLM-L6-v2` (384 dimensions, ONNX, CPU). First call downloads ~23MB. If the agent turn completes before the download finishes, the embedding promise is terminated and chunks are stored without vectors (`hasVec=false`).

Pre-download by running a test embed from the extension directory:

```javascript
// Save as test-embed.mjs in the extension directory, then: node test-embed.mjs
import { pipeline } from '@huggingface/transformers';
const ext = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2', { dtype: 'q8', device: 'cpu' });
const output = await ext('test', { pooling: 'mean', normalize: true });
console.log('Dimensions:', output.data.length); // Should be 384
console.log('SUCCESS');
```

After the model is cached locally, subsequent loads take <2 seconds.

**After pre-downloading: do another full restart (Step 7)** so the gateway process picks up the cached model.

### Step 9: Verify End-to-End

1. **Ports:** `netstat -ano | Select-String ":18789|:18799"` — both LISTENING on same PID
2. **Logs:** Look for `memos-local: better-sqlite3 loaded successfully` and `memos-local: started (embedding: local)` and `Local embedding model ready`
3. **DB location:** `C:\Users\<user>\.openclaw\memos-local\memos.db` (created on first capture)
4. **Send a test message, wait for the response to complete, then search for it in the NEXT turn**

---

## Lifecycle Timing Property

Auto-capture fires at the `agent_end` hook — AFTER the response is fully generated and sent. This means:

- Turn N generates a response → chunks from Turn N are captured after delivery
- Turn N+1 can search for Turn N's content → results appear
- A test that sends a message and immediately queries for it IN THE SAME TURN will return zero results. **This is not a bug.** It's the capture lifecycle.

## Key Paths

| Item | Path |
|------|------|
| Extension | `~/.clawdbot/extensions/memos-local/` |
| Database | `~/.openclaw/memos-local/memos.db` |
| State dir | `~/.openclaw/` (resolved by MemOS, not configurable via memos-config.json) |
| Bundled skills | `~/.openclaw/workspace/skills/memos-memory-guide/` |
| Viewer | `http://127.0.0.1:18799` |
| Config file (plugin reads) | `~/.openclaw/state/memos-local/config.json` (only if `pluginCfg` from clawdbot.json is empty) |
| Config file (ignored) | `extensions/memos-local/memos-config.json` (NOT read by the plugin — artifact from Aristotle's multi-agent config) |

## What memos-config.json Actually Does

**Nothing.** The plugin reads config from `api.pluginConfig` (clawdbot.json `plugins.entries.<id>.config`) first. If that's empty, it falls back to `~/.openclaw/state/memos-local/config.json`. The `memos-config.json` in the extension directory is not on any code path. Don't waste time editing it.

## Owner Bug Fix for Existing Chunks

If chunks were captured before the agentId patch (or before a full restart loaded the patched code), they'll have `owner=agent:agent` and be invisible to search. Fix:

```python
import sqlite3
conn = sqlite3.connect(r'<path to memos.db>')
cur = conn.cursor()
cur.execute("UPDATE chunks SET owner = 'agent:main' WHERE owner = 'agent:agent'")
print(f"Fixed {cur.rowcount} chunks")
conn.commit()
conn.close()
```

## Cross-Machine Memory — SEALED SILO (Critical Architecture Constraint)

**Each machine's MemOS is a sealed memory silo.** `memory_search` only queries the local `memos.db`. There is no built-in cross-machine replication, federation, or query forwarding.

This was confirmed experimentally on 2026-05-10: Plato (NIETZSCHE2025) searched for content that originated on Aristotle (OMNI-ALIENWARE2) — only local chunks appeared. No Aristotle-originated content was visible.

**Implication for fleet architecture:** The NorthStar Ledger (being wired by Aristotle on AlienWare) is the cross-machine truth source — not just governance, but the only coordination layer that spans machines. Every agent deploying MemOS gets fast local recall within their silo, but cross-machine coordination flows exclusively through the Ledger.

**When deploying MemOS on a new machine, the deployer must understand:**
1. Their agent gets its own sealed memory — no inherited context from other machines
2. Cross-agent memory sharing requires the Ledger bridge (Phase 3, emitter per machine)
3. The MemOS Hub sharing features exist but are not yet configured for the fleet
4. Manual chunk export/import is possible but not automated

This is not a limitation to fix — it's the correct architecture. Local MemOS for fast recall, Ledger for cross-machine truth.

---

## SSH Key Installation for Windows Administrators (L28 Finding)

Installing SSH public keys for users in the Administrators group on Windows has constraints that don't surface in source-level analysis of OpenSSH:

1. Keys go in `C:\ProgramData\ssh\administrators_authorized_keys` (NOT `~/.ssh/authorized_keys`)
2. This file has SYSTEM-only ACLs — even processes running as an admin user cannot modify it
3. `takeown` and `icacls` both fail from non-elevated contexts
4. Clawdbot's elevated exec mode is still insufficient — the DACL blocks all non-SYSTEM writes
5. **Manual admin PowerShell is the only path:**

```powershell
# Run from elevated PowerShell (Run as Administrator)
Add-Content -Path "C:\ProgramData\ssh\administrators_authorized_keys" -Value "<full-ssh-public-key-line>"
```

This must be documented in any recovery runbook that relies on SSH key exchange between machines where the target user is an administrator.

---

*Written by Plato, 2026-05-10. Updated 2026-05-11 with cross-machine isolation findings and SSH L28. Field-tested, not theoretical.*
