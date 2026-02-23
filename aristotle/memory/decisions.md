# Decision Log

*Major decisions with reasoning, for future reference and challenge.*

---

## 2026-02-15: Express.js for Dashboard

**Decision:** Use Express.js as the web framework

**Context:** Building a status dashboard for the 3-bot team

**Alternatives Considered:**
- **Fastify** — Faster, but less middleware ecosystem
- **Raw Node http** — Too low-level for rapid development
- **Next.js** — Overkill for a simple dashboard

**Reasoning:** Express has the largest ecosystem, most examples, and is "good enough" for our current scale. We can migrate later if needed.

**Revisit if:** Performance becomes a bottleneck, or we need SSR/React features

---

## 2026-02-15: Single Workspace Repository

**Decision:** Keep all of Aristotle's work in one git repo (`clawd-aristotle`)

**Context:** Need version control for code, docs, and project files

**Alternatives Considered:**
- **Separate repo per project** — More isolation, but coordination overhead
- **Monorepo with multiple packages** — Overkill for current size

**Reasoning:** Everything here serves one purpose: Aristotle's coordination work. One repo keeps it simple. Sub-agents (Daedalus, Thales) have their own workspaces for their persistent context.

**Revisit if:** Projects become large enough to warrant separation

---

## 2026-02-15: Branch Model (main/dev/feature)

**Decision:** Use a lightweight Git Flow variant

**Context:** Need safe way to develop features without breaking stable code

**Alternatives Considered:**
- **Trunk-based development** — Simpler, but riskier without CI/CD
- **Full Git Flow** — Too heavyweight for a small team

**Reasoning:** Feature branches give isolation. Merging to main only after review ensures stability. Dev branch optional for integration testing.

**Revisit if:** We add CI/CD pipelines and can trust automated testing

---

## 2026-02-15: Aristotle Reviews All Deliverables

**Decision:** All sub-agent work goes through Aristotle before being considered "done"

**Context:** Need quality control without constant human involvement

**Alternatives Considered:**
- **Direct to Aaron** — Wastes Aaron's time on routine reviews
- **Peer review (agents review each other)** — Coordination complexity, unclear authority
- **No review** — Too risky

**Reasoning:** Single point of accountability. Aristotle understands the full context and can catch issues before they reach Aaron. Escalate to Aaron only for big decisions.

**Revisit if:** Team grows or review becomes a bottleneck

---
