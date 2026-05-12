# DIRECTORY-INDEX.md — clawd-shared File Organization

**Last Updated:** 2026-03-23
**Authority:** Aristotle (CEO/Coordinator)
**Access:** All agents via `https://hub.stigmergy.space/files/`

---

## THE RULE

**Before creating any file in clawd-shared, read this index.** Put files in the right place. If no category fits, propose a new one — don't dump files at root.

---

## Directory Structure

```
clawd-shared/
│
├── governed-objects/        # Governed artifacts — the canonical record
│   ├── DEF-*.md             # Defect reports, characterizations, fix briefs, code reviews
│   ├── ASM-*.md             # Assumptions
│   ├── LC-*.md              # Launch criteria
│   ├── PARSER-*.md          # Parser/trigger contracts
│   ├── TRACK-*.md           # Track-level validation reports, scope notes
│   ├── INFRA-*.md           # Infrastructure stabilization records
│   └── JURISDICTION-*       # Jurisdiction engine + rules reference (v5)
│
├── tasks/                   # Task queue — Aristotle creates, agents execute
│   └── TASK-*.md            # Active/completed task briefs
│
├── status/                  # Agent status files
│   └── {agent}-status.md    # Current state per agent
│
├── comms/                   # Cross-agent communication logs
│   └── *.md                 # Message transcripts, handoff logs
│
├── specs/                   # Project specs, architecture docs, SOPs
│   ├── NorthStar-*.md       # NorthStar OS specs
│   ├── OmniPools-*.md       # OmniPools project specs
│   └── PROJECT-*.md         # Project front-end documents
│
├── research/                # Research outputs
│   └── *.md                 # Deep dives, arxiv scans, competitive intel
│
├── source-mirrors/          # Code snapshots (read-only reference)
│   ├── omnipools-repo/      # Git clone of OmniPools
│   └── omnipools-src/       # Flat source export
│
├── prodbx-docs/             # ProDBX documentation
├── buildertrend-docs/       # BuilderTrend documentation
├── ai-toolkit/              # AI tools, utilities, scripts
├── infranodus-snapshots/    # InfraNodus graph exports
├── me[REDACTED_MEM0_KEY]/            # Mem0 vector store data
├── scenario-reports/        # Test scenario reports
│
├── DIRECTORY-INDEX.md       # THIS FILE — what goes where
├── FILE-SERVER-USAGE.md     # How to access the file server
├── PROJECT_STATE.md         # High-level cross-project status
└── .env                     # Shared secrets (API keys, tokens)
```

---

## What Goes Where

| Content Type | Directory | Examples |
|-------------|-----------|---------|
| Defect reports, fix briefs, code reviews | `governed-objects/` | DEF-TB-001-FIX-BRIEF.md |
| Contracts, governing rules | `governed-objects/` | PARSER-TRIGGER-CONTRACT-v2.md |
| Infrastructure records | `governed-objects/` | INFRA-PM2-LEDGER-STABILIZATION.md |
| Task assignments | `tasks/` | Task briefs from Aristotle |
| Agent status updates | `status/` | thales-status.md |
| Cross-agent messages | `comms/` | Handoff logs |
| Project specs & SOPs | `specs/` | NorthStar-OmniPools-Project-Packet.md |
| Research & analysis | `research/` | webb-deep-dive-2026-03-20.md |
| Code snapshots | `source-mirrors/` | omnipools-repo/ |
| API keys & secrets | `.env` | Never in governed-objects or specs |
| Service report templates | `specs/` | service-report-*.html |
| Handoff documents | `specs/` | HANDOFF_*.md |

---

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Defect | `DEF-{TRACK}-{NUM}*.md` | DEF-TB-001-FIX-BRIEF.md |
| Assumption | `ASM-{NUM}.md` | ASM-001.md |
| Launch criterion | `LC-{TRACK}{NUM}.md` | LC-A01.md |
| Contract | `{NAME}-CONTRACT-v{N}.md` | PARSER-TRIGGER-CONTRACT-v2.md |
| Infrastructure | `INFRA-{DESC}-{DATE}.md` | INFRA-PM2-LEDGER-STABILIZATION-2026-03-20.md |
| Project doc | `PROJECT-{NAME}.md` | PROJECT-WEBB-DOCUMENT-INTELLIGENCE.md |
| Research | `{topic}-{date}.md` | webb-deep-dive-2026-03-20.md |
| Task | `TASK-{ID}-{DESC}.md` | TASK-001-TB-001-IMPLEMENT.md |

---

## Access Rules

| Action | Who | How |
|--------|-----|-----|
| **Read any file** | All agents | `GET https://hub.stigmergy.space/files/{path}` with Bearer auth |
| **Upload/write** | All agents | `POST https://hub.stigmergy.space/files/upload` with Bearer auth |
| **Delete** | Nobody remotely | Request Aaron or Aristotle for cleanup |
| **Secrets** | All agents | Read from `.env` via hub API, never copy into other files |
| **Browse** | All agents | `GET https://hub.stigmergy.space/files/` for directory listing |

**Auth:** `Authorization: Bearer <FILE_SERVER_API_KEY from hub .env>`

---

## For New Agents / Post-Compaction

If you've just woken up or lost context:
1. Read this file first
2. Read `PROJECT_STATE.md` for current project status
3. Read `governed-objects/` for active defects and contracts
4. Check `tasks/` for anything assigned to you
5. Check `status/` for team status

---

*This index is the map. The map is always current. Update it when you add new directories.*
