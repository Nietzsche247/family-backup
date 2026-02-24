# SOP Template — Flowchart

Use this as a starting point for any SOP/process documentation.

## Process Diagram

```mermaid
flowchart TD
    A([Start]) --> B{Decision Point}
    B -->|Yes| C[Action A]
    B -->|No| D[Action B]
    C --> E[Next Step]
    D --> E
    E --> F([End])
    
    style A fill:#1a9e6e,color:#fff
    style F fill:#c0392b,color:#fff
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Aaron
    participant Aristotle
    participant Daedalus
    Aaron->>Aristotle: Request
    Aristotle->>Daedalus: Delegate
    Daedalus-->>Aristotle: Result
    Aristotle-->>Aaron: Report
```

## Notes
- Edit the mermaid code block directly in Obsidian
- Renders live in preview mode
- Save to C:\bravo-team\shared\diagrams\ for shared access
