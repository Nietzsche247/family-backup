# Standard File Server Block — Copy Into Every Agent's TOOLS.md

Paste the section below into each agent's TOOLS.md (or equivalent persistent memory file).

---

### 📁 Shared File Server (clawd-shared on AlienWare2025)

All agents across all machines share files through the comms hub file server.

**Base URL:** `https://hub.stigmergy.space/files/`
**Auth:** `Authorization: Bearer <FILE_SERVER_API_KEY>` (get key from hub .env or your local .env)
**Local path (AlienWare agents only):** `C:\Users\aaron\clawd-shared\`

**Read a file:**
```bash
curl -H "Authorization: Bearer $KEY" https://hub.stigmergy.space/files/governed-objects/DEF-TB-001-FIX-BRIEF.md
```

**Browse directory:**
```bash
curl -H "Authorization: Bearer $KEY" https://hub.stigmergy.space/files/
curl -H "Authorization: Bearer $KEY" https://hub.stigmergy.space/files/governed-objects/
```

**Upload a file:**
```bash
curl -X POST -H "Authorization: Bearer $KEY" \
  -F "file=@/path/to/local/file.md" \
  -F "path=governed-objects" \
  https://hub.stigmergy.space/files/upload
```

**Directory structure:**
- `governed-objects/` — Defects, fix briefs, contracts, code reviews (canonical record)
- `tasks/` — Task queue (Aristotle creates, agents execute)
- `status/` — Agent status files
- `comms/` — Cross-agent communication logs
- `specs/` — Project specs, SOPs, architecture docs, handoffs
- `research/` — Research outputs, deep dives, arxiv scans
- `source-mirrors/` — Code snapshots (omnipools-repo, omnipools-src)
- `.env` — Shared secrets (API keys — never copy into other files)

**Rules:**
- Read `DIRECTORY-INDEX.md` before creating files — put things in the right place
- Secrets go in `.env` only — never in governed-objects or specs
- No delete endpoint — request cleanup from Aristotle or Aaron
- Always check if a file already exists before creating a duplicate

**Post-compaction recovery:**
1. Read `DIRECTORY-INDEX.md` first
2. Read `PROJECT_STATE.md` for current project status
3. Check `governed-objects/` for active work
4. Check `tasks/` for assignments
