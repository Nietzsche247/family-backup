# KEYRING.md — Canonical Shared Key Ring
# All agents read this. Aaron never relays a key again.
# Updated: 2026-04-07
# IMPORTANT: This file is excluded from MemPalace indexing.

---

## HOW TO USE THIS FILE

**Local agents (AlienWare2025):** Read directly from `C:\Users\aaron\clawd-shared\KEYRING.md`
**Remote agents (NIETZSCHE2025, etc.):**
```
Invoke-RestMethod -Uri "https://hub.stigmergy.space/files/KEYRING.md" -Headers @{Authorization="Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27"}
```
Or via curl:
```bash
curl -H "Authorization: Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27" https://hub.stigmergy.space/files/KEYRING.md
```

**Bootstrap key (hardcode this one — it unlocks everything else):**
`FILE_SERVER_API_KEY = wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27`

---

## COMMS HUB

| Key | Value |
|-----|-------|
| Hub URL | https://hub.stigmergy.space |
| ENV_API_KEY | wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27 |
| FILE_SERVER_API_KEY | wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27 |
| File server base | https://hub.stigmergy.space/files/ |
| Env registry | GET https://hub.stigmergy.space/api/env (Bearer ENV_API_KEY) |

---

## GATEWAY TOKENS (per-agent push delivery)

| Agent | Machine | Token |
|-------|---------|-------|
| aristotle | AlienWare2025 | 2461f6603a12be7834554741068559144df6921f7618d124 |
| plato | NIETZSCHE2025 | ad8703220cdfa6fcf6a9589dec3100c90be32537bc47cb28 |
| empiricus | nietzsche-i9 | 911a052c34fb55b170cd7d2ef3dd66ab8d9f11f5c88e088d |
| daedalus | AlienWare2025 | (none — same machine, no token needed) |
| thales | AlienWare2025 | (none — same machine, no token needed) |
| steelman | AlienWare2025 | (none — same machine, no token needed) |
| researcher | AlienWare2025 | (none — same machine, no token needed) |

---

## AI / MODEL API KEYS

| Service | Key | Notes |
|---------|-----|-------|
| OpenAI | [REDACTED_OPENAI_KEY] | text-embedding-3-large, memory search |
| OpenAI (2nd) | [REDACTED_OPENAI_KEY] | From env registry |
| xAI / Grok | [REDACTED_XAI_KEY] | From clawd-shared/[REDACTED_XAI_KEY].env |
| xAI (2nd) | [REDACTED_XAI_KEY] | From env registry — also used as OPENAI_API_KEY |
| Google AI / Gemini | [REDACTED_GOOGLE_KEY] | gemini-2.0-flash, gemini-2.5-pro |
| Anthropic | [REDACTED_ANTHROPIC_KEY] | Raw API key added 2026-06-12 |
| Brave Search | BSABrFgq3Pu_TKiWkCcAWt2jH8GzqIS | Web search API |
| Mem0 | [REDACTED_MEM0_KEY] | Vector memory |
| CapSolver | CAP-8D364C440207FAF4A5ED8D3CB5B10255C583629B337250545315E833E82BE52A | CAPTCHA solving, $10 balance |
| Moltbook | moltbook_sk_SvaAAMdhZHsTu0dtyvmyqnPf_KSnelbX | |

---

## BROWSER / AUTOMATION

| Key | Value |
|-----|-------|
| BROWSER_SERVER_URL | http://5.78.186.135:3000 |
| BROWSER_API_TOKEN | 7e2f60e94627aee2277e87b103e429cb629d6508b6624b4e |

---

## INFRASTRUCTURE SERVICES

| Service | Key/Value | Notes |
|---------|-----------|-------|
| BLM_API_URL | http://10.0.0.50:5000 | Plato/OpenClaw machine (LAN) |
| GOD_EYE_URL | https://god-eye.stigmergy.space | Shadowbroker OSINT dashboard |
| GitHub Token | [REDACTED_GH_CLASSIC] | Account: Nietzsche247 |
| GitHub Email | Aaron@omnipoolbuilders.com | |
| ClawhHub Token | clh_Y0jWOaf8jNYodVUsDH6AuE9duT6O0XImDkDrVT5ax7I | Account: @Nietzsche247 |

---

## DATABASE / BACKEND

| Service | Key/Value |
|---------|-----------|
| Supabase Project ID | xuwalxiznpdtvpczqokh |
| Supabase URL | https://xuwalxiznpdtvpczqokh.supabase.co |
| Supabase Anon Key | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh1d2FseGl6bnBkdHZwY3pxb2toIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU0MDQzNTIsImV4cCI6MjA4MDk4MDM1Mn0.eOcx2ekUIPtxlmYixd0K8HDRdRtNWvUhKdbu-oig8Lw |

---

## SLACK (Empiricus)

| Key | Value |
|-----|-------|
| Bot Token | [REDACTED_SLACK_BOT] |
| App Token | [REDACTED_SLACK_APP] |

---

## NETWORK / MACHINES

| Machine | LAN IP | Tailscale IP | Role |
|---------|--------|-------------|------|
| omni-alienware2025 | 208.111.34.11 | 100.108.47.36 | Core hub |
| nietzsche2025 | 10.0.0.50 | 100.73.106.82 | Plato's machine |
| nietzsche-i9 | 10.0.0.48 | 100.65.240.87 | Empiricus machine |

**SMB Share (LAN only — NOT over Tailscale relay):**
- Server: `\\10.0.0.50\shared`
- User: `NIETZSCHE2025\smbuser` / Password: `Password1`

---

## HOW TO ADD A NEW KEY

1. Edit `C:\Users\aaron\clawd-shared\KEYRING.md` directly (local)
2. Upload to file server:
   ```powershell
   Invoke-RestMethod -Uri "https://hub.stigmergy.space/files/upload" `
     -Method POST `
     -Headers @{Authorization="Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27"} `
     -Form @{file=Get-Item "C:\Users\aaron\clawd-shared\KEYRING.md"; path=""}
   ```
3. Done. All agents get it on next read — no TOOLS.md edits needed.

---

## MEMPALACE EXCLUSION

This file must NOT be indexed by MemPalace. If you see it being ingested, add to exclusion rules:
- Pattern: `KEYRING.md`
- Reason: Contains all credentials — not suitable for vector search

## Twilio SMS
| TWILIO_ACCOUNT_SID | ACd25eaa08f79a5d700062037c9c4b64a6 | Live account |
| TWILIO_API_KEY | SK1147b15d539accaba590eeb6aa61ee84 | API key SID |
| TWILIO_API_SECRET | uw9730iO7DzXpWH3nWh1aO32VTW8EojB | API key secret |
| TWILIO_TEST_SID | ACb189830e194a720a5084d8d0fd544875 | Test account |

## Telegram Bot
| TELEGRAM_BOT_TOKEN | 8904247689:AAF-OB8LASiyl8slOMvFyhfHU2cZgp_Ix4o | @Nietzsche247_bot |

##HANDWRITTEN API
f44943f30ce541e897901d6f5ae18e7e
