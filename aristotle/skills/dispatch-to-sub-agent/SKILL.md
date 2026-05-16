---
name: dispatch-to-sub-agent
description: "Standard sub-agent dispatch envelope for Daedalus, Thales, Steel Man, Researcher. Brief format and invocation patterns."
---

# Dispatch to Sub-Agent

## Roster
| Agent | ID | Use When |
|-------|-----|----------|
| Daedalus 🔧 | daedalus | Code, features, bug fixes |
| Thales ⚙️ | thales | Infra, deployment, testing |
| Steel Man 🗡️ | steelman | Review plans, find flaws |
| Researcher 🔬 | researcher | Deep research, large-context |

## Methods
- **sessions_spawn** (isolated): `sessions_spawn({agentId, task, runTimeoutSeconds: 300})`
- **sessions_send** (existing session): `sessions_send({sessionKey: "agent:daedalus", message, timeoutSeconds: 120})`

## Brief Format
```
TASK: [one-line]
CONTEXT: [why it matters]
DELIVERABLE: [what you expect back]
ACCEPTANCE CRITERIA: [how to judge done]
CONSTRAINTS: [time, stack, deps]
PRIORITY: [critical/high/normal/low]
```

## Rules
- Steel Man reviews before Daedalus builds (non-trivial)
- Daedalus + Thales can parallel on independent tasks
- Never same task to two agents
- Two failures → different agent or approach
