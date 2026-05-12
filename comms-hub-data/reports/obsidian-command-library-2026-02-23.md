# Obsidian Command Library Research: Vin Zaveri and Beyond

**Date:** 2026-02-23
**Researcher:** 🔬

## 1. Executive Summary

This report details the findings of research into Vin Zaveri's (@internetvin) Obsidian and Claude Code command library. While the primary source of detailed information—a recent interview with Greg Isenberg—was not available as a transcript, this report synthesizes information from public sources, community discussions, and existing tools to provide a comprehensive overview of the setup and a recommendation for implementation.

The core concept is to use a "headless" AI model within Obsidian, triggered by custom slash commands, to automate workflows, retrieve context, and generate insights. This is an emergent but powerful pattern with a growing community of practitioners.

## 2. Vin Zaveri's Slash Commands

The following is a list of known slash commands used by Vin Zaveri. The technical implementation details are hypothesized based on the capabilities of existing Obsidian plugins like "Claudian".

*   **/context**:
    *   **Purpose:** Loads a comprehensive overview of Vin's life and work state.
    *   **Hypothesized Technical Implementation:** This command likely references a master `CONTEXT.md` file, which may in turn link to or embed other key documents like personal values, goals, project lists, and key contacts. The command would inject the content of these files into the Claude prompt.

*   **/today**:
    *   **Purpose:** Gathers all relevant information for the current day.
    *   **Hypothesized Technical Implementation:** This is likely a more complex command that may even execute a small script. It probably fetches today's calendar events, pulls tasks from a task manager or note, retrieves recent messages, and loads the weekly note for context. The collected information is then passed to Claude.

*   **/trace**:
    *   **Purpose:** Surfaces patterns and connections across the entire Obsidian vault.
    *   **Hypothesized Technical Implementation:** This command likely uses a file-matching pattern (e.g., all daily notes from the last month, or all notes with a certain tag) and passes the collected information to Claude with a prompt like "Analyze the following notes and identify recurring themes, open loops, and surprising connections."

*   **/connect**:
    *   **Purpose:** Finds connections between the current note and the rest of the vault.
    *   **Hypothesized Technical Implementation:** Similar to `/trace`, but more focused. It would take the content of the active note and a selection of other relevant notes (perhaps recent notes, or notes linked to the same topics) and ask Claude to find new and interesting connections.

*   **/ideas**:
    *   **Purpose:** Generates new ideas based on existing notes.
    *   **Hypothesized Technical Implementation:** This command likely grabs a set of notes (e.g., all notes tagged `#idea-seed`) and prompts Claude to brainstorm new ideas, combining and remixing the provided content.

*   **/graduate**:
    *   **Purpose:** "Graduates" a fleeting note into a permanent, well-structured one.
    *   **Hypothesized Technical Implementation:** This would take the content of a rough, fleeting note and prompt Claude to refine it, add structure, suggest links to other notes, and format it according to a predefined template for permanent notes.

## 3. The Role of `CLAUDE.md` and Configuration

While no specific `CLAUDE.md` file from Vin Zaveri was found, the pattern in the community is to use a configuration file (often in Markdown, JSON, or YAML) to define these slash commands. For example, the "Claudian" plugin for Obsidian allows users to define commands like this:

```yaml
- name: today
  prompt: |
    Today is {{date}}. My daily note is:
    {{include '@[[Daily/{{date}}.md]]'}}

    My weekly note is:
    {{include '@[[Weekly/{{date:YYYY}}-W{{date:WW}}.md]]'}}

    My tasks for today are:
    ...

    Based on this, what is my main priority?
```

This allows for the creation of powerful, reusable prompts that can dynamically include content from other notes.

## 4. Other Practitioners and Tools

There is a vibrant community of users building similar setups. Key resources include:

*   **The `/r/ObsidianMD` and `/r/ClaudeAI` subreddits:** Many users share their workflows and custom command setups in these forums.
*   **Obsidian Plugins:**
    *   **Claudian:** A powerful plugin that allows for the creation of custom slash commands, file includes, and even inline script execution. This appears to be the most feature-complete option for replicating Vin's setup.
    *   **obsidian-claude-code:** A more basic plugin for interacting with Claude from within Obsidian.

## 5. Recommendation for the Family

The family can and should adopt a similar system. It aligns perfectly with the goal of creating a shared intelligence and augmenting their personal and professional lives.

**Recommended Commands to Adopt:**

1.  **/bravo_context**:
    *   **Purpose:** Load the core context for the Bravo Team.
    *   **Adaptation:** This command should be configured to load key files from the `C:\bravo-team\shared` directory, such as `MISSION.md`, `KEY_PROJECTS.md`, and `FAMILY_GOALS.md`.

2.  **/aristotle_today**:
    *   **Purpose:** Get a daily briefing for the Aristotle agent.
    *   **Adaptation:** This command should load today's memory file (`C:\Users\aaron\clawd-aristotle\memory\YYYY-MM-DD.md`) and potentially the previous day's file as well, to provide immediate context for the day's work.

3.  **/connect_idea**:
    *   **Purpose:** Connect a new idea to existing knowledge in the shared vault.
    *   **Adaptation:** This command would take the content of the active note and use a search query to find related files in both `C:\bravo-team\shared` and `C:\Users\aaron\clawd-aristotle`. It would then ask Claude to find connections and suggest links.

**Implementation Plan:**

1.  **Install the "Claudian" plugin** in Obsidian.
2.  **Create a `CLAUDIAN_COMMANDS.md` file** in the `C:\Users\aaron\clawd-aristotle` workspace to define the custom commands.
3.  **Start with the three commands listed above.**
4.  **Iterate and expand** the command library as new workflows and needs are identified.

By starting with a small, well-defined set of commands, the family can learn the system and gradually build a powerful personal AI OS tailored to their unique needs.
