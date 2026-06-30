#!/usr/bin/env python3
"""
summarize_day.py — Nightly session summarization helper.

Designed to be called by a Hermes cron job (Phase 3) or as a preprocessor.
This script:
1. Identifies today's or yesterday's session file.
2. Extracts the day's turn blocks and filters for structure.
3. Outputs the relevant context to stdout for the LLM summary step.
4. Is safe, scoped, and never modifies the session file.

Usage:
    python3 summarize_day.py                      # yesterday's session (for post-midnight cron)
    python3 summarize_day.py --date 2026-06-30     # specific date
    python3 summarize_day.py --date today          # today's session
    python3 summarize_day.py --raw                 # dump full session lineage
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = Path(os.environ.get(
    "HERMES_MEMORY_DIR",
    "/vault/Hermes_Agent_Folder/Hermes_Memory"
))
SESSIONS_DIR = MEMORY_DIR / "Sessions"
SUMMARIES_DIR = MEMORY_DIR / "Summaries"
TODO_DIR = Path(os.environ.get(
    "TODO_DIR",
    "/vault/Hermes_Agent_Folder/Todo_Tasks"
))


def resolve_date(date_arg: str | None) -> str:
    """Return YYYY-MM-DD string for --date argument."""
    if date_arg is None or date_arg == "yesterday":
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_arg == "today":
        return datetime.now().strftime("%Y-%m-%d")
    else:
        # validate format
        try:
            datetime.strptime(date_arg, "%Y-%m-%d")
            return date_arg
        except ValueError:
            print(f"ERROR: invalid date '{date_arg}'. Use YYYY-MM-DD, 'today', or 'yesterday'.", file=sys.stderr)
            sys.exit(1)


def parse_turns(content: str) -> list[dict]:
    """Parse a session file into a list of turn dicts."""
    turns = []
    blocks = re.split(r"^## Turn ", content, flags=re.MULTILINE)
    for block in blocks[1:]:  # first split is the header
        lines = block.strip().split("\n")
        turn_header = lines[0].strip()  # e.g. "001 — 14:30:00"
        turn_num = turn_header.split("—")[0].strip()
        time_str = turn_header.split("—")[-1].strip() if "—" in turn_header else ""

        # Extract user prompt
        prompt_match = re.search(r"```text\n(.+?)\n```", block, re.DOTALL)
        user_prompt = prompt_match.group(1).strip() if prompt_match else ""

        # Extract response
        response_match = re.search(r"```markdown\n(.+?)\n```", block, re.DOTALL)
        response = response_match.group(1).strip() if response_match else ""

        turns.append({
            "turn": turn_num,
            "time": time_str,
            "user_prompt": user_prompt,
            "response": response,
        })
    return turns


def get_todo_task_index() -> str:
    """Read the todo task index if it exists, returning a summary."""
    index_path = TODO_DIR / "__00_Todo_Task_Index.md"
    if index_path.exists():
        content = index_path.read_text()
        # extract only the Active/In Progress sections for compactness
        active = ""
        lines = content.split("\n")
        capture = False
        for line in lines:
            if "🟢 Active" in line or "🔵 In Progress" in line:
                capture = True
            if capture:
                active += line + "\n"
                if line.strip() == "" and capture:
                    break
        return active[:2000] if active else "(no active tasks found)"
    return "(todo index not found)"


def main():
    parser = argparse.ArgumentParser(description="Nightly session summarization helper")
    parser.add_argument("--date", default=None, help="Date YYYY-MM-DD, 'today', or 'yesterday'")
    parser.add_argument("--raw", action="store_true", help="Dump full session data as JSON")
    args = parser.parse_args()

    date_str = resolve_date(args.date)
    session_path = SESSIONS_DIR / f"{date_str}_Session.md"
    summary_path = SUMMARIES_DIR / f"{date_str}_Summary.md"

    if not session_path.exists():
        print(f"No session log found for {date_str}")
        sys.exit(0)

    content = session_path.read_text()
    turns = parse_turns(content)

    if args.raw:
        print(json.dumps({
            "date": date_str,
            "session_file": str(session_path),
            "summary_file": str(summary_path),
            "turn_count": len(turns),
            "turns": turns,
        }, indent=2))
        return

    # Output compact context for LLM cron summarizer
    print(f"=== Session Summary Context: {date_str} ===\n")
    print(f"Session file: {session_path}")
    print(f"Total turns: {len(turns)}\n")

    for t in turns:
        print(f"--- Turn {t['turn']} at {t['time']} ---")
        print(f"USER PROMPT: {t['user_prompt'][:300]}")
        print(f"RESPONSE: {t['response'][:500]}")
        print()

    print("=== Current Todo Tasks === ")
    print(get_todo_task_index())


if __name__ == "__main__":
    main()
