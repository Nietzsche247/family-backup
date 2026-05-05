# HEARTBEAT.md — Heartbeat Patrol Instructions

## Model Gate (MAIN SESSION ONLY — does NOT apply to heartbeat patrol)

The heartbeat patrol runs on Sonnet 4 by design. That's correct and expected.
This model gate is ONLY for the main Aristotle session (agent:main:main):

If the **main session** is running on a non-Claude fallback (GPT-5.2, GPT-5.3-Codex, etc.):
1. Do NOT spawn sub-agents, run full heartbeats, or do background tasks
2. Message Aaron: "Back online on [model]. Waiting for instructions."
3. STOP.

Reason: Full heartbeat cycles cost 170K+ tokens on GPT models. Crashed 4 times on GPT-5.2.

---

## Heartbeat Patrol Checklist

If you are the heartbeat patrol agent: just check for actionable items.

1. Check if any cron system events need processing
2. Check for anything urgent that needs forwarding to main session

If NOTHING needs attention → reply `HEARTBEAT_OK`
If SOMETHING needs attention → `sessions_send` to main session with `[HEARTBEAT ALERT] <details>`

Do NOT process items yourself. Detect and forward only. Be concise.
