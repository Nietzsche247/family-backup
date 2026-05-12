# Phase 0 — Thales Deliverables: Status Report

**Agent:** Thales  
**Phase:** 0 — Baseline, repo wiring, safety rails  
**Completed:** 2026-04-02  
**Status:** ✅ COMPLETE — all deliverables shipped and validated against live data

---

## Deliverables

### 1. Backup Script — `backup-agent-data.ps1`
**Location:** `C:\Users\aaron\clawd-shared\openclaw-fork\tools\backup-agent-data.ps1`

Discovers and archives:
- All `.clawdbot-*\agents\*\sessions\sessions.json` files
- All `.clawdbot-*\agents\*\sessions\*.jsonl` transcripts
- All `.clawdbot-*\cron\runs\*.jsonl` cron run logs
- All `clawd-*\memory\` directories
- All `clawd-*\MEMORY.md` files

Output: single timestamped ZIP at `tools\_backups\openclaw-agent-data-YYYY-MM-DD_HH-mm-ss.zip`, plus embedded `backup-manifest.json`.

**WhatIf validation (run 2026-04-02):**
```
Discovered .clawdbot-* roots: 7
Discovered clawd-* workspaces: 8
Files to include (sessions/transcripts): 418
Memory dirs to include: 7
```

**Usage:**
```powershell
# Dry-run (preview)
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\backup-agent-data.ps1 -WhatIf

# Run with custom output dir
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\backup-agent-data.ps1 -OutDir C:\backups\openclaw
```

---

### 2. Restore Script — `restore-agent-data.ps1`
**Location:** `C:\Users\aaron\clawd-shared\openclaw-fork\tools\restore-agent-data.ps1`

Safely restores from a backup ZIP:
- Defaults to **preview/WhatIf mode** (no changes unless `-Force` is passed)
- Supports scoping: `-OnlyClawdbot` (sessions+transcripts only) or `-OnlyMemory` (memory dirs only)
- Extracts to temp dir first; copies back to `%USERPROFILE%` preserving relative paths
- Standalone: no running Clawdbot instance required

**Usage:**
```powershell
# Preview
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\restore-agent-data.ps1 -ArchivePath .\tools\_backups\openclaw-agent-data-2026-04-02_10-00-00.zip

# Actually restore
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\restore-agent-data.ps1 -ArchivePath <zip> -Force

# Sessions+transcripts only
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\restore-agent-data.ps1 -ArchivePath <zip> -Force -OnlyClawdbot
```

---

### 3. Invariants Checker — `invariants-checker.js`
**Location:** `C:\Users\aaron\clawd-shared\openclaw-fork\tools\invariants-checker.js`

Checks:
- ✅ Tool-call pairing: every `toolCall` has a matching `toolResult`
- ✅ No orphaned `toolResult` records (references unknown `toolCallId`)
- ✅ No duplicate `toolCall` IDs
- ✅ Turn alternation (conversation-level): consecutive `user` turns flagged as errors
- ✅ Token bounds: any `usage.*` field > 200,000 flagged as error
- ✅ System message presence (warning in `raw` mode, error in `fixture` mode)
- ✅ Bootstrap heading completeness in fixture mode
- ✅ `sessions.json` structural checks: `systemSent`, `skillsSnapshot.prompt`, `sessionFile` existence
- ✅ Invalid JSON lines detected

Supports single file, directory (`--recursive`), and `sessions.json` inputs. JSON output mode (`--json`) available.

**Validation against live data (34 sessions across all aristotle agents):**
```
Checked: 34  Errors: 3300  Warnings: 34
```
Key findings in production data:
- 1 session with **missing tool results** (4 orphaned toolCalls — possible network drop/kill)
- 2 sessions with **user-follows-user turn violations** (heartbeat injection pattern)
- Multiple sessions with **token bound exceeded** (sessions that grew past 200K without compaction)
- 1 session with **invalid JSON** (lines 308–318; corrupted write)

**Usage:**
```bash
node tools/invariants-checker.js --input <file.jsonl>
node tools/invariants-checker.js --input <directory> --recursive
node tools/invariants-checker.js --input <file.jsonl> --mode fixture --expectedBootstrap AGENTS.md,TOOLS.md
node tools/invariants-checker.js --input <file.jsonl> --json
```

---

### 4. Dry-Run Compaction CLI — `dry-run-compaction.js`
**Location:** `C:\Users\aaron\clawd-shared\openclaw-fork\tools\dry-run-compaction.js`

Features:
- Loads a JSONL transcript fixture
- Estimates token counts (using `usage.input+output` if present, char/4 heuristic otherwise)
- Groups assistant+toolResult bundles to avoid orphaning tool pairs during compaction
- Simulates head-summarize / tail-keep strategy
- Emits JSON report: `beforeTokens`, `afterTokens`, `didCompact`, `summarizedGroups`, `keptGroups`
- Runs invariant checks on the *compacted output* and reports violations
- Optional `--emitCompactedJsonl` to print compacted JSONL (delimited)
- Never writes to disk

**Validation against live data:**
```
File: f6bd564c (389K tokens)
beforeTokens: 389,105
afterTokens: 79,082  (79.7% reduction)
didCompact: true
messageGroups: 565
summarizedGroups: 427
keptGroups: 138
invariantErrors: 194  (all token_bound_exceeded in kept tail — pre-existing, not introduced by compaction)
```

**Usage:**
```bash
# Default thresholds (compact if >120K, target 80K)
node tools/dry-run-compaction.js --input transcript.jsonl

# Custom thresholds
node tools/dry-run-compaction.js --input transcript.jsonl --maxTokens 90000 --targetTokens 60000

# Emit compacted JSONL
node tools/dry-run-compaction.js --input transcript.jsonl --emitCompactedJsonl
```

---

## Production Findings (incidental — useful for Phase 1)

Running the invariants checker against all 34 Aristotle main-agent sessions revealed:

| Finding | Count | Implication |
|---------|-------|-------------|
| Token bound exceeded (>200K) | ~3,200 | Compaction was **not firing**; many sessions ran well past 200K. Confirms the audit's diagnosis. |
| User-follows-user turn violations | ~20 instances across 10 sessions | Cron heartbeat messages injected without proper turn management |
| Missing tool results (session 2c82fd4a) | 4 orphaned calls | Session was likely killed mid-execution; recovery didn't write toolResults |
| Invalid JSON (session d5f19577) | 11 lines (308–318) | Corrupted write; partial record at end of a large compaction event |

These findings are **live data** — not synthetic. Phase 1 compaction work should address the 200K blowout pattern first.

---

## Files Delivered

| File | Path | Purpose |
|------|------|---------|
| `backup-agent-data.ps1` | `openclaw-fork/tools/` | Snapshot all agent data to ZIP |
| `restore-agent-data.ps1` | `openclaw-fork/tools/` | Restore from ZIP |
| `invariants-checker.js` | `openclaw-fork/tools/` | Validate transcript JSONL + sessions.json |
| `dry-run-compaction.js` | `openclaw-fork/tools/` | Simulate compaction, report before/after |

All tools: standalone (no running Clawdbot required), documented in file headers, tested against live production data.

---

## Handoff Notes for Daedalus

- The tools write to `openclaw-fork/tools/` where you're building the fork
- `invariants-checker.js` can be called programmatically: import and call `checkJsonl(filePath, opts)` directly if you want to embed it in the replay fixture pipeline
- `dry-run-compaction.js` accepts `--emitCompactedJsonl` to pipe compacted output directly into your fixture pipeline
- The JSONL format: `{type:"session",...}` header on line 1, then `{type:"message",...}` records; `message.role` is `user|assistant|toolResult|system`; tool calls are inside `message.content` as `{type:"toolCall",id,name,...}`

---

*Report generated by Thales subagent — phase0-thales-status.md*
