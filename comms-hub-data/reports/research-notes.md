# Research Notes

This file will contain the raw research notes for the platform architecture report.

## 7. Platform Architecture Patterns

**Key Finding**: The consensus from recent research and industry best practices points towards a **hub-and-spoke architecture** featuring a central orchestrator and domain-specialist agents. The most advanced systems use an **environment-based coordination mechanism** instead of direct agent-to-agent communication.

**Recommended Architecture**: A **Stigmergic Hub-and-Spoke Model**.

```
+-----------------------------------------------------------------+
|                                                                 |
|                      USER / EXTERNAL INPUT                      |
|                                                                 |
+---------------------------------v-------------------------------+
                                  |
+---------------------------------v-------------------------------+
|                                                                 |
|                  ORCHESTRATOR / ROUTER AGENT                    |
|                (Decomposes tasks, routes to specialists)        |
|                                                                 |
+---------------------------------v-------------------------------+
                                  |
+---------------------------------v-------------------------------+
|                                                                 |
|          STIGMERGIC BLACKBOARD (powered by SBP)                 |
|       (Agents emit signals here, other agents react to them)    |
|                                                                 |
+-------------------^----------------------^----------------------+
                    |                      |
      (Emits/Senses Signals)         (Emits/Senses Signals)
                    |                      |
+-------------------+------------------+---+----------------------+
|                   |                  |                          |
v                   v                  v                          v
+-------------+ +-------------+ +-------------+ +-----------------+
| FinanceAgent| | VisionAgent | | DataMinerAgent| | ImageGenAgent | ...
+-------------+ +-------------+ +-------------+ +-----------------+
      |               |                 |                 |
      v               v                 v                 v
+-------------+ +-------------+ +-------------+ +-----------------+
| Nautilus-   | | insightface | | browser-use | | ComfyUI + FLUX.1| ...
| Trader      | | + Milvus    | |             | |                 |
+-------------+ +-------------+ +-------------+ +-----------------+

```

**Core Components**:
1.  **Orchestrator Agent**: The "front door" of the system. It receives high-level goals, uses a powerful LLM to break them into smaller, actionable sub-tasks, and emits the initial signals to the blackboard to kick off a workflow.

2.  **Specialist Agents**: A collection of independent, domain-expert agents. Each specialist is built around one or more of the core tools identified in this research. For example:
    *   `FinanceAgent`: Knows how to use `NautilusTrader` and `Darts`.
    *   `VisionAgent`: Knows how to use `insightface` and `Milvus`.
    *   `DataMinerAgent`: Knows how to use `browser-use`.
    *   Each agent is responsible *only* for its domain.

3.  **Stigmergic Blackboard (`SBP`)**: The central nervous system. This is the critical component for decoupling.
    *   Agents *never* call each other directly.
    *   When an agent finishes a task, it emits a "pheromone" (a signal) to the blackboard. For example, the `DataMinerAgent` emits `blm.claims.found` with the data as a payload.
    *   Other agents have "scents" registered with the blackboard. For example, a `GISAgent` might be dormant until it senses the `blm.claims.found` signal, at which point it wakes up, consumes the data, and generates a map.

**Benefits of this Architecture**:
*   **Modularity & Scalability**: New capabilities can be added simply by creating a new Specialist Agent and teaching it what signals to listen for. No existing agents need to be modified.
*   **Robustness**: The system is not a brittle, hard-coded chain of calls. It's a dynamic, event-driven ecosystem. If one agent fails, it doesn't necessarily bring down the entire workflow.
*   **Emergent Behavior**: Complex, multi-step workflows can emerge from the simple rules of agents reacting to signals in the environment, rather than being explicitly coded. This is the core of a truly adaptive and "universal" platform.
