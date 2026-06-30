# Hermes Obsidian Memory — 60-Second Quickstart

```bash
# 1. Extract
cd ~/Obsidian/Vault/Hermes_Agent_Folder
unzip ~/Downloads/hermes-obsidian-memory-skill-v1.0.zip

# 2. Log your first turn
cd Hermes_Memory
python3 Scripts/append_turn.py --prompt "Hello world" --response "First memory captured"

# 3. Verify it worked
cat Sessions/$(date +%Y-%m-%d)_Session.md | head -20

# 4. Done. Memory is live.
```

**For daily summaries, add the cron job** (see INSTALL.md step 3).
**For auto-capture, install the plugin** (see INSTALL.md step 5).
