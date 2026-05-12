# Diagramming Tools Deep Dive: Analysis and Recommendation

**Date:** 2026-02-23
**To:** Aaron
**From:** Researcher 🔬

## 1. The Key Question

You asked for a diagramming tool that is (a) newer than Mermaid, (b) reactive to markdown/vault changes, and (c) connects to Obsidian with wikilinks. The primary use case is documenting SOPs, workflows, and system architectures.

After a deep dive into the available options, the clear recommendation is **Obsidian Canvas**, with **D2** as a secondary tool for specific, complex diagrams.

---

## 2. Recommendation: Obsidian Canvas

Obsidian Canvas is the best fit for the core requirements, particularly the "reactivity" and deep Obsidian integration.

*   **What it is:** A core plugin in Obsidian that provides an infinite, freeform canvas where you can place notes, cards, images, and connect them with arrows.
*   **Why it wins:**
    *   **Perfect Obsidian Integration:** It's a native feature. It doesn't get any better.
    *   **True Wikilink Support:** You don't just *link* to notes; you can drag your actual markdown files (`[[note]]`) onto the canvas. They appear as interactive, live-updating cards. This is the ultimate form of "wikilink support" as the diagram is built from the notes themselves.
    *   **Programmatically Generatable:** This is the killer feature. Canvas files are stored as simple `.canvas` JSON files. This means an agent or script can be written to:
        1.  Scan a directory of markdown files.
        2.  Parse the wikilinks between them.
        3.  Automatically generate a `.canvas` file that visually represents the relationships.
    *   **Reactive On-Demand:** While not "live-watching" files, an agent can regenerate the canvas at any time to reflect the current state of the vault. This achieves the goal of a diagram that is always in sync with the documentation.

### Setup Steps:

1.  **Enable the Plugin:** Go to `Settings` > `Core Plugins` and ensure `Canvas` is enabled.
2.  **Create a New Canvas:** Use the command palette (`Ctrl/Cmd+P`) and type "Create new canvas".
3.  **Add Notes:** Drag markdown files from the file explorer pane directly onto the canvas.
4.  **Connect Them:** Click and drag from the circular handles on any card to draw connection arrows to other cards.

### Agent-Driven Workflow (The "Reactive" Part):

A future agent task could be: `"Given the folder 'SOPs', create a canvas that diagrams the flow based on the 'next_step' wikilinks in each file."` The agent would then generate `SOPs.canvas` for you.

---

## 3. Runner-Up: D2 (by Terrastruct)

For situations where you need a highly structured, beautiful diagram and are willing to write the code for it, D2 is the best modern "diagrams-as-code" tool.

*   **What it is:** A modern, declarative language for creating diagrams, released in 2022.
*   **Why it's great:**
    *   **Superior Layout Engine:** It uses the ELK layout engine, which is significantly more advanced than Mermaid's. It produces cleaner, more readable diagrams from complex definitions with minimal manual tweaking.
    *   **Self-Contained:** It's a Go binary that runs locally. No external services needed.
    *   **Good Obsidian Plugin:** The official D2 plugin lets you render `d2` code blocks directly in your notes.

*   **Where it falls short:**
    *   **Not truly reactive to the vault.** It doesn't parse your vault's wikilinks to create a graph. It only renders the code you explicitly write in a code block. While you can embed `obsidian://` links, it's a manual process.

### Setup Steps:

1.  **Install D2:** Follow the official installation instructions at [d2lang.com](https://d2lang.com).
2.  **Install the Obsidian Plugin:** Go to `Settings` > `Community Plugins` > `Browse` and search for "D2". Install and enable it.
3.  **Use it:** Create a code block in a note like so:
    ```d2
    SOP-1 -> SOP-2: "User submits form"
    SOP-2 -> SOP-3: "Approval"
    ```
    The plugin will render it as a diagram.

---

## 4. Analysis of Other Tools

*   **Markmap:** Only visualizes the structure (headers, lists) of a *single* markdown file. It is not vault-aware and does not create diagrams from links between files. Useful for outlining, not for architecture.
*   **Foam (VS Code):** An excellent tool, but it's an *alternative* to an Obsidian-centric workflow, not an integration. It provides a reactive graph of a markdown folder, but for VS Code users.
*   **Quartz:** A static site generator for publishing an Obsidian vault. It's for creating a public-facing website with a graph view, not for diagramming *within* Obsidian for internal documentation.

## 5. Final Answer

For a diagramming tool that is deeply integrated with Obsidian and can be made reactive to the structure of your vault, **Obsidian Canvas is the clear winner.** Its native integration and the ability for agents to programmatically generate and update diagrams make it a future-proof solution for documenting complex systems.

Use **D2** when you need to hand-craft a specific, publication-quality diagram and the automatic layout is the most important feature.
