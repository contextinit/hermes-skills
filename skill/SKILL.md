---
name: hermes-obsidian-memory
description: "Use when you need persistent, user-reviewable memory across Hermes sessions. Extends Hermes with append-only daily session logs, nightly compressed summaries, task cross-checking, and optional plugin hooks for automatic capture of every turn into your Obsidian vault."
version: 1.0.0
author: Ramgopal M
license: MIT
metadata:
  hermes:
    tags: [memory, obsidian, pkm, second-brain, session, cron, hooks, knowledge-management]
    related_skills: [task-organization-vault]
---

# Hermes Obsidian Memory System

## Overview

Hermes Obsidian Memory solves a fundamental problem: **your Hermes sessions forget what happened last time**. Built-in memory is limited (~800 tokens). Session search helps, but it's slow and unstructured.

This skill creates a persistent, human-reviewable memory layer in your Obsidian vault. Every user prompt is captured verbatim, every Hermes response is recorded, and every night a cron job compresses the day's work into a structured summary — decisions, solutions, errors, pending tasks — cross-checked against your task index.

The result: Hermes can pick up where it left off, even after a fresh session. The system is **append-only** (never edits recorded turns) and **privacy-first** (all data stays in your vault, under your control).

## When to Use

- You want your Hermes sessions to remember context from previous conversations
- You prefer a **file-based, user-reviewable** memory over opaque vector stores
- You use Obsidian for PKM and want your agent conversations indexed there
- You want auto-generated nightly summaries of what was done, decided, and what's pending
- You want **zero external dependencies** — everything runs locally

**Don't use when:** you prefer a pure vector-database memory approach, or you don't use Obsidian.

## Architecture

```text
Obsidian Vault/Hermes_Agent_Folder/
├── Todo_Tasks/                    ← Task tracking
│   ├── __00_Todo_Task_Index.md    ← Master task index (source of truth)
│   └── T##_*.md                   ← Per-task detail files
└── Hermes_Memory/                 ← Memory system ← START HERE
    ├── Hermes_Obsidian_Readme.md  ← System orientation
    ├── __00_Memory_Index.md       ← Navigation: sessions + summaries
    ├── Memory_Implementation_Plan.md
    ├── Sessions/                  ← Append-only daily session logs
    │   └── YYYY-MM-DD_Session.md
    ├── Summaries/                 ← Nightly compressed summaries
    │   └── YYYY-MM-DD_Summary.md
    ├── Templates/                 ← File templates
    ├── Scripts/                   ← Logging helpers
    │   ├── append_turn.py
    │   └── summarize_day.py
    └── Hooks/                     ← Hermes plugin (auto-capture)
        └── hermes-obsidian-memory-plugin/
```

## Installation

```bash
# 1. Copy the package into your vault
cp -r hermes-obsidian-memory-skill/* /path/to/Obsidian/vault/Hermes_Agent_Folder/

# 2. Set up the nightly cron
hermes cron create "15 5 * * *" --name "Memory Summary" \
  --prompt "Run nightly memory summary using Hermes_Memory/Scripts/summarize_day.py"

# 3. (Optional) Install the auto-capture plugin
cd Hermes_Memory/Hooks/hermes-obsidian-memory-plugin && bash install-plugin.sh
hermes restart
```

See [INSTALL.md](./INSTALL.md) for full details, or [QUICKSTART.md](./QUICKSTART.md) for a 60-second setup.

## How It Works

### 1. Session Capture

Every Hermes turn is recorded to `Sessions/YYYY-MM-DD_Session.md`. User prompts go in verbatim (in ` ```text ``` ` blocks). Hermes responses go in ` ```markdown ``` ` blocks. Existing turns are **never edited** — append-only.

**Two capture modes:**
- **Manual:** `python3 Scripts/append_turn.py --prompt "..." --response "..."`
- **Automatic (plugin):** Hermes plugin hooks fire `pre_llm_call` and `post_llm_call` to auto-capture

### 2. Nightly Summarization

A Hermes cron job runs at **12:15 AM CT** (05:15 UTC) daily:
1. Reads yesterday's session file
2. Extracts all turns with `summarize_day.py --raw`
3. Compresses Hermes responses/actions into structured summary sections
4. Cross-checks pending tasks against `Todo_Tasks/__00_Todo_Task_Index.md`
5. Updates `__00_Memory_Index.md`

**User prompts remain untouched** in the session file — only responses are analyzed.

### 3. Context Recovery

At session start, the plugin hook reads the latest 3 nightly summaries and injects them as context into the first user turn. New sessions start informed.

## Startup Protocol

When starting a fresh Hermes session:

1. Read `Hermes_Obsidian_Readme.md` — folder orientation
2. Read `Hermes_Memory/__00_Memory_Index.md` — session inventory
3. Read latest 3-5 summaries from `Hermes_Memory/Summaries/`
4. Read `Todo_Tasks/__00_Todo_Task_Index.md` — current task status
5. Compose a context summary before proceeding

## Design Principles

- **Append-only** — session files are never modified after recording
- **Raw vs compressed** — verbatim in Sessions, compressed in Summaries
- **Task cross-checking** — every nightly summary validates against the Todo Index
- **Calendar discipline** — calendar invites only for date-bound commitments
- **Minimal startup cost** — read summaries, not raw sessions
- **Plugin automates** — zero manual effort after installation
- **Safe by default** — hooks are non-blocking, errors never crash Hermes

## Nightly Summary Structure

```markdown
## Executive Summary
## Decisions Made
## Key Learnings
## Solutions / Fixes Implemented
## Errors & Workarounds
## Pending Tasks Identified (cross-checked vs Todo Index)
## Files Created / Updated
## Follow-up Recommendations
```

## Common Pitfalls

1. **write_file blocked on vault paths.** The `write_file` tool may reject paths under `/vault/`. Use `terminal` with base64-echo instead:
   ```python
   import base64
   encoded = base64.b64encode(content.encode()).decode()
   terminal(f'echo {encoded} | base64 -d > "/path/to/file.md"')
   ```

2. **Heredocs with `&` break in shell.** The `&` character is parsed as a background operator. Always use Python base64 encoding for file writes containing special characters.

3. **Cron timezone mismatch.** The cron schedule `15 5 * * *` is UTC (05:15), which equals 12:15 AM CT during CDT. If the container runs UTC, this is correct. Verify with `date` in the terminal.

4. **Plugin dir wrong.** The plugin defaults `/vault/Hermes_Agent_Folder/Hermes_Memory`. If your vault is elsewhere, set `HERMES_OBSIDIAN_MEMORY_DIR` in your Hermes .env.

5. **`__00_` prefix needed.** `__00_Todo_Task_Index.md` sorts to the top of directory listings, making it easy to find. Regular `Todo_Task_Index.md` gets buried among `T##_*.md` files.

## Verification Checklist

- [ ] `Hermes_Obsidian_Readme.md` exists inside `Hermes_Memory/`
- [ ] `__00_Memory_Index.md` exists and links to valid session/summary files
- [ ] `Scripts/append_turn.py` runs without errors: `python3 append_turn.py --prompt "test" --response "test"`
- [ ] `Scripts/summarize_day.py --date today --raw` produces valid JSON
- [ ] Templates exist in `Templates/` with correct placeholders
- [ ] Plugin `__init__.py` passes `python3 -c "import ast; ast.parse(open(...).read())"`
- [ ] Nightly cron job is listed: `hermes cron list`
