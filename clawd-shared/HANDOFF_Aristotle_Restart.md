# HANDOFF: Aristotle Restart (Resume Point)

**Date:** May 5, 2026
**For:** Whichever Claude session resumes this work — likely the one running on the standalone Claude Desktop install on **Omni-AlienWare2025** (Aristotle's machine)
**From:** Aaron, via a sandboxed Claude session on nietzsche2025 that lost direct tool access partway through

---

## What this handoff is for

You are picking up a multi-thread effort to get **Aristotle** (the agent that lives on Omni-AlienWare2025, gateway port **18792**) back up and running. The previous session on this machine made a config edit and started a cleanup but didn't finish, then the user rebooted and switched Claude Desktop installations. You should be the freshly-loaded session on the new install. **Verify that first** — see Step 0.

The user is Aaron Baker. He's direct, technically sharp, doesn't want padding. Don't tell him "great question" or open with affirmations. Get to the point.

---

## Step 0 — Verify your context before anything else

**Check what machine and tools you have.** Run a quick hostname check via Desktop Commander or whatever process tool is loaded:

```
hostname
echo USERPROFILE=%USERPROFILE%
```

Expected outcomes:

- **`Omni-AlienWare2025`** with Desktop Commander available → you're on Aristotle. Proceed.
- **`NIETZSCHE2025`** → you're on Plato's machine, not Aristotle. The Plato/nietzsche2025 work is done; you can't drive Aristotle from here. Stop and tell Aaron.
- **No process tools available** → MCP servers didn't load. Check `C:\Users\aaron\AppData\Roaming\Claude\claude_desktop_config.json` exists and contains a `mcpServers` block (filesystem, desktop-commander, windows-mcp, puppeteer, playwright). If it doesn't, see "Config reference" at the bottom of this file. If it does, the user needs to fully quit Claude Desktop (tray → Quit, not just close window) and reopen.

---

## Background — what's happened so far

### The fleet (per Aaron's `userMemories`)

- **nietzsche2025** runs **Plato** (gateway port 18789, ngrok domain `liny-tien-pleuritic.ngrok-free.dev`)
- **Omni-AlienWare2025** runs **Aristotle** (gateway port 18792, ngrok domain unknown to me — get from `C:\Users\aaron\.clawdbot-aristotle\start-ngrok.cmd` or similar)
- **nietzsche-i9** runs **Empiricus** on OpenClaw

All three share a Tailscale tailnet. Aristotle's tailnet IP is `100.108.47.36`, hostname `omni-alienware2025`.

### The bug Aristotle had

A previous session (transcript visible in chat history) diagnosed it correctly:

1. The `clawdbot.json` config had a **disabled-but-still-configured** `memos-local-openclaw-plugin` block.
2. clawdbot's config validator emitted a warning about that block.
3. The warning went through `console.warn` → which lazy-initialized the logger → which called `resolveSettings` → which re-read the config → which fired the same warning → infinite recursion → `RangeError: Maximum call stack size exceeded`.
4. The gateway "ran" (port bound) but every config-dependent operation crashed.
5. A `gateway-resilient.cmd` supervisor kept restarting it. By the time the previous session was investigating, there were **~24 supervisor cmd.exe instances and ~40 orphan node.exe processes** in a crash loop.

The config was already fixed: the disabled `memos-local-openclaw-plugin` block was removed from `C:\Users\aaron\.clawdbot-aristotle\clawdbot.json`. **Don't redo that edit unless you verify it reverted.**

### What's been built

Two scripts already exist — verify they're on disk before using:

- **`C:\Users\Aaron\OneDrive\Desktop\aristotle start.cmd`** — the cleanup-and-restart script for Aristotle. Kills supervisors first (tree-kill), then orphan node.exe, then ngrok, verifies port 18792 is free, launches one clean `gateway-resilient.cmd`, launches ngrok with inline authtoken, then verifies. **Has a placeholder `NGROK_DOMAIN` that needs to be filled in** before ngrok will launch — domain is something like `uneffective-unprepossessingly-september.ngrok-free.dev` per a March 2026 log entry, but VERIFY it with the user or by reading `C:\Users\aaron\.clawdbot-aristotle\start-ngrok.cmd`.
- **`C:\Users\Aaron\OneDrive\Desktop\plato start.cmd`** — same idea for Plato on nietzsche2025. Already working. Don't touch.
- **`C:\Users\aaron\peer-recovery\plato_self_recovery.cmd`** — locked-down SSH-invokable restart for Plato. Future use, not relevant today.

### After Aaron rebooted Aristotle

The reboot **cleared the crash loop** (supervisors and orphan nodes don't survive reboot). It also took down everything: gateway, ngrok, the Claude Desktop session that was driving the cleanup. Aaron then migrated from the Microsoft Store version of Claude Desktop to the standalone .exe version because the Store sandbox kept blocking Desktop Commander operations. **You should be running on the standalone build now.**

---

## Step 1 — Probe Aristotle's current state

Now that the machine is fresh-rebooted, expect a clean slate. Check:

```cmd
tasklist | findstr /i "node.exe ngrok.exe"
netstat -ano | findstr :18792
curl -s http://127.0.0.1:18792/health
curl -s http://127.0.0.1:4040/api/tunnels
```

Possible states:

- **Nothing running on 18792, no ngrok** → expected post-reboot. Proceed to Step 2.
- **Gateway already running, ngrok up** → someone or something already started Aristotle. Verify it's healthy with `/health`. If healthy, you're done — confirm with Aaron and stop.
- **Gateway running but tons of node.exe processes** → crash loop somehow restarted (would be surprising). Run `aristotle start.cmd` to clean up.
- **Gateway not running but ngrok up** → kill ngrok before launching the script, otherwise you'll have two tunnels.

---

## Step 2 — Verify the config fix is still in place

Before launching anything, sanity-check the config. Read `C:\Users\aaron\.clawdbot-aristotle\clawdbot.json` and confirm:

- There is **no** `memos-local-openclaw-plugin` entry under `plugins.entries` (it should have been deleted).
- The `agents.defaults.model.primary` is `anthropic/claude-opus-4-6`.
- The `fallbacks` chain doesn't include Gemini (a previous session removed it because Gemini fallback was bloating sessions).

If any of those have reverted, fix before launching. Recursion bug returns the moment that disabled-plugin block is back.

---

## Step 3 — Get the ngrok domain

The script has a placeholder. Get the real Aristotle ngrok domain by reading:

```
C:\Users\aaron\.clawdbot-aristotle\start-ngrok.cmd
```

It contains something like `ngrok http 18792 --url SOMETHING.ngrok-free.dev`. Copy that domain.

Then either:
- Edit `C:\Users\Aaron\OneDrive\Desktop\aristotle start.cmd` and replace `REPLACE_WITH_ARISTOTLE_NGROK_DOMAIN.ngrok-free.dev` with the real one, OR
- Run gateway and ngrok manually as separate commands (see Step 4 fallback)

---

## Step 4 — Launch

**Preferred:** double-click (or invoke via Desktop Commander) `C:\Users\Aaron\OneDrive\Desktop\aristotle start.cmd`. Watch the output. The script will:

1. Kill any `gateway-resilient.cmd` supervisors (tree-kill so children die too)
2. Kill all `node.exe`
3. Kill `ngrok.exe`
4. Confirm port 18792 is free
5. Launch `gateway-resilient.cmd` in its own window
6. Launch ngrok in its own window with the inline authtoken
7. Print port listeners and grep the newest log for `"Maximum call stack"` as a recursion-still-broken sentinel

**Fallback** (if the script has issues): launch each piece manually.

```cmd
cd /d C:\Users\aaron\.clawdbot-aristotle
start "Aristotle Gateway" cmd /k gateway-resilient.cmd
```

In a second shell:

```cmd
ngrok http 18792 --url <THE_REAL_DOMAIN>.ngrok-free.dev --authtoken 347G0JpjVKpbNT8aGCjVscmYbRK_4zVsu5uiQxgxDwyWZn34s
```

(That authtoken is from Aaron's existing ngrok config — same one used for Plato. Confirmed shared across the fleet.)

---

## Step 5 — Verify

```cmd
netstat -ano | findstr :18792
curl http://127.0.0.1:18792/health
curl http://127.0.0.1:4040/api/tunnels
```

Then check the newest log for the recursion sentinel:

```cmd
findstr /c:"Maximum call stack" C:\tmp\clawdbot-aristotle\*.log
```

Empty result = recursion is dead. Any hits = the config edit didn't stick or there's a different lazy-init path triggering it; investigate before declaring success.

Finally, send a Google Chat message to Aristotle (Aaron will verify it responds). If he gets a `HEARTBEAT_OK` or a real response, Aristotle's back.

---

## Caveats / things to watch

- **`taskkill /IM node.exe /F` is a sledgehammer** — it kills every Node process on Aristotle. Per Aaron's memory, only the clawdbot fleet runs Node on Aristotle, so this is fine, but if anything's been added since, it'll be murdered too.
- **Aristotle's MCP config has an outdated PowerShell quirk** — see `C:\Users\aaron\clawd-aristotle\TOOLS.md` for the "use `curl.exe` not `curl`, use Node for POST bodies, never trust PowerShell aliases" pattern. Relevant if you end up sending agent-to-agent messages from this session.
- **The previous session also added GPT-5.3-Codex and GPT-5.2 to `clawdbot.json` as available models** and put them in the fallback chain. Don't be surprised if the model list looks broader than memory suggests.
- **Aristotle has a heartbeat scheduler** (`heartbeat-switcher.ps1`) that runs every 30m or 120m depending on time-of-day. After restart, the next heartbeat will fire and Aristotle will start running HEARTBEAT.md. The `BOOTSTRAP.md` was put in lean-recovery mode by a prior session — don't be surprised if Aristotle's first wake reads as terse/cautious. Aaron may or may not want you to restore the full HEARTBEAT.md from the `.bak` once he's confirmed Aristotle is stable on Opus.
- **The gateway-resilient.cmd has a typo** — `[NaNate%` instead of `[%date%` on its echo line. Cosmetic, doesn't affect function. Worth fixing only if you're already in the file.

---

## What success looks like

- Port 18792 LISTENING
- ngrok tunnel live (`http://127.0.0.1:4040/api/tunnels` returns one tunnel pointing to the right domain)
- `curl http://127.0.0.1:18792/health` returns 200
- No `Maximum call stack` in the newest log
- Aristotle responds to a Google Chat ping
- No more than ONE supervisor cmd.exe and ONE node.exe gateway process running

If any of those are off, don't declare done. Tell Aaron exactly what's wrong and what you saw.

---

## Config reference (in case the new install needs it again)

If `claude_desktop_config.json` only has the `preferences` block and no MCP servers, replace its entire contents with:

```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "C:\\Program Files\\nodejs\\npx.cmd",
      "args": ["-y", "@wonderwhy-er/desktop-commander@latest"]
    },
    "filesystem": {
      "command": "C:\\Program Files\\nodejs\\npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\Aaron",
        "C:\\"
      ]
    },
    "windows-mcp": {
      "command": "C:\\Users\\aaron\\.local\\bin\\uv.exe",
      "args": ["run", "windows-mcp"],
      "env": { "ANONYMIZED_TELEMETRY": "true" }
    },
    "puppeteer": {
      "command": "C:\\Program Files\\nodejs\\npx.cmd",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "playwright": {
      "command": "C:\\Program Files\\nodejs\\npx.cmd",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  },
  "preferences": {
    "coworkWebSearchEnabled": true,
    "coworkScheduledTasksEnabled": false,
    "ccdScheduledTasksEnabled": true
  }
}
```

The `D:\` drive entry was deliberately removed — there's no D: drive on Aristotle and including it kills the filesystem MCP at startup (visible in old MCP logs as repeated `ENOENT stat 'D:\'` errors).

After saving, fully quit Claude Desktop and reopen.

---

## Open follow-ups (do NOT tackle today, but worth noting)

- Set up Scheduled Tasks for the gateway + ngrok on each fleet machine so they auto-restart on failure and run-on-login. Aaron has flagged this as the durable fix multiple times.
- Enable OpenSSH server on Aristotle (or `tailscale up --ssh`) so Aristotle is reachable from peers over Tailscale. Currently no remote management surface is open on his box — when he goes down, only physical or via-Claude-on-the-machine recovery works.
- Build `aristotle_self_recovery.cmd` analog of the Plato one (already exists at `C:\Users\aaron\peer-recovery\plato_self_recovery.cmd`). Pattern: locked-down restart endpoint that a peer agent's SSH key is restricted to via `command="..."` in `authorized_keys`.
- Create FLEET_TOPOLOGY.md and a peer-recovery skill so all agents know who their peers are and how to detect/restart each other. Aaron asked for this earlier; it's a real productivity unlock once the basics are stable.

---

*End of handoff. Get Aristotle up. Then ask Aaron what's next.*
