# Hermes Obsidian Memory — Installation Guide

## Prerequisites

- Hermes Agent (any provider)
- Obsidian vault with write access
- Python 3.10+

## Step-by-Step

### 1. Extract the package into your vault

```bash
# Assuming your Obsidian vault is at ~/Obsidian/Vault
unzip hermes-obsidian-memory-skill-v1.0.zip -d ~/Obsidian/Vault/Hermes_Agent_Folder/
```

### 2. Verify the structure

```bash
ls ~/Obsidian/Vault/Hermes_Agent_Folder/Hermes_Memory/
# Should see: __00_Memory_Index.md  Hermes_Obsidian_Readme.md  Scripts/  Sessions/  Summaries/  Templates/  Hooks/
```

### 3. Set up the nightly cron job

```bash
hermes cron create "15 5 * * *" \
  --name "Hermes Nightly Memory Summary" \
  --prompt "Run the nightly Hermes memory summarization for yesterday's session at /path/to/Hermes_Memory/Sessions/."
```

### 4. Test the logging script

```bash
cd ~/Obsidian/Vault/Hermes_Agent_Folder/Hermes_Memory
python3 Scripts/append_turn.py --prompt "Installation test" --response "Testing capture"
cat Sessions/$(date +%Y-%m-%d)_Session.md
```

### 5. (Optional) Install the auto-capture plugin

```bash
bash Hooks/hermes-obsidian-memory-plugin/install-plugin.sh
hermes restart
```

### 6. Verify

```bash
hermes cron list
hermes plugins list
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `HERMES_OBSIDIAN_MEMORY_DIR` | `/vault/Hermes_Agent_Folder/Hermes_Memory` | Root of the memory system |
| `TODO_DIR` | `/vault/Hermes_Agent_Folder/Todo_Tasks` | Root of the task index |
