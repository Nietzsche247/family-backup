# RAIL Pattern v1 — Skill Lifecycle Standard

> **Governed object.** Authority: T0 (Ledger-backed once first skill_invoked event lands).

## The Pattern

Every operational capability follows this lifecycle:

```
SKILL FILE → REGISTRATION → INVOCATION → LEDGER EVENT → RETRIEVABLE OUTPUT
```

### 1. Skill File
A SKILL.md with YAML frontmatter (`name`, `description`) containing:
- When to invoke
- Inputs / outputs
- Step-by-step procedure
- Ledger event shape
- Dependencies

**Location:** `~/.openclaw/skills/<skill-name>/SKILL.md`
**Also copied to:** `<workspace>/skills/<skill-name>/SKILL.md` (for prompt injection)

### 2. Registration
Skill must exist in BOTH:
- **Filesystem** (for `skill_manage` and prompt injection via `<available_skills>`)
- **MemOS SQLite store** (for `skill_search` and `skill_get`)

**L44:** `skill_manage` only writes filesystem. MemOS store must be populated separately via SQL INSERT into `skills` + `skill_versions` + `skills_fts` tables. See `clawd-shared/sql/register-skill.sql`.

### 3. Invocation
Call the skill via its procedure. On completion, emit a Ledger event.

**Current mechanism:** Manual invocation wrapper (`invoke-skill.js` pattern).
**Future:** Automated invocation tracking in the agent_end hook.

### 4. Ledger Event
```json
{
  "event_type": "status_update",
  "event_subtype": "skill_invoked",
  "agent": "<who>",
  "skill_name": "<name>",
  "skill_id": "<uuid>",
  "invoked_by": "<agent>",
  "invocation_id": "<uuid>",
  "input_summary": "<truncated>",
  "output_summary": "<truncated>",
  "success": true,
  "duration_ms": 70
}
```

**Note:** `skill_invoked` is not a native Ledger event_type. Uses `status_update` with `event_subtype: skill_invoked` until schema is extended.

### 5. Retrievable Output
Invocation output is captured via:
- MemOS chunks (through agent_end capture of the parent session)
- Ledger event payload (`output_summary` field)
- Optional: governed artifact file (e.g., `SOURCE-TRUTH-PREFLIGHT.md`)

---

## Worked Examples (Phase 2b, 2026-05-15)

### Example 1: recover-aristotle-gateway
| Step | Detail |
|------|--------|
| File | `~/.openclaw/skills/recover-aristotle-gateway/SKILL.md` |
| Registration | SQL INSERT, MemOS store id `37a87886-...` |
| Search | `skill_search "recover"` → found |
| Get | `skill_get(skillId="37a87886-...")` → full content |
| Invocation | 7-step procedure (manual, production-validated May 8-13) |

### Example 2: probe-fleet-health
| Step | Detail |
|------|--------|
| File | `~/.openclaw/skills/probe-fleet-health/SKILL.md` |
| Registration | SQL INSERT, MemOS store id `e8a6e20c-...` |
| Invocation | `invoke-skill.js probe-fleet-health` → Gateway UP, Ledger UP, CommsHub UP |
| Ledger Event | `01KRPRTFZF9GG5YXB5FB7QW7NP` (status_update/skill_invoked, 70ms, success=true) |
| AT-5 | Fresh sub-agent discovered via `skill_search("recover")` without context paste |

### Example 3: source-truth-preflight
| Step | Detail |
|------|--------|
| File | `~/.openclaw/skills/source-truth-preflight/SKILL.md` |
| Registration | SQL INSERT, MemOS store id `48c43c06-...` |
| Search | `skill_search "source truth"` → found |
| Invocation | (not yet tested against real project — Phase 4 first use) |

---

## The 5 Phase 2b Skills

| # | Skill | Search keyword | MemOS ID (prefix) |
|---|-------|---------------|-------------------|
| 1 | recover-aristotle-gateway | recover | 37a87886 |
| 2 | probe-fleet-health | probe | e8a6e20c |
| 3 | dispatch-to-sub-agent | dispatch | 706fcb45 |
| 4 | ledger-emit | ledger | 101fbf57 |
| 5 | comms-hub-bridge-send | bridge | e2edf0ab |
| 6 | source-truth-preflight | source truth | 48c43c06 |

---

## Known Gaps (parking lot)

- **R1:** skill_get fails on name, only UUID works
- **R2:** skill_manage doesn't write to MemOS store (L44)
- **Cross-agent:** MemOS stores are per-gateway; Daedalus can't find Aristotle's skills
- **Invocation tracking:** Manual wrapper, not automated in agent_end
- **skill_invoked event_type:** Not in Ledger schema, using status_update workaround
