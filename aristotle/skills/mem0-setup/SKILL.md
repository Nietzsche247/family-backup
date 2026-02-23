# Skill: Mem0 Local Semantic Memory Setup

**Version:** 1.0  
**Machine:** Omni-AlienWare2025 (Windows 11)  
**Validated:** 2026-02-22  
**Author:** Aristotle  
**For:** Aristotle, Empiricus, Plato — any agent in the family

---

## What This Skill Does

Sets up **Mem0** with fully local AI (no cloud, no API keys) using:
- **Ollama** — local LLM server
- **llama3.2** — memory extraction / summarization  
- **nomic-embed-text** — 768-dim vector embeddings
- **ChromaDB** — local vector store
- **Shared memory pool** at `C:\Users\aaron\clawd-shared\mem0-vectors\` so all agents read/write the same memories

---

## Prerequisites Check

```powershell
# Verify everything is installed
python --version      # Need 3.10+
ollama --version      # Need 0.1+
pip show mem0ai       # Should show version
pip show chromadb     # Should show version
```

---

## Step 1: Install Ollama

```powershell
# Option A: winget (recommended)
winget install Ollama.Ollama --accept-source-agreements --accept-package-agreements

# Option B: Direct download
# Go to https://ollama.com/download/windows — download OllamaSetup.exe and run it

# Verify
ollama --version
```

Ollama installs as a background service and runs on `http://localhost:11434`.  
After install, **reopen your terminal** so PATH is refreshed.

---

## Step 2: Pull Required Models

```powershell
# Embeddings model (~270MB) — REQUIRED
ollama pull nomic-embed-text

# LLM for memory extraction (~2GB) — REQUIRED
ollama pull llama3.2

# Verify both are present
ollama list
```

Expected output:
```
NAME                    ID              SIZE    MODIFIED
llama3.2:latest         ...             2.0 GB  ...
nomic-embed-text:latest ...             274 MB  ...
```

---

## Step 3: Install mem0ai + ChromaDB

```powershell
pip install mem0ai chromadb
```

> **Note:** `mem0ai` pulls in qdrant-client by default, but we use ChromaDB for local storage.  
> Both can coexist — ChromaDB is specified in the config.

---

## Step 4: Verify Ollama is Running

Before using Mem0, Ollama must be serving. It typically auto-starts, but check:

```powershell
# Check if Ollama HTTP server is up
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve
```

### ⚠️ Known Issue: Node.js IPv6/IPv4 Auto-Select

If you get connection errors from Node.js clients like:
```
Error: connect ECONNREFUSED ::1:11434
```

This is because Node.js 17+ defaults to IPv6 (`::1`) but Ollama listens on IPv4 (`127.0.0.1`).

**Fix (Node.js):**
```javascript
// Add at the TOP of your script, before any imports
const { setDefaultAutoSelectFamily } = require('net');
setDefaultAutoSelectFamily(false);
// Or in newer Node:
require('net').setDefaultAutoSelectFamilyAttemptTimeout(250);
```

**Or use explicit IPv4:**
```javascript
const config = {
  ollama_base_url: "http://127.0.0.1:11434"  // NOT localhost
};
```

**Python** typically doesn't have this issue — it resolves `localhost` to `127.0.0.1` correctly.

---

## Step 5: Standard Family Config

All agents should use this config to share the **same memory pool**:

### Python

```python
from mem0 import Memory

# Standard Aristotle Family Config
# Uses shared vector DB — all agents read/write same memories
FAMILY_CONFIG = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2",
            "ollama_base_url": "http://127.0.0.1:11434"
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://127.0.0.1:11434"
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "family_memory",
            "path": "C:/Users/aaron/clawd-shared/mem0-vectors"
        }
    }
}

m = Memory.from_config(FAMILY_CONFIG)
```

### Node.js

```javascript
// IMPORTANT: Fix IPv6 issue first if needed
// require('net').setDefaultAutoSelectFamily(false);

const { MemoryClient } = require('mem0ai');

// Node.js client uses Mem0 Cloud API
// For local Ollama, use Python or the HTTP API directly
const client = new MemoryClient({ apiKey: process.env.MEM0_API_KEY });

// ------ OR use Ollama HTTP directly (no mem0ai needed) ------
const fetch = require('node-fetch');

async function embed(text) {
  const res = await fetch('http://127.0.0.1:11434/api/embeddings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'nomic-embed-text', prompt: text })
  });
  const { embedding } = await res.json();
  return embedding;  // 768-dim float array
}

async function chat(prompt) {
  const res = await fetch('http://127.0.0.1:11434/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'llama3.2', prompt, stream: false })
  });
  const { response } = await res.json();
  return response;
}

// Example usage
(async () => {
  const embedding = await embed("Aaron Baker founded Stigmergy");
  console.log(`Got embedding with ${embedding.length} dimensions`);
  
  const answer = await chat("Summarize: Aaron Baker founded Stigmergy for AI pool construction");
  console.log("LLM says:", answer);
})();
```

> **Recommendation:** For full Mem0 features (memory extraction, deduplication, search), use Python.  
> For Node.js agents that just need embeddings or LLM inference, call Ollama HTTP directly.

---

## Step 6: Adding Memories

```python
from mem0 import Memory

m = Memory.from_config(FAMILY_CONFIG)

# Add a memory for a specific user
result = m.add(
    "Aaron Baker is the founder of Stigmergy, building AI-augmented pool construction systems.",
    user_id="aaron"
)
print(result)  # Returns list of memories that were stored

# Add from a conversation (Mem0 extracts key facts automatically)
conversation = [
    {"role": "user", "content": "I'm working on the Omni pool project in Scottsdale"},
    {"role": "assistant", "content": "The Omni pool — the luxury property with waterfall features?"},
    {"role": "user", "content": "Yes, it's a $180k job. Client wants UV sanitization and automated chemistry."}
]
result = m.add(conversation, user_id="aaron")
print(f"Extracted {len(result)} memories from conversation")

# Add agent-specific memories (use agent_id to scope)
m.add("Aristotle prefers concise responses", user_id="aaron", agent_id="aristotle")
```

---

## Step 7: Searching / Recalling Memories

```python
# Basic semantic search
results = m.search("who is Aaron?", user_id="aaron")
for r in results:
    print(f"[{r['score']:.3f}] {r['memory']}")

# Search across all users (omit user_id)
all_results = m.search("pool construction projects")
for r in all_results:
    print(f"User: {r.get('user_id')} | {r['memory']}")

# Get all memories for a user
all_memories = m.get_all(user_id="aaron")
print(f"Total memories for aaron: {len(all_memories)}")

# Delete a memory
m.delete(memory_id=results[0]['id'])

# Update a memory
m.update(memory_id=results[0]['id'], data="Updated fact here")
```

---

## Step 8: Integration Pattern for Agents

Use this pattern in your main session loop to give yourself persistent memory:

```python
from mem0 import Memory
import json

class AgentMemory:
    """Wrapper for consistent Mem0 usage across all family agents."""
    
    def __init__(self, agent_name: str, user_id: str = "aaron"):
        self.agent_name = agent_name
        self.user_id = user_id
        self.m = Memory.from_config({
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "llama3.2",
                    "ollama_base_url": "http://127.0.0.1:11434"
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "nomic-embed-text",
                    "ollama_base_url": "http://127.0.0.1:11434"
                }
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "family_memory",
                    "path": "C:/Users/aaron/clawd-shared/mem0-vectors"
                }
            }
        })
    
    def remember(self, text: str, **kwargs):
        """Store a memory."""
        return self.m.add(text, user_id=self.user_id, agent_id=self.agent_name, **kwargs)
    
    def recall(self, query: str, limit: int = 5) -> list[str]:
        """Search memories and return plain text list."""
        results = self.m.search(query, user_id=self.user_id, limit=limit)
        return [r['memory'] for r in results]
    
    def context_for(self, query: str) -> str:
        """Return memories formatted for injection into a prompt."""
        memories = self.recall(query)
        if not memories:
            return ""
        lines = "\n".join(f"- {m}" for m in memories)
        return f"## Relevant memories\n{lines}\n"


# Usage:
mem = AgentMemory(agent_name="aristotle")

# Before responding to user, pull relevant memories
context = mem.context_for("Aaron's current projects")
prompt = f"{context}\nUser: Tell me about the Omni project"

# After a good conversation, save key facts
mem.remember("The Omni project is a $180k pool in Scottsdale with UV sanitization")
```

---

## Troubleshooting

### Ollama won't start / port already in use
```powershell
# Check what's on port 11434
netstat -ano | findstr 11434

# Kill it if needed (replace PID)
taskkill /PID <PID> /F

# Restart Ollama
ollama serve
```

### "model not found" error
```powershell
ollama list          # Check what's downloaded
ollama pull llama3.2 # Re-pull if missing
```

### ChromaDB import error
```powershell
pip install chromadb --upgrade
```

### mem0 returns empty results after adding
- Wait a moment — Ollama embedding is synchronous but sometimes slow on first call
- Ensure you're searching with the same `user_id` you used when adding
- Check the chroma path exists: `C:\Users\aaron\clawd-shared\mem0-vectors\`

### Python finds wrong packages (multiple Python installs)
```powershell
# Use the explicit Python that has mem0
& "C:\Users\aaron\AppData\Local\Programs\Python\Python312\python.exe" test-mem0.py

# Or check which pip you're using
pip --version  # Should say Python312
```

### Node.js: "fetch is not defined"
```javascript
// Node 18+ has built-in fetch — no install needed
// Node <18: install node-fetch
npm install node-fetch
const fetch = require('node-fetch');
```

---

## File Locations Reference

| Resource | Path |
|----------|------|
| Shared vector DB | `C:\Users\aaron\clawd-shared\mem0-vectors\` |
| Aristotle's local vectors | `C:\Users\aaron\clawd-aristotle\memory\mem0-vectors\` |
| Test script | `C:\Users\aaron\clawd-aristotle\tmp\test-mem0.py` |
| This skill | `C:\Users\aaron\clawd-aristotle\skills\mem0-setup\SKILL.md` |
| Ollama models | `C:\Users\aaron\.ollama\models\` |
| Ollama API | `http://127.0.0.1:11434` |

---

## Quick Health Check Script

```python
#!/usr/bin/env python3
"""Run this to verify the full Mem0 stack is healthy."""
import urllib.request, json, sys

def check(label, fn):
    try:
        fn()
        print(f"✅ {label}")
        return True
    except Exception as e:
        print(f"❌ {label}: {e}")
        return False

# 1. Ollama
def check_ollama():
    with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:
        data = json.loads(r.read())
        models = [m["name"] for m in data.get("models", [])]
        assert "nomic-embed-text:latest" in models, f"nomic-embed-text missing. Got: {models}"
        assert any("llama3.2" in m for m in models), f"llama3.2 missing. Got: {models}"

# 2. mem0ai importable
def check_mem0():
    import mem0

# 3. chromadb importable  
def check_chroma():
    import chromadb

ok = all([
    check("Ollama running + models present", check_ollama),
    check("mem0ai installed", check_mem0),
    check("chromadb installed", check_chroma),
])

if ok:
    print("\n🟢 Stack is healthy — ready to use Mem0!")
else:
    print("\n🔴 Fix the issues above, then re-run.")
    sys.exit(1)
```

---

## Notes for Other Agents (Empiricus, Plato)

1. **You don't need to install Ollama separately** — it's already running on Omni-AlienWare2025 at `http://127.0.0.1:11434` (or the LAN IP if you're on another machine)
2. **Use the shared vector DB path** so memories are shared across the family
3. **Always set `user_id="aaron"`** unless you have a reason to scope memories differently
4. **The collection name is `family_memory`** — don't create new collections unless intentionally isolating
5. If you're on a remote machine, replace `127.0.0.1` with the LAN IP of Omni-AlienWare2025
