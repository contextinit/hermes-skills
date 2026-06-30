"""
Hermes Obsidian Memory Plugin — Auto-capture user prompts and responses to vault session files.

Register hooks:
- pre_llm_call:   Capture user prompt, inject latest 3 summaries as context
- post_llm_call:   Capture assistant response for this turn
- on_session_start: Log session start metadata
- on_session_end:   Flush any buffered content

Installation:
    1. Copy this directory to ~/.hermes/plugins/hermes-obsidian-memory/
    2. Enable with: hermes plugins install hermes-obsidian-memory
    3. Configure paths in the plugin config
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PLUGIN_NAME = "hermes-obsidian-memory"

# ─── Configuration (override via env vars) ──────────────────────────────────────
MEMORY_DIR = Path(os.environ.get(
    "HERMES_OBSIDIAN_MEMORY_DIR",
    "/vault/Hermes_Agent_Folder/Hermes_Memory"
))
APPEND_SCRIPT = MEMORY_DIR / "Scripts" / "append_turn.py"
SUMMARIES_DIR = MEMORY_DIR / "Summaries"
INDEX_PATH = MEMORY_DIR / "__00_Memory_Index.md"
# ─────────────────────────────────────────────────────────────────────────────────

_turn_buffer: dict | None = None
"""Buffer for the current turn's data while the LLM is processing."""


def _call_append_script(prompt: str, response: str) -> str | None:
    """Shell out to append_turn.py and return turn number string."""
    try:
        result = subprocess.run(
            [sys.executable, str(APPEND_SCRIPT),
             "--prompt", prompt,
             "--response", response],
            capture_output=True, text=True, timeout=10,
            cwd=os.path.dirname(APPEND_SCRIPT),
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"[{PLUGIN_NAME}] append_turn.py stderr: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"[{PLUGIN_NAME}] append_turn.py error: {e}")
        return None


def _read_recent_summaries(count: int = 3) -> str:
    """Read last N summary files for context injection."""
    if not SUMMARIES_DIR.exists():
        return ""
    files = sorted(SUMMARIES_DIR.glob("*_Summary.md"), reverse=True)[:count]
    parts = []
    for f in files:
        date_str = f.stem.replace("_Summary", "")
        content = f.read_text()[:1500]  # trim to avoid bloat
        parts.append(f"=== {date_str} Summary ===\n{content}")
    return "\n\n".join(parts)


def register(ctx):
    """Register plugin hooks with the Hermes agent context."""

    @ctx.register_hook("on_session_start")
    async def on_session_start(session_id: str, **kwargs):
        """Log session start metadata."""
        print(f"[{PLUGIN_NAME}] Session started: {session_id}")
        # Future: append session start to daily session file

    @ctx.register_hook("on_session_end")
    async def on_session_end(session_id: str, **kwargs):
        """Flush on session end."""
        global _turn_buffer
        _turn_buffer = None

    @ctx.register_hook("pre_llm_call")
    async def pre_llm_call(
        session_id: str,
        user_message: str,
        conversation_history: list,
        is_first_turn: bool,
        model: str,
        platform: str,
        **kwargs,
    ):
        """
        Called once per turn before LLM processing.

        Two responsibilities:
        1. Buffer the user prompt for later pairing with the response.
        2. On first turn, inject recent summaries as context.
        """
        global _turn_buffer
        _turn_buffer = {"prompt": user_message, "response": None}

        # Inject recent summaries only on first turn of a session
        context = {}
        if is_first_turn:
            summaries = _read_recent_summaries(count=3)
            if summaries:
                context["context"] = (
                    "─── Hermes Obsidian Memory Recent Context ───\n"
                    f"{summaries}\n"
                    "─── End Memory Context ───"
                )
        return context if context else None

    @ctx.register_hook("post_llm_call")
    async def post_llm_call(
        session_id: str,
        messages: list,
        response: str,
        **kwargs,
    ):
        """
        Called after LLM call returns.

        Pairs the buffered user prompt with the assistant response
        and writes both to the daily session file via append_turn.py.
        """
        global _turn_buffer
        if _turn_buffer is None:
            print(f"[{PLUGIN_NAME}] WARNING: no buffered prompt for post_llm_call")
            return

        _turn_buffer["response"] = response
        turn = _call_append_script(
            prompt=_turn_buffer["prompt"],
            response=_turn_buffer["response"],
        )
        if turn:
            print(f"[{PLUGIN_NAME}] Captured turn {turn}")
        else:
            print(f"[{PLUGIN_NAME}] Failed to capture turn")
        _turn_buffer = None
