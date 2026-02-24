# InfraNodus Integration Skill (v2) — GraphRAG Engine

**Owner:** Thales ⚙️  
**Version:** 2.0  
**Status:** Live & Upgraded  

---

## What Is InfraNodus?

InfraNodus is a **text network analysis** platform that converts text into a **knowledge graph**. This skill provides a comprehensive integration, including a powerful **GraphRAG query engine**.

**Core Capabilities:**
1.  **Analyze Text:** Generate a knowledge graph showing concept clusters, influence scores, and structural gaps.
2.  **GraphRAG Query:** Ask questions of your text. InfraNodus uses the graph structure to augment your query, providing context-aware, insightful answers.
3.  **AI Advice:** Generate gap-bridging research questions, innovative ideas, and summaries directly from the graph structure.
4.  **Compare Texts:** Find the difference, overlap, or union between the knowledge graphs of multiple documents.

---

## Hub API Endpoints (v2)

The comms-hub (`http://localhost:3001`) exposes a full suite of endpoints:

### Primary Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/infranodus/analyze` | Submit text, get a full knowledge graph analysis (nodes, edges, clusters, gaps). |
| `POST` | `/api/infranodus/query` | **(GraphRAG)** Ask a question against a text/context; get a graph-augmented answer. |
| `POST` | `/api/infranodus/advice` | Get AI-generated ideas, summaries, or challenges based on graph structure. |
| `POST` | `/api/infranodus/compare` | Compare two texts to find their `difference`, `overlap`, or `merge`. |

### Utility Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/infranodus/graphsummary`| Get a compact text summary of a graph, perfect for LLM prompt injection. |
| `POST` | `/api/infranodus/vault` | Analyze the entire `C:\bravo-team\shared` Obsidian vault. |
| `GET` | `/api/infranodus/contexts` | List all analyses cached in the current server session. |
| `GET` | `/api/infranodus/analysis/:name` | Retrieve a full cached analysis result by its context name. |
| `GET` | `/api/infranodus/gaps/:name` | Get just the gaps and top concepts for a context. |
| `GET` | `/api/infranodus/summary/:name`| Get a cached graph summary. |
| `GET`|`/api/infranodus/projects`| List the 8 pre-configured project contexts. |

---

## How Agents Should Use This (v2 Workflow)

### Pattern 1: The "Default" GraphRAG Workflow
This is the most powerful pattern. **Use this for any research or query task.**

1.  **Gather Context:** Collect all relevant text from files, web pages, or previous notes.
2.  **Analyze First:** `POST /api/infranodus/analyze` with the collected text and a `contextName`. This builds the knowledge graph.
    ```json
    { "text": "...", "contextName": "my-research-context" }
    ```
3.  **Query the Graph:** `POST /api/infranodus/query` with your question, referencing the `contextName`.
    ```json
    {
      "query": "What is the key insight missing from this text?",
      "contextName": "my-research-context",
      "mode": "reprompt" 
    }
    ```
    The `reprompt` mode uses GraphRAG to rewrite your simple query into a rich, context-aware prompt, yielding superior results.

### Pattern 2: Quick AI Insight
When you need a creative spark or a new research direction from a piece of text.

1.  `POST /api/infranodus/advice` with your text and a `requestMode`.
    *   `requestMode: 'question'` → Generates a research question that bridges a structural gap.
    *   `requestMode: 'idea'` → Generates an innovative idea that connects disparate topics.
    *   `requestMode: 'challenge'` → Generates a statement that challenges the text's assumptions.
    ```json
    {
      "text": "...",
      "requestMode": "question",
      "optimize": "gaps"
    }
    ```

### Pattern 3: Find the Difference
Use this to understand what's new or unique in a document compared to another.

1.  `POST /api/infranodus/compare` with two text objects and `mode: 'difference'`.
    ```json
    {
      "contexts": [ { "text": "Version 1 of the document..." }, { "text": "Version 2..." } ],
      "mode": "difference"
    }
    ```
2.  The resulting graph shows concepts present in Text A but absent in Text B.

### Pattern 4: Injecting Graph Context into another LLM
To give a different AI (e.g., a sub-agent) the "gist" of a large document without sending the whole text.

1.  `POST /api/infranodus/graphsummary` with your text.
2.  Take the `graphSummary` string from the response.
3.  Include it in your prompt to the other LLM: *"Based on the following knowledge graph summary, please answer my question... [graphSummary here] My question is: ...*

---

## v2 Advanced Patterns (New)

### Pattern 5: CrewAI-Style 4-Agent Gap Research Chain ⛓️
**Endpoint:** `POST /api/infranodus/chain`

Runs a complete 4-step gap research pipeline in a single call. Adapted from the CrewAI-InfraNodus workflow.

**The 4 internal agents:**
1. **Graph Analyst** — submits text → extracts graph, clusters, gaps
2. **Gap Analyst** — distills structural gaps into an actionable insight report
3. **Question Generator** — generates research questions that bridge the gaps
4. **Synthesizer** — produces a full report grounded in gap-identified topics

```http
POST /api/infranodus/chain
Content-Type: application/json

{
  "text": "Your research corpus here...",
  "contextName": "pool-engineering",
  "question": "What are the most critical missing connections?"
}
```

**Response structure:**
```json
{
  "gaps": [...],            // Structural gaps from graph topology
  "gapSummary": "...",      // Human-readable gap descriptions
  "topConcepts": "...",     // Most influential concepts with scores
  "gapReport": "...",       // Agent 2: actionable insight report
  "researchQuestions": [],  // Agent 3: research questions from gaps
  "synthesis": "...",       // Agent 4: full grounded report
  "graph": { ... },         // Node/edge/cluster summary
  "chain": [...],           // Step-by-step execution log
  "elapsedMs": 4200
}
```

**When to use this:**
- Researcher agent needs a complete research brief from a document
- Aristotle wants to understand what's missing from a strategy doc
- Steelman wants to find the weakest assumptions in a proposal
- Any agent running multi-step analysis — this does it in one call

**Family agent workflow:**
```
1. Collect text (web scrapes, docs, notes, web search results)
2. POST /api/infranodus/chain with text + contextName
3. Use researchQuestions as next-round search queries
4. Use synthesis as the deliverable / briefing document
5. Use gaps as "what to investigate next" backlog
```

---

### Pattern 6: Portable GraphRAG (Graph-Grounded LLM Answers) 🧠
**Endpoint:** `POST /api/infranodus/graphrag`

The key upgrade over standard RAG: instead of retrieving text chunks, we retrieve the **graph structure** and use topology as LLM context. Sends clusters + gaps + influence scores to Ollama (localhost:11434), falls back to InfraNodus AI.

```http
POST /api/infranodus/graphrag
Content-Type: application/json

{
  "text": "Text corpus to analyze...",
  "question": "What are the key risks we're not addressing?",
  "contextName": "options-trading",
  "ollamaModel": "llama3",
  "ollamaUrl": "http://localhost:11434",
  "fallbackToInfraNodus": true
}
```

**Response:**
```json
{
  "answer": "...",           // Graph-grounded answer
  "source": "ollama",        // 'ollama' | 'infranodus-fallback' | 'error'
  "ollamaModel": "llama3",
  "graphContext": {
    "modularity": 0.42,
    "gaps": [...],
    "topInfluential": [...],
    "topClusters": [...],
    "graphSummary": "..."
  }
}
```

**Why GraphRAG > standard RAG:**
| Standard RAG | GraphRAG |
|---|---|
| Retrieves text chunks | Retrieves graph topology |
| LLM answers from keyword matches | LLM answers from concept relationships |
| Gaps are invisible | Gaps are **explicit LLM context** |
| All chunks weighted equally | Influence scores tell LLM what matters most |
| Misses structural holes | Structural holes are the primary signal |

**Ollama model suggestions:**
- `llama3` — balanced, good default
- `mistral` — strong structured reasoning
- `qwen2.5:14b` — best analytical depth
- Falls back to InfraNodus AI if Ollama is offline

---

### Pattern 7: Native MCP Tool Access 🔌
**Status:** Configured in `~/.clawdbot-thales/clawdbot.json`

The InfraNodus MCP server (`infranodus-mcp-server`) is now wired into Thales' Clawdbot config. When active, InfraNodus tools are **native session tools** — no hub endpoints required.

**Active configuration:**
```json
"tools": {
  "mcp": {
    "servers": {
      "infranodus": {
        "command": "npx",
        "args": ["-y", "infranodus-mcp-server"],
        "env": {
          "INFRANODUS_API_KEY": "<key>"
        }
      }
    }
  }
}
```
*(Wired to all Clawdbot agent configs that need it)*

**MCP tools available natively:**
- Gap detection on any text
- Cluster analysis and topical overview  
- Research question generation
- Graph traversal and search
- GraphRAG reasoning with existing graphs
- SEO / search intent comparison

**Using it:** With MCP active, agents can call InfraNodus conversationally:
- *"Analyze this text for structural gaps"*
- *"Generate research questions from this corpus"*
- *"Compare these two documents and find what's missing"*

The server installs automatically on first use via `npx -y infranodus-mcp-server`.

**Remote hosted MCP (Claude Web):** `https://mcp.infranodus.com` → Settings → Connectors

---

## Visual Dashboard (`http://hub.stigmergy.space`)

The `🕸️ InfraNodus` tab has been upgraded to a full-featured IDE:
- **Mode-switching Interface:** Toggle between **Analyze**, **GraphRAG Query**, **Compare**, and **Vault** modes.
- **GraphRAG Panel:** Select a cached analysis, type a question, and get a graph-augmented answer in a dedicated panel.
- **Compare Panel:** Two text areas to compare documents and visualize the result.
- **Animated Gap Lines:** Structural gaps are now shown with a subtle animation to draw attention to them.
- **Quick Actions:** The results panel has buttons to instantly generate AI questions/ideas from the current graph.

---

## Ledger Registration (Updated)

```json
{
  "name": "infranodus_integration_v3",
  "type": "api",
  "canonical_path": "https://infranodus.com/api/v1/",
  "project": "global",
  "owner": "thales",
  "description": "Full-featured text network analysis and GraphRAG engine. Converts text to queryable knowledge graphs, finds structural gaps, generates AI-augmented insights. Includes CrewAI-style chain workflow, portable GraphRAG, and MCP server integration.",
  "endpoints": [
    "POST /api/infranodus/analyze",
    "POST /api/infranodus/query",
    "POST /api/infranodus/advice",
    "POST /api/infranodus/compare",
    "POST /api/infranodus/graphsummary",
    "POST /api/infranodus/vault",
    "POST /api/infranodus/chain",
    "POST /api/infranodus/graphrag",
    "GET /api/infranodus/contexts",
    "GET /api/infranodus/analysis/:name",
    "GET /api/infranodus/gaps/:name",
    "GET /api/infranodus/summary/:name",
    "GET /api/infranodus/projects"
  ],
  "mcp": {
    "server": "infranodus-mcp-server",
    "configured_in": "~/.clawdbot-thales/clawdbot.json",
    "remote": "https://mcp.infranodus.com"
  }
}
```

---

*InfraNodus v3 — chain + GraphRAG + MCP. Thales out.*
*Updated: 2026-02-24*
