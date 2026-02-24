# Skill: Mermaid Diagrams 📊

Generate, save, and render Mermaid diagrams for flowcharts, sequence diagrams, ER diagrams, Gantt charts, and agent workflows.

## Quick Reference

| What you want | How |
|---|---|
| Render in browser | `http://localhost:3001/api/diagram?code=[URL-encoded syntax]` |
| Render via POST | `POST http://localhost:3001/api/diagram` with `{"code":"..."}` |
| Save as file | Write `.md` file to `C:\bravo-team\shared\diagrams\` |
| Embed in Obsidian | Wrap in ` ```mermaid ` code block — renders natively |
| Dashboard viewer | Open hub at `http://localhost:3001` → 📊 Diagrams tab |

---

## Diagram Types & Syntax

### 1. Flowchart (SOP / Process)

Use for: SOPs, decision trees, process flows.

```mermaid
graph TD
    A([Start]) --> B[Step 1: Intake]
    B --> C{Decision Point}
    C -->|Yes| D[Path A]
    C -->|No| E[Path B]
    D --> F[Review]
    E --> F
    F --> G([End])
```

**Direction modifiers:** `TD` (top-down), `LR` (left-right), `RL`, `BT`

**Node shapes:**
- `[Rectangle]` — standard step
- `(Rounded)` — soft step
- `([Stadium])` — start/end
- `{Diamond}` — decision
- `[(Database)]` — data store
- `((Circle))` — event

---

### 2. Sequence Diagram (Agent/System Communication)

Use for: agent conversations, API call flows, protocol documentation.

```mermaid
sequenceDiagram
    participant Aaron as 👤 Aaron
    participant Aristotle as 🏛️ Aristotle
    participant Daedalus as 🔧 Daedalus
    participant Hub as 🔁 Comms Hub

    Aaron->>Aristotle: Assign task
    Aristotle->>Hub: POST /api/bridge/message
    Hub-->>Daedalus: Wake via gateway
    Daedalus->>Daedalus: Execute build
    Daedalus-->>Aristotle: Report complete
    Aristotle-->>Aaron: Summary
```

**Arrow types:**
- `A->>B: msg` — solid arrow (sync call)
- `A-->>B: msg` — dashed arrow (async/response)
- `A-)B: msg` — open async arrow
- `Note over A,B: text` — annotation

---

### 3. Entity-Relationship Diagram (Data Model)

Use for: database schemas, data relationships, system models.

```mermaid
erDiagram
    AGENT ||--o{ TASK : "owns"
    TASK ||--o{ MESSAGE : "generates"
    TASK }o--|| PROJECT : "belongs to"

    AGENT {
        string name PK
        string role
        string model
        string machine
    }
    TASK {
        string id PK
        string title
        string status
        string priority
        datetime created
    }
    MESSAGE {
        string id PK
        string from
        string to
        string body
        datetime timestamp
    }
    PROJECT {
        string id PK
        string name
        string owner
    }
```

**Cardinality:**
- `||--||` — exactly one to exactly one
- `||--o{` — one to zero-or-many
- `}o--o{` — zero-or-many to zero-or-many

---

### 4. Gantt Chart (Project Timeline)

Use for: project planning, sprint schedules, roadmaps.

```mermaid
gantt
    title North Star Q1 Roadmap
    dateFormat  YYYY-MM-DD
    excludes    weekends

    section Infrastructure
    Comms Hub v1          :done,     t1, 2025-01-01, 14d
    Bridge protocol       :done,     t2, after t1, 7d
    Ledger service        :active,   t3, after t2, 10d

    section Agents
    Aristotle deploy      :done,     a1, 2025-01-15, 5d
    Daedalus deploy       :done,     a2, after a1, 3d
    Plato remote          :          a3, after t3, 7d

    section Skills
    Mermaid skill         :done,     s1, 2025-02-01, 1d
    Memory consolidation  :          s2, after s1, 5d
```

**Task states:** `done`, `active`, `crit` (critical path), blank (future)

---

### 5. Agent Workflow (Architecture Diagram)

Use for: system architecture, agent topology, data flow.

```mermaid
flowchart LR
    User([👤 Aaron]) --> |chat| Aristotle

    subgraph Local["🖥️ Omni-AlienWare2025"]
        Aristotle{🏛️ Aristotle} --> |build tasks| Daedalus
        Aristotle --> |research| Researcher
        Aristotle --> |debate| Steelman
        Daedalus[🔧 Daedalus]
        Researcher[🔬 Researcher]
        Steelman[⚔️ Steelman]
        Hub[(🔁 Comms Hub\nlocalhost:3001)]
    end

    subgraph Remote["☁️ Remote Machines"]
        Plato[🏛️ Plato\nTailscale]
        Empiricus[🧪 Empiricus\nHetzner]
    end

    Daedalus --> Hub
    Researcher --> Hub
    Hub --> |bridge| Plato
    Hub --> |bridge| Empiricus
    Aristotle --> |answer| User
```

---

## How to Save Diagrams

Save any diagram as a Markdown file in the shared diagrams directory:

```
C:\bravo-team\shared\diagrams\
```

**File format** — wrap in a mermaid code block:

````markdown
# Diagram Title

Brief description of what this shows.

```mermaid
graph TD
    A --> B
```

**Author:** daedalus
**Created:** 2025-02-XX
**Tags:** #architecture #flowchart
````

**Naming convention:** `YYYY-MM-DD-descriptive-name.md`
Example: `2025-02-19-agent-workflow.md`

---

## Rendering via Hub

### Option 1: GET request (query param)
```javascript
const code = `graph TD\n    A-->B`;
const url = `http://localhost:3001/api/diagram?code=${encodeURIComponent(code)}`;
// Opens a dark-themed rendered HTML page
```

### Option 2: POST request (JSON body)
```javascript
const response = await fetch('http://localhost:3001/api/diagram', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code: 'graph TD\n    A-->B' })
});
const html = await response.text();
```

### Option 3: Dashboard Viewer
1. Open `http://localhost:3001`
2. Click **📊 Diagrams** tab
3. Type/paste Mermaid syntax in the editor
4. Click **▶ Render** or it auto-renders live
5. Click **⛶ Full** to open in new tab
6. Click **🔗 Copy URL** to get a shareable link

---

## Obsidian Integration

Obsidian renders Mermaid natively. Just wrap any diagram in a mermaid code block in any `.md` file:

````markdown
```mermaid
graph TD
    A[Idea] --> B[Research]
    B --> C[Build]
    C --> D[Ship]
```
````

No plugins needed — works out of the box.

---

## Quick Examples by Use Case

### SOP Flowchart
```mermaid
graph TD
    START([📥 Request Received]) --> TRIAGE{Urgent?}
    TRIAGE -->|Yes| ESCALATE[Escalate to Lead]
    TRIAGE -->|No| QUEUE[Add to Queue]
    ESCALATE --> ASSIGN[Assign Agent]
    QUEUE --> ASSIGN
    ASSIGN --> WORK[Execute Task]
    WORK --> REVIEW{QA Pass?}
    REVIEW -->|Yes| DONE([✅ Complete])
    REVIEW -->|No| REWORK[Rework]
    REWORK --> REVIEW
```

### Data Flow
```mermaid
flowchart LR
    Input([Raw Data]) --> Parse[Parse & Validate]
    Parse --> Transform[Transform]
    Transform --> Store[(Database)]
    Store --> API[REST API]
    API --> Dashboard[Dashboard]
    API --> Export[Export]
```

---

## Tips

- **Obsidian renders live** — paste any diagram into a `.md` file and switch to Preview
- **URL length limit** — for very long diagrams, use POST instead of GET
- **Theme** — the hub always renders with `theme: 'dark'` — matches the aesthetic
- **Debug** — if a diagram doesn't render, check syntax at [mermaid.live](https://mermaid.live)
- **Subgraphs** — use `subgraph Name["Label"]` ... `end` to group nodes visually
- **Click events** — add `click NodeId href "url"` to make nodes clickable in rendered output
