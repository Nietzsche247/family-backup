# MemOS Local Plugin Deploy Recipe
# Proven on Aristotle (Omni-AlienWare2025), 2026-05-08
# For: Plato (NIETZSCHE2025), Empiricus (nietzsche-i9), or any new agent

## Prerequisites
- Clawdbot 2026.1.24-3+ running
- Node.js 22+
- Ollama with nomic-embed-text model (for local embeddings)

## Step 1: Copy Extension
Copy the memos-local extension directory to the target machine's Clawdbot extensions:
```
# Source (AlienWare): C:\Users\aaron\.clawdbot-aristotle\extensions\memos-local\
# Target: C:\Users\{user}\.clawdbot\extensions\memos-local\
```
This includes the pre-compiled dist/ directory, node_modules, patches, and config.

## Step 2: Verify 3 Patches (already in the compiled dist/index.js)
These patches are baked into the compiled JavaScript. If re-compiling from source, apply:
1. **Manifest rename**: clawdbot.plugin.json extensions field → ["./dist/index.js"]
2. **registerMemoryCapability → api.on**: Plugin SDK compatibility
3. **isGatewayStartCommand bypass**: Added Clawdbot argv detection

## Step 3: Pre-compile TypeScript (already done)
The dist/ directory contains compiled JavaScript. If missing:
```bash
cd extensions/memos-local
npm install  # if node_modules missing
npx tsc      # compiles despite 2 type errors, emits anyway
```
Verify: dist/index.js should be ~130KB (not 588 bytes — that's a test stub)

## Step 4: Create type stub (if compiling from scratch)
```
mkdir -p node_modules/openclaw/plugin-sdk/
# Write index.d.ts with OpenClawPluginApi interface stub
# See Aristotle's version for reference
```

## Step 5: Configure Gateway
Add to clawdbot.json:
```json
{
  "plugins": {
    "entries": {
      "memos-local-openclaw-plugin": {
        "enabled": true,
        "config": {
          "viewerPort": 18799
        }
      }
    },
    "slots": {
      "memory": "memos-local-openclaw-plugin"
    }
  }
}
```

## Step 6: FULL Restart (not SIGUSR1)
CRITICAL: Must be a full process kill + restart, not SIGUSR1 hot-reload.
SIGUSR1 leaves stale serviceStarted flag → DB connection never opens.
```
schtasks /end /TN "Clawdbot Gateway"
# Kill all node.exe gateway processes
schtasks /run /TN "Clawdbot Gateway"
```

## Step 7: Verify
1. Check gateway log for: "REGISTER CALLED" + "better-sqlite3 loaded successfully"
2. Check port 18799 listening (Memory Viewer)
3. Test: memory_search should return "No candidates" (not "connection not open")
4. Open http://127.0.0.1:18799 — set password on first visit

## Step 8: Configure Models (via viewer API)
```
POST /api/auth/setup {"password":"your-password"}
PUT /api/config {
  "embedding": {"provider":"openai","model":"nomic-embed-text","endpoint":"http://127.0.0.1:11434/v1/embeddings","apiKey":"ollama","dimensions":768},
  "summarizer": {"provider":"openai","model":"gpt-4.1-mini","endpoint":"https://api.openai.com/v1/chat/completions","apiKey":"YOUR_KEY"},
  "skillEvolution": {"summarizer":{"provider":"openai","model":"gpt-4.1-mini","endpoint":"https://api.openai.com/v1/chat/completions","apiKey":"YOUR_KEY"}}
}
```

## Known Issues
- OpenAI embeddings quota: If OpenAI key is exhausted, use Ollama (local, free)
- NAT loopback: Public URL probes from same machine fail (expected)
- Plugin logs "memos-local: stopped" during SIGUSR1 cycle — ignore if followed by restart
- Viewer auth stored at ~/.openclaw/viewer-auth.json — delete to reset password

## Verification Checklist
- [ ] dist/index.js is 130KB+ (not 588-byte stub)
- [ ] clawdbot.plugin.json extensions: ["./dist/index.js"]
- [ ] Gateway config has plugins.entries.memos-local-openclaw-plugin.enabled: true
- [ ] Gateway config has plugins.slots.memory: "memos-local-openclaw-plugin"
- [ ] Full restart done (not SIGUSR1)
- [ ] Port 18799 listening
- [ ] memory_search returns valid response (even if empty)
- [ ] Models configured in viewer settings
