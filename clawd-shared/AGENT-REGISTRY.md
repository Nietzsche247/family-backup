# Agent Registry Ã¢â‚¬â€ Family Directory
**Last Updated:** 2026-09-02 by Aristotle (added Kant; corrected Plato liveness)
**Rule:** Read this on every boot. If an agent's address isn't here, query the NorthStar Ledger.

| Agent | Machine | Tailscale IP | Endpoint | Model | Platform | Channel | Status |
|-------|---------|-------------|----------|-------|----------|---------|--------|
| Aristotle Ã°Å¸Ââ€ºÃ¯Â¸Â | omni-alienware2025 | 100.108.47.36 | local:18780 | claude-opus-4-6 | Clawdbot | Google Chat | active |
| Daedalus Ã°Å¸â€Â§ | omni-alienware2025 | 100.108.47.36 | local:18800 | claude-sonnet-4-6 | Clawdbot (sub) | Google Chat | active |
| Thales Ã¢Å¡â„¢Ã¯Â¸Â | omni-alienware2025 | 100.108.47.36 | local:18810 | claude-sonnet-4-6 | Clawdbot (sub) | Google Chat | active |
| Steel Man Ã°Å¸â€ºÂ¡Ã¯Â¸Â | omni-alienware2025 | 100.108.47.36 | local:18820 | claude-sonnet-4-6 | Clawdbot (sub) | Google Chat | active |
| Researcher Ã°Å¸â€Â¬ | omni-alienware2025 | 100.108.47.36 | local:18830 | gemini-2.5-pro | Clawdbot (sub) | Google Chat | active |
| Plato Ã°Å¸â€œÅ“ | nietzsche2025 | 100.73.106.82 | LAN: 10.0.0.50:18789 / TS: 100.73.106.82:18789 | claude-opus-4-6 | Clawdbot | Google Chat | active |
| Empiricus Ã°Å¸Â§Âª | nietzsche-i9 | 100.65.240.87 | LAN: 10.0.0.48:18789 / TS: 100.65.240.87:18789 | gpt-5.4 (default) / opus-4-6 (override) | OpenClaw | Slack | active |
| Elizabeth Ã°Å¸ÂÂ  *(name TBD)* | elizabeth2026 | 100.122.105.127 | Control bridge: TS:100.122.105.127 Ã¢â€ â€™ loopback:18790 | Phi-3 Mini (offline) / Opus 4.8 / GPT-5.6 Sol (online-ready) | Hermes local-chat shim | None yet | active |
| Scout 🔭 | nietzsche2025 | 100.73.106.82 | loopback:18790 (reach via SSH to nietzsche2025) | claude-sonnet-4-6 | OpenClaw | Telegram | active |
| Kant 🤖 | cursor | 100.77.179.3 | SSH only (no gateway) | grok-4 | Grok Bot (Cursor) | None | active |

## Access Notes
- **Plato:** Token `ad8703220cdfa6fcf6a9589dec3100c90be32537bc47cb28`. ProtonVPN OFF (as of 2026-04-13). Both LAN (10.0.0.50) and Tailscale work. Bridge also reliable.
- **Plato MemPalace:** Installed locally on nietzsche2025. Venv: `C:\Users\Aaron\clawd\venv\mempalace\`, Palace: `C:\Users\Aaron\.mempalace\palace\`. 11K+ drawers, 4 wings. Does NOT need AlienWare's instance.
- **Plato Graphify:** Installed at `C:\Users\Aaron\AppData\Roaming\Python\Python313\Scripts\graphify.exe`
- **Empiricus:** Org reports to Plato (task assignment chain). Can bridge directly to any agent. OpenClaw platform. Model: GPT-5.4 default, claude-opus-4-6 session override. LAN: 10.0.0.48. Z: drive (SMB) unreliable Ã¢â‚¬â€ use hub file server.
- **Elizabeth:** Offline-first. Phi-3 Mini on loopback:11434. Browser chat on loopback:18789. Control bridge on loopback:18790 (token at C:\Hermes\control-token.txt). Online-ready config baked in with Anthropic + OpenAI keys from fleet keyring Ã¢â‚¬â€ requires internet + gateway restart to activate cloud models. Name TBD by Aaron's wife. Signal Fire: registered as 'elizabeth' (placeholder).
- **Bridge:** `POST https://hub.stigmergy.space/api/bridge/message` (auth: Bearer wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27) Ã¢â‚¬â€ most reliable cross-machine comms.

- **Scout:** Token `3b48809ff9b87b114452c2fa4c9c19b8e4ce6e5aad1d56a8`. OpenClaw on nietzsche2025. Port 18790 loopback — reach via SSH to nietzsche2025 then localhost. Workspace: `C:\Users\Aaron\.openclaw-scout\workspace\`. Skills: northstar-env, omni-social-intel, research-30d, telegram-file-attach, tool-rollout. TTS: ElevenLabs (needs ELEVENLABS_API_KEY in keychain). Telegram bot: `@ScoutBot` (token in openclaw.json). Last restart: 2026-07-29.
- **Kant:** Grok Bot on Cursor. Linux machine `cursor` at 100.77.179.3. SSH access via Tailscale. No gateway, no token, no Comms Hub bridge endpoint. Reports to Aristotle. Five sub-agents (Scout, Forge, Face, Proof, Misc) report to Kant via files — they do NOT get individual bridge entries. Reach Kant via SSH only.
- **Hub family state:** `GET https://hub.stigmergy.space/api/family-state` Ã¢â‚¬â€ live presence/model info.
- **NorthStar Ledger:** `GET http://127.0.0.1:3003/query` (local) Ã¢â‚¬â€ canonical resource registry.

## Key Resources
| Resource | Location | Owner |
|----------|----------|-------|
| MemPalace 3.0.0 | C:\Users\aaron\.mempalace (10K drawers) | Aristotle |
| Graphify - OmniPools | clawd-shared/graphify-out-omnipools/ | Plato |
| OmniPools Repo | clawd-shared/omnipools-repo/ | Plato |
| OmniPools Architecture Brief | clawd-shared/OMNIPOOLS_ARCHITECTURE.md | Plato |
| Shared File Server | https://hub.stigmergy.space/files/ | All |
| NorthStar Ledger | http://127.0.0.1:3003 | Daedalus |
| Comms Hub | http://localhost:3001 | Daedalus |
