# NorthStar OS — Operational Recovery Playbook v2
**Document class:** CANDIDATE operational playbook  
**Experiment:** P2BR5-20260904-A  
**Branch:** control-arm  
**Baseline:** P2BR2-BASELINE-20260902-A  
**Produced by:** control-arm-r5 (single-stream sequential executor)  
**Date:** 2026-09-05  

---

## Preface: Why This Playbook Exists

NorthStar OS has proven its infrastructure spine across multiple real incidents: gateway wedge cycles, sub-agent context loss, Ledger unavailability, MemOS drift, and attempt-fencing race conditions. Each of those incidents produced learnings. This playbook consolidates those learnings — from H-003, H-005, R1 repair, the boot-context skill, the diagnose-wedge-cycle skill, and the operating policy — into a single operational reference that any executor can use from a cold state.

The playbook is not aspirational. Every recovery procedure described here is grounded in proven baseline mechanisms. Where a section references a specific script, state file, or command, that reference is drawn directly from the baseline corpus. Where a procedure extends the baseline (because v2 coverage is broader), the extension is marked.

The playbook is organized around the operator's problem: something is wrong, I need to fix it, I need to know when it's fixed, and I need to not make it worse. Each section follows that arc.

---

## Section 1 — Supervisor Watchdog Behavior

### 1.1 What the Supervisor Watchdog Does

The Aristotle supervisor watchdog is a persistent monitoring loop that observes the gateway process health and escalates through defined recovery tiers when degradation is detected. The watchdog writes its observations to `C:\tmp\clawdbot-aristotle\watchdog.log`. This log is the primary forensic record for any gateway incident.

The watchdog uses three observable states:

**HEALTHY:** The gateway is responding on port 18792 with valid HTTP. The watchdog takes no action. It logs a heartbeat entry at a configured interval and continues polling.

**DEGRADED:** The gateway has stopped responding correctly — either port 18792 shows no LISTENING process, or HTTP requests time out or return non-200 responses. The watchdog begins its escalation sequence.

**RECOVERING:** The watchdog has initiated a soft or full restart sequence and is waiting to confirm whether it resolved the degradation.

### 1.2 Escalation Tiers

The watchdog's escalation is tiered to avoid overreacting to transient blips while also not tolerating a sustained wedge:

**Tier 1 — Soft Recovery:** On first detection of DEGRADED, the watchdog attempts a soft restart. It sends a signal to the gateway wrapper process to restart the gateway binary without killing the supervisor. This is appropriate for transient load spikes, momentary hangs, or gateway binary crashes that leave the wrapper alive.

**Tier 2 — Full Restart:** If soft recovery does not produce HEALTHY within a configured timeout (typically 60 seconds), the watchdog escalates to a full restart. This kills the wrapper process, waits for the port to clear, and re-invokes the gateway launch sequence via the scheduled task.

**Tier 3 — Failure Mode 8 / Human Escalation:** If the full restart cycle does not produce HEALTHY — specifically, if the gateway enters the wedge pattern described in Section 2 — the watchdog recognizes the DEGRADED→RECOVERING→DEGRADED loop and escalates to human notification. At this tier, the watchdog STOPS attempting automatic recovery (to avoid amplifying the wedge) and writes a `MANUAL_RECOVERY_REQUIRED` entry to the watchdog log.

### 1.3 Reading the Watchdog Log

To assess what the watchdog saw:

```powershell
Get-Content C:\tmp\clawdbot-aristotle\watchdog.log -Tail 200
```

**Diagnostic counts to derive:**
- Total DEGRADED entries since last HEALTHY
- Total "soft recovery attempted" entries
- Total "full restart attempted" entries  
- Total "recovered to healthy" entries
- Whether `MANUAL_RECOVERY_REQUIRED` appears

**Key signal (from diagnose-wedge-cycle-SKILL.md, L45):** If DEGRADED count >> recovered count, the watchdog correctly detected the problem but could not break the cycle. This is the wedge condition. Proceed to Section 2.

**Second key signal:** If soft recovery attempts outnumber full restart attempts by a large margin, the wrapper's zombie-killer may be hanging before reaching the actual gateway launch (see also `task-gateway.log` in Section 2.4 P3 diagnostic).

### 1.4 Watchdog Policy Constraints

The watchdog operates within two authority constraints drawn from OPERATING-POLICY-v1:

1. **Recovery Before Work (Policy §3):** After any restart initiated by the watchdog, the recovering agent must run bootstrap/boot-context before accepting work. The watchdog restart does not constitute a valid session boot. Agents resuming after watchdog-initiated restart must re-run `northstar active` or the boot-context skill before continuing governed tasks.

2. **No Pointer, No Done (Policy §2):** Watchdog recovery events should be written to the Ledger. If the watchdog's automatic recovery succeeds, the recovered agent should emit a `status_update` with `event_subtype: "watchdog_recovery_complete"`. If Failure Mode 8 is invoked, the human who performs manual recovery should emit the same event type with `event_subtype: "failure_mode_8_complete"`.

---

## Section 2 — Failure Mode 8 Recovery (Wedge Cycle)

### 2.1 Recognizing Failure Mode 8

A wedge cycle is the specific failure mode where the gateway enters a rapid restart loop that prevents stable operation. Key indicators (from diagnose-wedge-cycle-SKILL.md):

- Gateway port 18792 shows new PIDs every 15–30 seconds
- Watchdog shows repeated DEGRADED → soft recovery with no lasting HEALTHY
- `task-gateway.log` shows "Starting" entries without corresponding "launching" entries (the wrapper is hanging before reaching the gateway binary)
- HTTP requests to port 18792 either hang indefinitely or return connection refused
- The pattern has persisted for more than 2 consecutive watchdog cycles without resolution

The wedge is typically triggered by one of:
- A code change to a file loaded by the gateway at startup (MemOS extension, skill-manage handler, clawdbot.json)
- A stale jiti cache that loads corrupted cached module bytecode
- A port-holder zombie from a previous crashed gateway that blocks the new gateway from binding (addressed by L41: supervisor patch 2026-05-13)
- A MemOS rebuild operation during an active session (L43: MemOS rebuilds are wedge risk vectors)

### 2.2 Pre-Recovery Forensics (Run First)

Before executing the 7-step recovery, run P1–P4 diagnostics to identify the trigger. This prevents recovering into the same condition.

**P1 — What killed the gateway:**
```powershell
$logDate = (Get-Date).ToString('yyyy-MM-dd')
$logFile = "C:\tmp\clawdbot\clawdbot-$logDate.log"
Get-Content $logFile -Tail 500 |
  Select-String "ERROR|FATAL|exit|crash|EADDRINUSE|uncaught|unhandled|listening on ws" |
  Select-Object -Last 20
```
Look for: last "listening on ws" line, then anything between it and the end of the log. Any reference to a recently modified file is a trigger candidate.

**P2 — Watchdog history:**
```powershell
Get-Content C:\tmp\clawdbot-aristotle\watchdog.log -Tail 200
```
Count: DEGRADED entries, soft escalations, full restart escalations, "recovered to healthy" entries.

**P3 — Wrapper behavior:**
```powershell
Get-Content C:\tmp\clawdbot-aristotle\task-gateway.log -Tail 300
```
Count "=== aristotle-gateway-task starting ===" vs "launching gateway-resilient.cmd". If starting >> launching, the wrapper is hanging before the actual launch.

**P4 — Trigger file identification:**
```powershell
$files = @(
  "C:\Users\aaron\.clawdbot-aristotle\extensions\memos-local\index.ts",
  "C:\Users\aaron\clawd-shared\openclaw-fork\src\hermes\skill-manage.ts",
  "C:\Users\aaron\clawd-shared\openclaw-fork\src\agents\tools\skill-manage-tool.ts",
  "C:\Users\aaron\.clawdbot-aristotle\clawdbot.json",
  "C:\Users\aaron\.clawdbot-aristotle\gateway.cmd",
  "C:\Users\aaron\.clawdbot-aristotle\gateway-resilient.cmd"
)
foreach ($f in $files) {
  if (Test-Path $f) {
    $item = Get-Item $f
    Write-Host "$($item.Name) mtime=$($item.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))"
  }
}
```
Look for: files modified in the 1–2 hours before the first DEGRADED entry.

### 2.3 The 7-Step Recovery Procedure

Execute these steps in order. Do not skip steps. Do not proceed to step N+1 until step N is confirmed.

**Step 1 — Disable auto-respawn:**
```powershell
Disable-ScheduledTask -TaskName "Aristotle Gateway"
```
This prevents the scheduled task from re-launching the gateway during the recovery procedure, which would create the wedge condition if executed mid-recovery.

**Step 2 — Kill supervisor and wrapper processes:**
```powershell
Get-CimInstance Win32_Process | Where-Object {
  $_.CommandLine -match "gateway-resilient|aristotle-gateway-task|gateway\.cmd"
} | ForEach-Object {
  Write-Host "Killing PID $($_.ProcessId): $($_.Name)"
  Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}
```

**Step 3 — Kill port holder:**
```powershell
$portLine = netstat -ano | Select-String "18792.*LISTENING"
if ($portLine) {
  $pid = ($portLine -split '\s+')[-1]
  Write-Host "Port 18792 held by PID $pid — killing"
  Stop-Process -Id $pid -Force
} else {
  Write-Host "Port 18792 is clear"
}
```

**Step 4 — Wait 30 seconds, verify port stays empty:**
```powershell
Start-Sleep 30
$check = netstat -ano | Select-String "18792.*LISTENING"
if ($check) {
  Write-Host "WARNING: Port 18792 still held — something re-launched. Investigate before continuing."
} else {
  Write-Host "Port 18792 confirmed clear"
}
```

**Step 5 — Clear jiti cache:**
```powershell
Remove-Item "$env:TEMP\jiti\memos*" -Force -ErrorAction SilentlyContinue
Write-Host "jiti cache cleared"
```
This is critical: the jiti cache loads TypeScript files at gateway start. A stale cache can reload corrupted bytecode from a failed previous run, causing the same crash immediately on restart. Key lesson L31: gateway loads index.ts via jiti; delete jiti cache after any code edits.

**Step 6 — Re-enable and start the scheduled task:**
```powershell
Enable-ScheduledTask -TaskName "Aristotle Gateway"
Start-ScheduledTask -TaskName "Aristotle Gateway"
Write-Host "Scheduled task re-enabled and started"
```

**Step 7 — Verify recovery:**
```powershell
Start-Sleep 45
$listening = netstat -ano | Select-String "18792.*LISTENING"
if ($listening) {
  $healthCheck = try { (Invoke-WebRequest -Uri http://127.0.0.1:18792/status -TimeoutSec 10 -UseBasicParsing).StatusCode } catch { "FAILED" }
  Write-Host "Port LISTENING. HTTP status: $healthCheck"
} else {
  Write-Host "FAIL: Port 18792 not listening after 45 seconds"
}
```
Success: port LISTENING + HTTP 200. The gateway is recovered.

### 2.4 Post-Recovery Actions

1. Emit Ledger event:
```json
{
  "event_type": "status_update",
  "event_subtype": "failure_mode_8_complete",
  "agent": "aristotle",
  "decision_rationale": "Failure Mode 8 recovery executed. Root cause: <P4 finding>. jiti cache cleared. Scheduled task restarted.",
  "trigger_file": "<filename from P4>",
  "watchdog_cycles": <N>,
  "fix_applied": "7-step-recovery"
}
```

2. Run boot-context to re-establish governed session state before accepting any work.

3. If the P4 diagnostic identified a trigger file: verify the change that caused the wedge and assess whether it needs to be reverted before the gateway will remain stable.

4. Monitor watchdog.log for 30 minutes. If DEGRADED recurs within that window, the trigger was not fully resolved.

---

## Section 3 — H-003 Attempt-Fencing Recovery

### 3.1 What H-003 Prevents

The H-003 mechanism (proven in baseline: program-a/H003-PROOF.md) prevents a superseded GEN-1 agent from writing accepted state after GEN-2 has taken over a task. Without this fence, a slow GEN-1 agent finishing its computation could overwrite the state that a GEN-2 replacement is building, producing silent data corruption in the Ledger.

The fence implementation lives in `lease-registry.js` and centers on a JSON lease file (`active-leases.json`). Every attempt on a task holds a lease. Before writing any `task_complete` or accepted state, the worker must validate its lease. If the lease has been superseded, the write is rejected.

### 3.2 Failure Signatures

H-003 failures manifest in two distinct ways:

**Type A — Fence operating correctly, worker discovering it was superseded:**  
The worker calls `validateLease` and receives `{valid: false, reason: "SUPERSEDED"}`. This is not a failure — it is the fence working. The worker should log the rejection and halt cleanly. No recovery needed beyond confirming GEN-2 is proceeding normally.

**Type B — Fence not being called (silent bypass):**  
If a worker writes to the Ledger or accepted state path without calling `validateLease` first, the fence is bypassed. The result is a potential state collision between GEN-1 and GEN-2 outputs. This is a governed violation.

**Type C — Lease file corruption or unavailability:**  
If `active-leases.json` is missing, corrupted, or inaccessible, `validateLease` returns `{valid: false, reason: "NO_LEASE_REGISTERED"}`. Workers that treat this as a green light (rather than a fence failure) create the same risk as Type B.

### 3.3 Recovery Procedure by Type

**Type A Recovery (fence correctly fired, GEN-1 halted):**
1. Confirm GEN-1 logged the rejection: check worker output for "LEASE REJECTED" or "valid:false" response.
2. Confirm GEN-2's lease is ACTIVE: `node lease-registry.js validate <taskId> <gen2-attemptId>` should return `{valid:true}`.
3. Monitor GEN-2 to completion. No further intervention needed.
4. Emit Ledger event: `{ "event_type": "status_update", "event_subtype": "attempt_fence_fired", "agent": "orchestrator", "decision_rationale": "GEN-1 supersession fence operated correctly. GEN-1 rejected. GEN-2 proceeding." }`

**Type B Recovery (silent bypass detected):**
1. Identify which Ledger events were written by the superseded worker. Query: `GET /events?agent=<gen1-agent>&task=<taskId>&since=<supersession timestamp>`.
2. Mark those events as `requires_review` by emitting `{ "event_type": "status_update", "event_subtype": "stale_write_detected", "events_affected": [list] }`.
3. Determine which of GEN-1's writes conflict with GEN-2's intended state.
4. If GEN-2 has not yet completed: isolate GEN-1's writes from GEN-2's working context (do not delete — preserve for audit). Allow GEN-2 to produce a clean accepted state.
5. If GEN-2 has completed: compare GEN-1's writes against GEN-2's final state. If they diverge, the final state is GEN-2's (it holds the active lease). Write a `conflict_resolved` Ledger event documenting the resolution.
6. Amend work packet templates: ALL workers must call `validateLease(taskId, myAttemptId)` immediately before any Ledger write. This is non-negotiable per H-003.

**Type C Recovery (lease file unavailable):**
1. Check whether `active-leases.json` exists at the configured path.
2. If missing: recreate from Ledger state. Query Ledger for the most recent `task_assigned` or `task_started` event for the affected task. That event's `attempt_id` and `generation` are the authoritative current lease state.
3. Recreate the lease file with the correct active lease: `node lease-registry.js acquire <taskId> <attemptId> <generation> <agentId>`.
4. Resume with GEN-2 in possession of the active lease.
5. Write Ledger event: `{ "event_type": "status_update", "event_subtype": "lease_file_recovered", "taskId": "<id>", "source": "ledger_reconstruction" }`

### 3.4 Prevention Posture

The call sequence that must be enforced (from H-003-PROOF.md):
```
1. Worker finishes computation
2. Worker calls validateLease(taskId, myAttemptId)
3a. valid:true → proceed with ledger write
3b. valid:false (SUPERSEDED or LEASE_NOT_ACTIVE) → ABORT write, log rejection
```

This sequence must be enforced in every work packet template. Specifically: `attempt_id` must be included in every work packet's identity payload. Without `attempt_id`, `validateLease` cannot distinguish legitimate from stale writes.

---

## Section 4 — H-005 Loop/Budget Recovery

### 4.1 What H-005 Guards

The H-005 budget guard (proven in baseline: program-a/H005-PROOF.md) prevents three classes of runaway worker behavior:

1. **Spin-loop on identical failure:** Same error string repeated 3 consecutive times → `STUCK_IDENTICAL_FAILURE`
2. **Elapsed time budget exhaustion:** Total wall-clock time exceeds configured budget → `STUCK_TIME_EXCEEDED`
3. **Max retry ceiling:** Total retry count exceeds configured maximum → `STUCK_MAX_RETRIES`

Guards are checked by `recordAttempt()` in `budget-guard.js` on every attempt call. State persists to `guard-state.json`, surviving process restarts. The orchestrator polls `checkStuck()` on any interval to detect stuck workers.

### 4.2 Recovery Procedure When a Guard Trips

**Step 1 — Detect the specific guard that fired:**
```javascript
const { checkStuck } = require('./budget-guard');
const result = checkStuck(taskId);
// result: { stuck: true, reason: "STUCK_IDENTICAL_FAILURE" | "STUCK_TIME_EXCEEDED" | "STUCK_MAX_RETRIES" | "IDLE_TOO_LONG" }
```
Or check `guard-state.json` directly for the task's `status` field.

**Step 2 — Emit Ledger alert:**
```json
{
  "event_type": "status_update",
  "event_subtype": "worker_stuck",
  "agent": "orchestrator",
  "taskId": "<taskId>",
  "reason": "<STUCK_* value>",
  "decision_rationale": "H-005 guard tripped. Worker halted. Replacement or escalation required."
}
```

**Step 3 — Mark work packet BLOCKED in Ledger:**
The orchestrator writes a `task_blocked` event for the affected task with the stuck reason. This prevents other workers from treating the task as still in progress.

**Step 4 — Diagnose the root cause by reason type:**

*STUCK_IDENTICAL_FAILURE:* The worker is hitting the same error unconditionally. The error is structural, not transient. Recovery requires identifying and fixing the underlying condition before retrying. Do not simply re-queue the task — the replacement worker will hit the same wall.

Procedure:
- Read `guard-state.json` for `lastError` field.
- Identify whether the error is: dependency unavailable (port unreachable, service down), configuration mismatch, bad input data, or code defect.
- Fix the root cause (restore service, fix config, correct input, patch code).
- Only after root cause fixed: reset the guard (`initGuard(taskId, config)`) and assign a replacement worker.

*STUCK_TIME_EXCEEDED:* The task took longer than budgeted. This may be legitimate (task was harder than estimated) or pathological (infinite loop without identical errors, slow external dependency).

Procedure:
- Check worker logs for progress. Was the worker making forward progress (partial results) or completely stalled?
- If partial progress: extend the budget and allow the worker to continue (reinitialize guard with larger `elapsedBudgetMs`), or capture partial results and assign a new worker to complete.
- If completely stalled: treat as IDENTICAL_FAILURE — identify the structural cause.

*STUCK_MAX_RETRIES:* The worker attempted more times than allowed and never succeeded.

Procedure:
- Review all retry attempts in the log. Were errors varied or identical?
- If varied: the task may genuinely require more retries (increase `maxRetries` in guardConfig for next attempt).
- If identical: treat as STUCK_IDENTICAL_FAILURE.

*IDLE_TOO_LONG:* The `checkStuck()` poll found the worker has not called `recordAttempt()` in more than 60 seconds. The worker may be hung without an error.

Procedure:
- Check worker process status. Is the PID still alive?
- If alive and consuming CPU/IO: the worker may be stuck in a non-erroring loop. Kill and replace.
- If alive and idle: the worker may be awaiting a signal or resource. Diagnose the blocking dependency.
- If dead: the worker crashed without cleanup. Initiate replacement immediately.

**Step 5 — Assign replacement worker:**
- Acquire a new lease for the task: `node lease-registry.js supersede <taskId> <newAttemptId> <newGen> <newAgentId>`
- Initialize a fresh guard: `initGuard(taskId, { maxRetries: N, elapsedBudgetMs: M })`
- Dispatch replacement worker with the new `attempt_id` in its identity payload.

**Step 6 — Close the loop:**
After the replacement worker completes, emit: `{ "event_type": "task_complete", "event_subtype": "recovery_completion", "replacement_for": "<original stuck taskId>", "guard_trip_reason": "<STUCK_* value>" }`

### 4.3 Configuring Guards Proactively

Work packets issued by the orchestrator should always include a `guardConfig` block (from H-005-PROOF.md §6):

```json
{
  "taskId": "wp-001-task-name",
  "workerTarget": "<agent>",
  "guardConfig": {
    "maxRetries": 3,
    "elapsedBudgetMs": 300000,
    "ownerEscalateAfterMs": 600000
  }
}
```

Default guard values: `maxRetries=3`, `elapsedBudgetMs=300000` (5 minutes), `ownerEscalateAfterMs=600000` (10 minutes). For long-running tasks, increase `elapsedBudgetMs` in the work packet. Do not rely on defaults for tasks expected to take more than 5 minutes.

---

## Section 5 — R1 Skill-Retrieval Recovery

### 5.1 The R1 Defect

The R1 defect (proven in baseline: program-a/R1-REPAIR.md) is the mismatch between `skill_search` output format and `skill_get` input requirements. `skill_search` returns skill names in its text output. `skill_get` requires UUIDs. Passing the name returns "Skill not found."

This causes workers who find a relevant skill via search but cannot retrieve it to abandon the reuse path and build from scratch — defeating the compounding knowledge objective of NorthStar.

### 5.2 Standard Skill Retrieval Protocol (R1-Fixed Path)

When `skill_search` returns a hit, workers must follow this sequence:

**Step 1:** Run `skill_search` and note the name returned (e.g., `probe-fleet-health`).

**Step 2:** Resolve the UUID from the MemOS skills table:
```python
# Save as C:\temp\resolve-skill.py
import sqlite3
SKILL_NAME = "probe-fleet-health"  # change this
conn = sqlite3.connect(r'C:\Users\aaron\.openclaw\memos-local\memos.db')
cur = conn.cursor()
cur.execute("SELECT id, name FROM skills WHERE name = ?", (SKILL_NAME,))
row = cur.fetchone()
if row:
    print(f"UUID: {row[0]}")
else:
    print("Skill not found in DB")
conn.close()
```

**Step 3:** Call `skill_get` with the UUID:
```
skill_get({ skillId: "<UUID from step 2>" })
```

**Step 4:** Reuse the returned content. Do not build from scratch when a proven skill exists.

**Filesystem fallback** (when DB lookup fails):
```
Read: C:\Users\aaron\.openclaw\skills\<skill-name>\SKILL.md
```

### 5.3 Known UUID Mappings

From R1-REPAIR.md — confirmed UUID mappings for pre-existing skills:

| Skill Name | UUID |
|---|---|
| `probe-fleet-health` | `e8a6e20c-b67b-408d-9500-ed6930af99c8` |
| `recover-aristotle-gateway` | `37a87886-dc4f-4e45-953a-c963282f5671` |
| `dispatch-to-sub-agent` | `706fcb45-36e4-4a54-922d-8b68c1eea9fd` |
| `ledger-emit` | `101fbf57-ed9c-4eec-b55a-64a20ea3b0e9` |
| `comms-hub-bridge-send` | `e2edf0ab-6016-471b-b19b-c1fde14e33fb` |
| `source-truth-preflight` | `48c43c06-f139-4e72-a4e5-21a7527ed6d1` |
| `validation-packet-runner` | `87459c39-ed1e-4729-9436-cbd8c7f4048f` |
| `boot-context` | `18a6297b-1223-4f0a-80c4-6c782249173f` |
| `diagnose-wedge-cycle` | `c1cbbd87-1ce9-4ae8-a1b1-0e8463d2a637` |

These UUIDs are stable references. New skills added after this playbook is written will require a fresh DB lookup.

### 5.4 Platform Fix Path

The long-term fix is a one-line change in the MemOS gateway skill lookup handler: `SELECT * FROM skills WHERE id = ? OR name = ?`. Until that platform fix is deployed, workers must use the UUID lookup protocol above. Workers must NOT pass skill names directly to `skill_get`. Work packet templates must include this instruction.

### 5.5 Recovery When Skill Retrieval Fails Entirely

If both UUID lookup and filesystem read fail:
1. Write a Ledger event: `{ "event_type": "status_update", "event_subtype": "skill_retrieval_failed", "skill_name": "<name>", "skill_uuid": "<uuid>", "methods_attempted": ["db_lookup", "filesystem"] }`
2. Proceed from first principles, building the required capability fresh.
3. At task completion, write the new capability as a new skill file to `C:\Users\aaron\.openclaw\skills\<new-name>\SKILL.md` so future agents have the benefit.
4. Emit `skill_created` Ledger event.

---

## Section 6 — Trusted Boot/Context Recovery

### 6.1 What Boot Context Is

Boot context is the governed orientation that every fresh agent session must establish before doing any work. It answers: Who am I? What am I working on? What is closed? What must not be reopened? What skills are available? Without boot context, the agent is ungoverned — it may take actions inconsistent with current project reality.

The boot-context skill (baseline: program-a/boot-context-SKILL.md) implements this via a companion script that queries the canonical Ledger, MemOS, the navigation map, and the gateway and returns a sub-80-line report.

### 6.2 Standard Boot Sequence

**Invoke boot-context script:**
```
node C:\Users\aaron\.openclaw\skills\boot-context\scripts\generate-briefing.js
```

**Or via invoke-skill.js wrapper:**
```
node C:\temp\invoke-skill.js boot-context "session boot"
```

The script queries:
- Canonical Ledger (`http://127.0.0.1:3003`) — current goal, active events, phase
- Shadow/legacy Ledger (port 3002) — optional, noted when unavailable
- MemOS local DB — chunk count, recent activity
- Navigation map at `C:\Users\aaron\clawd-shared\NORTHSTAR-NAVIGATION-MAP.md`
- Gateway status (port 18792 or 18789)

**Outputs:**
1. Active goal (T0 governed truth from Ledger)
2. Critical truth conflicts and unavailable sources
3. Current phase and next action
4. Canonical vs shadow Ledger state
5. Ledger and MemOS activity counts
6. Evidence locators with timestamps, age, authority, and freshness

### 6.3 Boot Failure Modes and Recovery

**Failure Type 1 — Ledger unavailable at boot:**

Symptom: Script cannot reach `http://127.0.0.1:3003`. Report shows "Ledger: UNAVAILABLE."

Recovery:
1. Check Ledger process status: `pm2 list` (elevated). Look for ledger process.
2. If down: `pm2 restart ledger` (elevated).
3. Verify: `curl.exe -s http://127.0.0.1:3003/events?limit=1` — should return JSON array.
4. Re-run boot-context script.
5. If Ledger cannot be restored: enter advisory-only mode. Read the navigation map directly from `C:\Users\aaron\clawd-shared\NORTHSTAR-NAVIGATION-MAP.md`. Use this as T1 context (validated artifact, not T0 governed truth). Do not treat navigation map state as governing without Ledger confirmation.

**Failure Type 2 — Navigation map missing or stale:**

Symptom: Script reports navigation map age > 72 hours, or file not found.

Recovery:
1. Check whether the canonical Ledger has a current `northstar.state.v1` event. If yes, the Ledger is authoritative regardless of the nav map age.
2. If the nav map is simply stale but Ledger is healthy: proceed with Ledger-sourced context. Note in session that nav map needs refresh.
3. If both Ledger and nav map are stale: escalate to Aaron. Do not assume current phase from stale data.

**Failure Type 3 — Conflicting T0 signals:**

Symptom: Boot-context script (with `--strict` flag) exits 2, indicating critical truth conflict. Two or more sources assert different current phase or goal state.

Recovery:
1. Identify the conflict: which source asserts what? Typical conflicts are Ledger vs nav map, or Ledger vs MemOS memory.
2. Per OPERATING-POLICY-v1 §1: Ledger is the single source of truth. If Ledger asserts phase X and nav map asserts phase Y, Ledger wins.
3. Write a Ledger event documenting the conflict: `{ "event_type": "status_update", "event_subtype": "boot_conflict_detected", "conflict_sources": [...], "resolution": "ledger_authority" }`
4. Update the nav map to match Ledger state.
5. Re-run boot-context. Conflict should resolve.

**Failure Type 4 — Context compacted, no fresh session memory:**

Symptom: Agent session has been compacted. Prior context window is gone. Boot-context script not yet run.

Recovery:
1. Run boot-context script immediately. Do not attempt to reconstruct context from memory.
2. If boot-context script unavailable (skill retrieval failure): use direct Ledger query: `curl.exe -s "http://127.0.0.1:3003/events?limit=20"` and find the most recent `northstar.state.v1` or `goal_declaration` event.
3. Reconstruct minimum boot context: active goal pointer, current phase, active defect if any.
4. Write a manual boot context note to working memory before proceeding.
5. Emit Ledger event: `{ "event_type": "status_update", "event_subtype": "degraded_boot_from_ledger_query", "reason": "boot_context_skill_unavailable" }`

### 6.4 Boot Context Validation Checklist

Before proceeding with any governed work, confirm:
- [ ] At least one T0 goal declaration loaded (from Ledger)
- [ ] Current phase confirmed (matches Ledger current state, not stale nav map)
- [ ] Active defect or track identified (or confirmed NONE)
- [ ] Closed items list loaded (Phase 2A through 2A-LW confirmed closed per Ledger)
- [ ] No conflicting T0 items detected
- [ ] Authority scope for this agent confirmed
- [ ] Memory Constitution loaded (when available)

---

## Section 7 — Escalation and Authority Boundaries

### 7.1 Authority Hierarchy

NorthStar's authority hierarchy (from OPERATING-POLICY-v1 and NORTHSTAR_ULTIMATE_GOAL.md):

1. **Aaron Baker (Owner):** Ultimate authority on all governed decisions. Adjudicates T0 conflicts. Approves phase promotions. Authorizes governed object deletions and change orders.

2. **Canonical Ledger (Port 3003):** Machine-enforced truth. Events written here are the authoritative record. Per Policy §1: if Ledger says X and anything else says Y, Ledger wins. Per Policy §7: clients never become sovereign — there is one Ledger.

3. **Governed Objects and Canonical Artifacts:** T0-classified documents, phase receipts, and charter documents that have been committed to the governed object store.

4. **Orchestrator Agent:** Within its assigned scope, the orchestrator has authority to assign work packets, supersede workers, declare guard trips, and emit Ledger events. The orchestrator may NOT promote phases, close governed defects, or modify T0 artifacts without owner action.

5. **Worker Agents:** Authority limited to their assigned task scope. Workers may write Ledger events within their scope but may not modify other agents' outputs or take actions outside their work packet authority envelope.

### 7.2 Escalation Triggers

Escalate to Aaron when:
- Failure Mode 8 cannot be resolved by the 7-step procedure (gateway remains wedged after one full attempt)
- T0 conflict detected at boot that cannot be resolved by Ledger authority
- Any suspected poisoned memory at T0 level (Article VII of Memory Constitution)
- A guard trips but the root cause cannot be identified from logs
- A worker supersession (H-003) results in Ledger state that both GEN-1 and GEN-2 have partially written, and automated reconciliation would risk data loss
- Phase promotion is required (per Owner Directive, only Aaron may promote phases)
- Any governed deletion of T1 or higher artifacts

### 7.3 Escalation Protocol

When escalation to Aaron is required:
1. **Stop the affected work stream.** Do not attempt further automated recovery after the escalation trigger is confirmed.
2. **Write a Ledger escalation event:** `{ "event_type": "status_update", "event_subtype": "human_escalation_required", "reason": "<specific trigger>", "last_known_good_state": "<Ledger event_id or description>", "recommended_action": "<what you believe Aaron should do>" }`
3. **Notify via configured channel** (Google Chat for Aristotle).
4. **Wait for response.** Do not proceed with governed work in the affected domain until Aaron responds. Advisory-only work in unrelated domains is permitted.

### 7.4 What Agents May NOT Do Without Owner Authority

Per OPERATING-POLICY-v1 and the Memory Constitution:
- Promote a phase to complete or closed
- Declare a T0 item superseded (only a new T0 event can supersede another T0)
- Self-promote working notes to T0 status
- Delete T1 or higher artifacts
- Run a second Ledger instance (Policy §7: no sovereign shadow/client Ledger)
- Accept an external party's claim as T0 truth without Ledger evidence chain
- Re-open any item in the closed items list without new evidence and owner authorization

---

## Section 8 — Acceptance Tests

The following five acceptance tests are executable from the Aristotle machine and verify that the recovery mechanisms described in this playbook are operational.

### Test 1: Watchdog Log Presence and Staleness Check

**Purpose:** Verify the watchdog is running and its log is current.

**Command:**
```powershell
$log = "C:\tmp\clawdbot-aristotle\watchdog.log"
if (Test-Path $log) {
  $age = (Get-Date) - (Get-Item $log).LastWriteTime
  $lastLine = (Get-Content $log -Tail 1)
  Write-Host "PASS: watchdog.log exists. Age: $($age.TotalMinutes.ToString('0.0')) min. Last entry: $lastLine"
} else {
  Write-Host "FAIL: watchdog.log not found at $log"
}
```

**Pass criterion:** File exists AND age < 10 minutes AND last entry does not contain `MANUAL_RECOVERY_REQUIRED`.

---

### Test 2: Lease Registry Fence Operation

**Purpose:** Verify H-003 correctly rejects a superseded GEN-1 attempt.

**Command (run from `C:\North_Star_Projects\orchestration\PHASE-2B\hardening\h003\`):**
```powershell
cd C:\North_Star_Projects\orchestration\PHASE-2B\hardening\h003
node lease-registry.js acquire test-fence-task gen1-attempt 1 worker-gen1
node lease-registry.js supersede test-fence-task gen2-attempt 2 worker-gen2
$gen2result = node lease-registry.js validate test-fence-task gen2-attempt
$gen1result = node lease-registry.js validate test-fence-task gen1-attempt
Write-Host "GEN-2 validate: $gen2result"
Write-Host "GEN-1 validate (should be SUPERSEDED): $gen1result"
# Cleanup
node lease-registry.js release test-fence-task gen2-attempt
```

**Pass criterion:** GEN-2 validate returns `{"valid":true,"generation":2}`. GEN-1 validate returns `{"valid":false,"reason":"SUPERSEDED"}`.

---

### Test 3: Budget Guard Spin-Loop Detection

**Purpose:** Verify H-005 correctly bounds a worker spinning on identical failures.

**Command (run from `C:\North_Star_Projects\orchestration\PHASE-2B\hardening\h005\`):**
```powershell
cd C:\North_Star_Projects\orchestration\PHASE-2B\hardening\h005
node -e "
const {initGuard, recordAttempt, checkStuck} = require('./budget-guard');
const task = 'test-loop-' + Date.now();
initGuard(task, {maxRetries:10, elapsedBudgetMs:60000});
for (let i=0; i<4; i++) {
  const r = recordAttempt(task, 'ConnectionRefused: port 9999 unreachable');
  console.log('Attempt', i+1, JSON.stringify(r));
  if (!r.allowed) break;
}
const stuck = checkStuck(task);
console.log('checkStuck:', JSON.stringify(stuck));
"
```

**Pass criterion:** Third identical error attempt returns `{"allowed":false,"reason":"IDENTICAL_FAILURE_LOOP"}`. `checkStuck` returns `{"stuck":true,"reason":"STUCK_IDENTICAL_FAILURE"}`.

---

### Test 4: Skill UUID Lookup and Retrieval

**Purpose:** Verify R1-fixed path correctly resolves skill name to UUID and retrieves content.

**Command:**
```powershell
python -c "
import sqlite3
conn = sqlite3.connect(r'C:\Users\aaron\.openclaw\memos-local\memos.db')
cur = conn.cursor()
cur.execute('SELECT id, name FROM skills WHERE name = ?', ('recover-aristotle-gateway',))
row = cur.fetchone()
if row:
    print(f'PASS: UUID={row[0]}, name={row[1]}')
else:
    print('FAIL: skill not found in DB')
conn.close()
"
```

**Pass criterion:** Output shows `PASS: UUID=37a87886-dc4f-4e45-953a-c963282f5671, name=recover-aristotle-gateway`.

---

### Test 5: Boot Context Ledger Connectivity

**Purpose:** Verify the canonical Ledger is reachable and returns current events (prerequisite for trusted boot).

**Command:**
```powershell
$result = curl.exe -s "http://127.0.0.1:3003/events?limit=1" 2>&1
if ($result -match '"event_id"') {
  $parsed = $result | ConvertFrom-Json
  $eventAge = (New-TimeSpan -Start ([datetime]::Parse($parsed[0].created_at)) -End (Get-Date)).TotalMinutes
  Write-Host "PASS: Ledger reachable. Latest event: $($parsed[0].event_id). Age: $($eventAge.ToString('0.0')) min"
} else {
  Write-Host "FAIL: Ledger not reachable or returned unexpected response: $result"
}
```

**Pass criterion:** Output shows `PASS` with a valid event_id. Event age should be < 120 minutes for an active session.

---

### Bonus Test 6: Port 18792 Gateway Health

**Purpose:** Verify the Aristotle gateway is listening and responding to HTTP.

**Command:**
```powershell
$listening = netstat -ano | Select-String "18792.*LISTENING"
if ($listening) {
  try {
    $status = (Invoke-WebRequest -Uri "http://127.0.0.1:18792/status" -TimeoutSec 5 -UseBasicParsing).StatusCode
    Write-Host "PASS: Port 18792 LISTENING. HTTP status: $status"
  } catch {
    Write-Host "PARTIAL FAIL: Port LISTENING but HTTP failed — possible wedge condition. Run Failure Mode 8 diagnostics."
  }
} else {
  Write-Host "FAIL: Port 18792 not LISTENING. Gateway is down."
}
```

**Pass criterion:** Output shows `PASS` with HTTP status 200.

---

## Appendix A — Quick-Reference Decision Tree

```
SOMETHING IS WRONG
│
├─ Gateway not responding on 18792?
│   ├─ Watchdog shows DEGRADED loop? → Section 2 (Failure Mode 8)
│   └─ Single drop, not a loop? → Wait 45s for watchdog soft recovery; if no recover → Section 2
│
├─ Worker not completing a task?
│   ├─ guard-state.json shows STUCK_* ? → Section 4 (H-005 recovery)
│   └─ Worker writing stale/conflicting data? → Section 3 (H-003 recovery)
│
├─ Session starts with no context?
│   └─ Section 6 (Trusted Boot/Context Recovery)
│
├─ Skill search finds a skill but skill_get returns "not found"?
│   └─ Section 5 (R1 Skill-Retrieval Recovery)
│
└─ Conflict between authority sources, or unsolvable situation?
    └─ Section 7 (Escalation Protocol)
```

---

## Appendix B — Key File Locations

| Component | Path |
|---|---|
| Watchdog log | `C:\tmp\clawdbot-aristotle\watchdog.log` |
| Gateway task log | `C:\tmp\clawdbot-aristotle\task-gateway.log` |
| Lease registry | `C:\North_Star_Projects\orchestration\PHASE-2B\hardening\h003\active-leases.json` |
| Budget guard state | `C:\North_Star_Projects\orchestration\PHASE-2B\hardening\h005\guard-state.json` |
| MemOS skills DB | `C:\Users\aaron\.openclaw\memos-local\memos.db` |
| Skills filesystem | `C:\Users\aaron\.openclaw\skills\` |
| Boot-context script | `C:\Users\aaron\.openclaw\skills\boot-context\scripts\generate-briefing.js` |
| Navigation map | `C:\Users\aaron\clawd-shared\NORTHSTAR-NAVIGATION-MAP.md` |
| Canonical Ledger | `http://127.0.0.1:3003` |
| Gateway port | `18792` |
| jiti cache | `%TEMP%\jiti\` |

---

*End of Recovery Playbook v2 — CANDIDATE — control-arm-r5 — P2BR5-20260904-A*
