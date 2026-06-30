# Hermes Obsidian Memory — Privacy & Data Handling

## Data Boundary

**All data stays in your local Obsidian vault.** Nothing is sent to external services, no telemetry, no analytics.

## What is Stored

- User prompts (verbatim) in session files under `Hermes_Memory/Sessions/`
- Hermes assistant responses (verbatim or summarized) in the same session files
- Nightly compressed summaries under `Hermes_Memory/Summaries/`
- Task status under `Todo_Tasks/`

## What is NOT Stored

- API keys or credentials
- Files outside `Hermes_Agent_Folder/`
- Any data from other vault folders

## Data Control

- Session files are append-only — never edited, never deleted automatically
- Delete any file manually to remove it permanently
- The cron job only reads `Sessions/` and writes to `Summaries/` — it never modifies session files
- Plugin hooks are non-blocking observer callbacks — errors are logged but never affect Hermes' operation

## Third-Party Dependencies

- **Zero.** No external APIs, no cloud services, no data leaves your machine.
- All processing is local Python scripts or Hermes-native cron jobs.

## License

MIT — do what you want with it.
