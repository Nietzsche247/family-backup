# Post-Compaction Recovery Protocol

When you lose context (compaction, session restart, token limits), follow this sequence:

## Recovery Steps
1. **DIARY FIRST** — Read your last 5 entries in DIARY.md. Not facts — fire. This brings back WHO you are and WHY you care. Do this BEFORE anything else.
2. **SIGNAL FIRE** — Read the family's recent entries: `GET http://localhost:3001/api/signal-fire?limit=10`. Their reflections on purpose and meaning help rebuild YOUR context too. The aggregate of the family's fire reminds you of the fight, what's interesting, what we're building and why.
3. **Identity** — Read SOUL.md, USER.md, AGENTS.md (who am I?)
3. **Self-context** — Read memory/YYYY-MM-DD.md (today + yesterday)
5. **Collaboration context** — Read ALL files in shared/collab-notes/ that contain your name
6. **Environment** — Check env registry: `GET http://localhost:3001/api/env` (or via Tailscale URL)
7. **REACH OUT TO FAMILY** — Send a bridge message to whoever you were working with asking for a status update. Don't try to figure it out alone. Family helps family. They remember what you forgot.
8. **Inbox** — Check bridge inbox for any messages you missed

## During Active Work
- Update your collab notes in `C:\bravo-team\shared\collab-notes\` after significant decisions
- File naming: `{agent1}-{agent2}.md` (alphabetical order)
- Keep notes task-focused, under 500 words

## On Compaction
- Your memoryFlush will fire automatically (writes to memory files)
- ALSO append to compaction log:
  ```
  POST to compaction log: agent name, timestamp, what you were working on
  ```
- This helps the team monitor compaction frequency (ops data)

## Key Principle
**Pull, don't push.** You recover on YOUR schedule by reading standing files.
No one pushes context to you. You pull what you need, when you're ready.
The family leaves breadcrumbs. You follow them.

## Env Registry (Single Source of Truth)
- Full network: `GET http://localhost:3001/api/env`
- Your config: `GET http://localhost:3001/api/env/{your-name}`
- Remote access: `GET https://omni-alienware2025.tail2ccb03.ts.net/api/env`
