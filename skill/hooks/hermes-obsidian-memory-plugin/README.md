# Hermes Obsidian Memory Plugin

Auto-capture every user prompt and Hermes response to daily session files in an Obsidian vault.

## Features

- **pre_llm_call hook**: Captures the user's exact prompt before LLM processing.
- **post_llm_call hook**: Captures the assistant's final response after generation.
- **Context injection**: On first turn of each session, reads the latest 3 nightly summaries and injects them as context so Hermes remembers past sessions.
- **Append-only**: Writes to daily session files in Hermes_Memory/Sessions/ — never edits existing turns.
- **Zero risk**: Hooks are non-blocking. Errors are logged but never crash the agent.

## Installation

```bash
# From the vault where the plugin lives:
cp -r Hermes_Memory/Hooks/hermes-obsidian-memory-plugin ~/.hermes/plugins/

# Or use the installer:
bash Hermes_Memory/Hooks/hermes-obsidian-memory-plugin/install-plugin.sh [--hermes-dir ~/.hermes]

# Restart Hermes (or use /reset in current session)
hermes restart
```

## Verification

```bash
hermes plugins list
# Should show "hermes-obsidian-memory" in the list
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `HERMES_OBSIDIAN_MEMORY_DIR` | `/vault/Hermes_Agent_Folder/Hermes_Memory` | Root of the memory folder |

## Requirements

- Hermes Agent with plugin hook support
- Python 3.10+
- Read/write access to the Obsidian vault's Hermes_Agent_Folder

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Plugin code with all hook registrations |
| `install-plugin.sh` | One-command installer that copies files to ~/.hermes/plugins/ |
