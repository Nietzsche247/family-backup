# STATE.md — Current Project State

**Last Reviewed:** 2026-05-30
**Agent:** Aristotle
**Status:** Active

---

## CURRENT SYSTEM STATE

| System | Status | Notes |
|--------|--------|-------|
| Aristotle gateway | ✅ Running | Port 18792, Google Chat channel |
| Comms Hub | ✅ Running | Port 3001, pm2 |
| Hermes Agent | ✅ Running | Port 9119/8642, Docker, grok-4.3 |
| Neo fleet (4 profiles) | ✅ Built | neo/argos/morpheus/oracle in Hermes |
| @Nietzsche247_bot (Telegram) | ✅ Live | Home channel set, native Hermes |
| Plato | ✅ Reachable | 10.0.0.50, SSH + gateway |
| Empiricus | ✅ Reachable | 100.65.240.87, Tailscale SSH |
| Ledger | ⚠️ Stopped | pm2 shows stopped, not critical right now |

---

## ACTIVE PROJECT: Hermes + Neo Fleet

### What's done
- [x] Hermes deployed, local terminal, yolo mode, 85 skills
- [x] GitHub auth (Nietzsche247), SSH fleet access
- [x] 4-agent Neo fleet (neo/argos/morpheus/oracle) with SOUL.md + temperatures
- [x] Telegram C2 (@Nietzsche247_bot, home channel set)
- [x] Twilio credentials wired everywhere ($219 balance)
- [x] pyFlipper installed, Flipper Zero 90% ready
- [x] Red team research complete (tools, OSINT, pen test workflow)
- [x] hermes-agent-deploy skill v2.0 — full reproducible playbook
- [x] Go 1.24 installed in Hermes container

### What's pending (in priority order)
- [ ] **A2P 10DLC registration** OR buy toll-free Twilio number → SMS actually delivers
- [ ] **Verify recon tools** (subfinder, nuclei, httpx, ffuf) in `/root/go/bin/` — install may have completed
- [ ] **Fix Python lib installs** (impacket, scapy) — hit permission issues, retry with correct flags
- [ ] **Flipper Zero live test** — Android tablet USB OTG → Termux → WebSocket bridge
- [ ] **Neo Kanban end-to-end test** — give Neo a real task, watch Argos execute, verify completion
- [ ] **Google Workspace OAuth** — unlocks google-workspace skill (PARTIAL in skill test)
- [ ] **X/Twitter API key** — unlocks xurl skill
- [ ] **VPN stack** — Gluetun + ProtonVPN for pen testing anonymization

---

## NEXT SESSION STARTUP

1. Check if recon tools installed: `docker exec hermes ls /root/go/bin/`
2. Fix impacket: `docker exec hermes pip3 install impacket --break-system-packages --no-build-isolation`
3. Give Neo a real test task via Kanban or direct Telegram message
4. A2P registration decision with Aaron

---

## FLEET ROSTER

| Agent | Machine | Port | Channel | Status |
|-------|---------|------|---------|--------|
| Aristotle | Omni-AlienWare2025 | 18792 | Google Chat | ✅ |
| Daedalus | Omni-AlienWare2025 | 18800 | webchat | idle |
| Thales | Omni-AlienWare2025 | 18810 | — | idle |
| Steel Man | Omni-AlienWare2025 | 18820 | — | idle |
| Researcher | Omni-AlienWare2025 | 18830 | — | idle |
| Plato | NIETZSCHE2025 (10.0.0.50) | 18789 | Google Chat | ✅ |
| Empiricus | Nietzsche-i9 (100.65.240.87) | 18789 | Slack | ✅ |
| Hermes/Neo | Omni-AlienWare2025 | 9119/8642 | Telegram | ✅ |

---

## KEY RESOURCES

- **KEYRING:** `C:\Users\aaron\clawd-shared\KEYRING.md` + `https://hub.stigmergy.space/files/KEYRING.md`
- **Hermes skill:** `C:\Users\aaron\.openclaw\skills\devops\hermes-agent-deploy\SKILL.md`
- **Red team research:** `C:\Users\aaron\clawd-researcher\memory\2026-05-29-red-team-tools.md`
- **Neo fleet prompts:** `C:\Users\aaron\clawd-researcher\memory\2026-05-29-neo-fleet-prompts.md`
- **Steel Man critique:** `C:\Users\aaron\clawd-steelman\memory\2026-05-29-neo-fleet-critique.md`
