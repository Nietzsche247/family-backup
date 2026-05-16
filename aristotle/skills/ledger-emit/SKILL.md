---
name: ledger-emit
description: "Emit events to NorthStar Ledger (port 3003). Helper for memory_capture, task_completed, agent_recovery, goal_check events."
---

# Ledger Emit

## Endpoint
`POST http://127.0.0.1:3003/events` (Content-Type: application/json)

## Event Types
| Type | When |
|------|------|
| memory_capture | Auto: every agent_end (Phase 3 emitter) |
| task_completed | Manual: significant task done |
| agent_recovery | Manual: after recovery |
| configuration_change | Manual: infra changes |
| goal_check | Manual: goal alignment |

## Required Fields
```json
{"event_type": "task_completed", "agent": "aristotle", "decision_rationale": "Description"}
```

## Optional v1.2 Fields
```json
{"event_subtype": "routine_session_capture", "memory_chunk_id": "turnId reference"}
```

## Reliable Method (Node.js)
Write JSON to temp file, POST via http module. Never use curl for JSON bodies in PowerShell.

## Verification
`curl.exe -s "http://127.0.0.1:3003/events?limit=1"`
