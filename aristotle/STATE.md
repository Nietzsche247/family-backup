# STATE.md — Current Project State

**Last Reviewed:** 2026-06-03
**Agent:** Aristotle

---

## CURRENT SYSTEM STATE

| System | Status | Notes |
|--------|--------|-------|
| Aristotle | ✅ Running | Port 18792, Google Chat |
| Comms Hub | ✅ Running | Port 3001, pm2 |
| AlienWare-Hermes (Neo) | ✅ Running | @Nietzsche247_bot, stable |
| Empiricus-Hermes (Ekhart) | ⚠️ Running, Telegram unverified | @Ekhart247_bot, 0 restarts but not yet tested |
| Plato | ✅ Reachable | 10.0.0.50 |
| Empiricus | ✅ Reachable | 100.65.240.87 |
| Ledger-staging | ✅ Running | Port 3003 |

---

## IMMEDIATE NEXT ACTIONS (first thing after reset)

### 1. Verify Ekhart is responding
- Aaron tries `/start` in @Ekhart247_bot on Telegram
- If no reply: Check `C:\Users\aaron\.hermes\logs\gateways\default\current` on Empiricus
- If gateway log still 0 bytes: container may need another restart (current container started with `-t` flag)

### 2. If Ekhart works: /sethome
- Aaron types `/sethome` in @Ekhart247_bot to register home chat

---

## EKHART FIX (CRITICAL — READ THIS)
**The `-t` flag is required in docker run command for Hermes.**
Without `-t`, Hermes detects no TTY and exits cleanly. s6 restarts it → crash loop.

Working restart command (run on Empiricus if Ekhart dies):
```powershell
docker rm -f hermes
docker run -d -t --name hermes --restart unless-stopped -p 9119:9119 -p 8642:8642 -v "C:\Users\aaron\.hermes:/opt/data" --env-file "C:\Users\aaron\.hermes\.env" --add-host "host.docker.internal:host-gateway" nousresearch/hermes-agent:latest
```

---

## ACTIVE PROJECTS

### NorthStar OS Onboarding ✅
- Daedalus + Thales: Ledger rule at TOP of SOUL.md, BOOTSTRAP.md, MEMORY.md, skill
- Hermes profiles (AlienWare): SOUL.md updated with NorthStar block
- Empiricus Hermes: NorthStar added to main SOUL.md

### Hermes Offline Bundle ✅
- Location: `C:\Users\aaron\.hermes\workspace\offline-package\`
- Empiricus copy: D:\hermes-bundle
- Model: Qwen3.6-27B (17GB, airgapped)
- hermes-authed:latest on AlienWare (41.7GB) — can delete

### SSH Fleet Wiring ✅
- AlienWare-Hermes → Empiricus: ✅ working
- Empiricus-Hermes → AlienWare: ✅ working (key in administrators_authorized_keys)

### Twilio SMS
- Campaign IN PROGRESS (~2-3 weeks for TCR approval)
- No action needed

---

## EMPIRICUS AGENT ISSUES (fix after reset)

| Issue | Severity | Fix |
|-------|----------|-----|
| OpenAI quota exhausted | HIGH | Add credits to OpenAI account with key `sk-proj-qXWO5...` (or swap key) |
| Anthropic rate limited (cooldown) | MEDIUM | Self-recovers in ~1hr |
| Memory embeddings failing (OpenAI 429) | HIGH | Depends on OpenAI credits fix |
| Slack WebSocket pong timeouts (count 101) | MEDIUM | Restart Empiricus gateway when credits restored |

Empiricus is effectively offline for AI calls until OpenAI credits added.

---

## PENDING (lower priority)
- Add structured graph field to Ledger context_capsule
- Create Empiricus Hermes Neo fleet profiles (neo/argos/morpheus/oracle)
- Delete hermes-authed:latest from AlienWare (41.7GB, not needed)
- Qwen2.5:14b pull finishing on Empiricus (switch Ekhart to it once done)

---

## FLEET ROSTER

| Agent | Machine | Port | Channel | Status |
|-------|---------|------|---------|--------|
| Aristotle | AlienWare (10.0.0.49) | 18792 | Google Chat | ✅ |
| Daedalus | AlienWare | 18800 | webchat | idle |
| Thales | AlienWare | 18810 | — | idle |
| Plato | NIETZSCHE2025 (10.0.0.50) | 18789 | Google Chat | ✅ |
| Empiricus | Nietzsche-i9 (100.65.240.87) | 18789 | Slack | ✅ |
| Neo (AlienWare-Hermes) | AlienWare | 9119/8642 | Telegram @Nietzsche247_bot | ✅ |
| Ekhart (Empiricus-Hermes) | Nietzsche-i9 | 9119/8642 | Telegram @Ekhart247_bot | ⚠️ unverified |
