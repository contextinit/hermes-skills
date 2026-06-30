#!/usr/bin/env python3
"""
append_turn.py — Append a turn to today's Hermes session log.

Usage:
    python3 append_turn.py --prompt "User prompt text" --response "Assistant response text" [--turn 003]

The script:
- Locates or creates today's session file under Hermes_Memory/Sessions/
- Appends a properly formatted turn block
- Auto-increments turn numbers if --turn is omitted
- Never edits or rewrites existing turns

Outputs the turn number written (for chaining from hooks).
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────────
MEMORY_DIR = Path(os.environ.get(
    "HERMES_MEMORY_DIR",
    "/vault/Hermes_Agent_Folder/Hermes_Memory"
))
SESSIONS_DIR = MEMORY_DIR / "Sessions"
TIMEZONE = os.environ.get("HERMES_TIMEZONE", "America/Chicago")
# ──────────────────────────────────────────────────────────────────────────────────


def today_session_path() -> Path:
    """Return path to today's session file, creating it if missing."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = SESSIONS_DIR / f"{date_str}_Session.md"
    if not path.exists():
        header = (
            f"# Hermes Session Log — {date_str}\n\n"
            f"> **Date:** {date_str}\n"
            f"> **Timezone:** {TIMEZONE}\n"
            f"> **Purpose:** Verbatim user prompts + Hermes responses/actions.\n"
            f"> **Rule:** Append-only. User prompt blocks never edited.\n\n"
            f"---\n\n"
            f"*Session started automatically.*\n\n"
            f"---\n"
        )
        path.write_text(header)
    return path


def last_turn_number(session_path: Path) -> int:
    """Scan the session file for the highest existing turn number."""
    content = session_path.read_text()
    matches = re.findall(r"^## Turn (\d+)", content, re.MULTILINE)
    return max((int(m) for m in matches), default=0)


def append_turn(prompt: str, response: str, turn: int | None = None) -> int:
    """Append a turn block to today's session file."""
    path = today_session_path()
    now = datetime.now().strftime("%H:%M:%S")
    if turn is None:
        turn = last_turn_number(path) + 1

    block = (
        f"\n## Turn {turn:03d} — {now}\n\n"
        f"### User Prompt — Verbatim\n\n"
        f"```text\n{prompt}\n```\n\n"
        f"### Hermes Response / Actions\n\n"
        f"```markdown\n{response}\n```\n\n"
        f"---\n"
    )
    with path.open("a") as f:
        f.write(block)
    return turn


def main():
    parser = argparse.ArgumentParser(description="Append a turn to today's Hermes session log.")
    parser.add_argument("--prompt", required=True, help="The user's verbatim prompt")
    parser.add_argument("--response", required=True, help="The assistant's response / action summary")
    parser.add_argument("--turn", type=int, default=None, help="Explicit turn number (auto if omitted)")
    args = parser.parse_args()

    turn = append_turn(args.prompt, args.response, args.turn)
    print(turn)


if __name__ == "__main__":
    main()
