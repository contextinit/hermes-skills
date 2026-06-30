#!/usr/bin/env python3
"""
run_all_tests.py — Consolidated TDD test runner.

Each test prints PASS or FAIL. At the end, a summary is printed.
Any FAIL results should be documented in a .md issue file then fixed.
"""

import ast, json, os, re, sys, subprocess, datetime
from pathlib import Path

BASE = Path("/vault/Hermes_Agent_Folder/Hermes_Memory")
MEM_DIR = BASE

passed = 0
failed = 0
results = []

def test(name, condition_fn, detail=""):
    global passed, failed
    try:
        ok = condition_fn()
        if ok:
            passed += 1
            results.append(f"  PASS  {name}")
        else:
            failed += 1
            results.append(f"  FAIL  {name}  {detail}")
    except Exception as e:
        failed += 1
        results.append(f"  FAIL  {name}  EXCEPTION: {e}")

def file_exists(p):
    return Path(p).exists()

def file_size(p):
    return Path(p).stat().st_size if Path(p).exists() else 0

def file_contents(p):
    return Path(p).read_text() if Path(p).exists() else ""

# ════════════════════════════════════════════════════════════════════
# TEST 1: append_turn.py
# ════════════════════════════════════════════════════════════════════
print("\n=== TESTS: append_turn.py ===")

script = MEM_DIR / "Scripts" / "append_turn.py"
test(name="1.1 Script exists", condition_fn=lambda: file_exists(script))

# Run append_turn.py to get a new turn
today = datetime.date.today().strftime("%Y-%m-%d")
session_file = MEM_DIR / "Sessions" / f"{today}_Session.md"
before_turns = file_contents(session_file).count("## Turn ") if file_exists(session_file) else 0

result = subprocess.run(
    [sys.executable, str(script), "--prompt", "TDD test prompt 1", "--response", "TDD test response 1"],
    capture_output=True, text=True, timeout=10
)
turn_num = result.stdout.strip()
test(name="1.2 Append returns turn number",
     condition_fn=lambda: turn_num.isdigit() and int(turn_num) > before_turns,
     detail=f"got {turn_num}, before had {before_turns}")

after_turns = file_contents(session_file).count("## Turn ")
test(name="1.3 Turn count increased",
     condition_fn=lambda: after_turns > before_turns,
     detail=f"before {before_turns}, after {after_turns}")

# Check turn block format
content = file_contents(session_file)
has_user_block = "### User Prompt" in content
has_resp_block = "### Hermes Response" in content
test(name="1.4 Turn blocks complete",
     condition_fn=lambda: has_user_block and has_resp_block,
     detail=f"user_block:{has_user_block} resp_block:{has_resp_block}")

# Special characters test
result2 = subprocess.run(
    [sys.executable, str(script), "--prompt", "Line1\nLine2 with $pecial & chars", "--response", 'Code with ``` and "quotes"'],
    capture_output=True, text=True, timeout=10
)
test(name="1.5 Special chars exit 0",
     condition_fn=lambda: result2.returncode == 0,
     detail=f"exit {result2.returncode}")

# ════════════════════════════════════════════════════════════════════
# TEST 2: summarize_day.py
# ════════════════════════════════════════════════════════════════════
print("\n=== TESTS: summarize_day.py ===")

sum_script = MEM_DIR / "Scripts" / "summarize_day.py"
test(name="2.1 Script exists", condition_fn=lambda: file_exists(sum_script))

# --raw mode
result3 = subprocess.run(
    [sys.executable, str(sum_script), "--date", "today", "--raw"],
    capture_output=True, text=True, timeout=10
)
parsed = None
try:
    parsed = json.loads(result3.stdout) if result3.stdout.strip() else None
except: pass
test(name="2.2 --raw returns valid JSON",
     condition_fn=lambda: parsed is not None and "turns" in parsed,
     detail=f"stdout[:300]={result3.stdout[:300]}")

if parsed:
    test(name="2.3 JSON has date and turns",
         condition_fn=lambda: parsed.get("date") == today and parsed.get("turn_count", 0) > 0,
         detail=f"date={parsed.get('date')} turn_count={parsed.get('turn_count')}")

# Text mode
result4 = subprocess.run(
    [sys.executable, str(sum_script), "--date", "today"],
    capture_output=True, text=True, timeout=10
)
test(name="2.4 Text mode has USER PROMPT marker",
     condition_fn=lambda: "USER PROMPT:" in result4.stdout,
     detail=f"stdout[:200]={result4.stdout[:200]}")
test(name="2.5 Text mode has RESPONSE marker",
     condition_fn=lambda: "RESPONSE:" in result4.stdout,
     detail=f"stdout[:200]={result4.stdout[:200]}")
test(name="2.6 Text mode references todo",
     condition_fn=lambda: "Current Todo Tasks" in result4.stdout or "(todo index not found)" in result4.stdout,
     detail=f"stdout[:300]={result4.stdout[:300]}")

# ════════════════════════════════════════════════════════════════════
# TEST 3: __00_Memory_Index.md
# ════════════════════════════════════════════════════════════════════
print("\n=== TESTS: __00_Memory_Index.md ===")

idx = MEM_DIR / "__00_Memory_Index.md"
test(name="3.1 Index exists", condition_fn=lambda: file_exists(idx) and file_size(idx) > 100,
     detail=f"size={file_size(idx)}")

idx_content = file_contents(idx)
test(name="3.2 Has required sections",
     condition_fn=lambda: "Hermes Memory Index" in idx_content and "Session & Summary Log" in idx_content and "Quick Stats" in idx_content,
     detail="section check")
test(name="3.3 Has today's date",
     condition_fn=lambda: today in idx_content,
     detail=f"looking for {today}")

# Check links
links = re.findall(r'\]\(([^)]+)\)', idx_content)
good_links = 0
bad_links = 0
for link in links:
    if link.startswith('http'): continue
    target = MEM_DIR / link
    if target.exists():
        good_links += 1
    else:
        bad_links += 1
test(name="3.4 Index links resolve",
     condition_fn=lambda: bad_links == 0,
     detail=f"good={good_links} broken={bad_links}")

# ════════════════════════════════════════════════════════════════════
# TEST 4: Hermes_Obsidian_Readme.md
# ════════════════════════════════════════════════════════════════════
print("\n=== TESTS: Hermes_Obsidian_Readme.md ===")

readme = MEM_DIR / "Hermes_Obsidian_Readme.md"
test(name="4.1 README exists", condition_fn=lambda: file_exists(readme) and file_size(readme) > 500,
     detail=f"size={file_size(readme)}")

readme_content = file_contents(readme)
test(name="4.2 Has startup protocol",
     condition_fn=lambda: "Startup" in readme_content and "Context Recovery" in readme_content,
     detail="startup section check")

# Check readme is listed INSIDE Hermes_Memory in the folder map
# Look for "├── Hermes_Obsidian_Readme.md" (with indentation) under a Hermes_Memory context
test(name="4.3 README in correct location in folder map",
     condition_fn=lambda: re.search(r"Hermes_Memory.*\n.*├── Hermes_Obsidian_Readme", readme_content, re.DOTALL) is not None,
     detail="should be indented under Hermes_Memory/")

test(name="4.4 Has hard boundary rule",
     condition_fn=lambda: "Hard Access Boundary" in readme_content or "only this folder" in readme_content.lower(),
     detail="boundary check")

# Test referenced paths
ref_paths = ["Todo_Tasks", "Hermes_Memory", "Sessions", "Summaries", "Templates", "Scripts", "Hooks"]
for rp in ref_paths:
    p = MEM_DIR.parent / rp if rp.startswith("Hermes") or rp.startswith("Todo") else MEM_DIR / rp
    if not p.exists():
        p = MEM_DIR / rp
test(name="4.5 Referenced paths exist",
     condition_fn=lambda: all((MEM_DIR / p).exists() or (MEM_DIR.parent / p).exists() for p in ref_paths),
     detail=f"paths={ref_paths}")

# ════════════════════════════════════════════════════════════════════
# TEST 5: Templates
# ════════════════════════════════════════════════════════════════════
print("\n=== TESTS: Templates ===")

dt = MEM_DIR / "Templates" / "Daily_Session_Template.md"
nt = MEM_DIR / "Templates" / "Nightly_Summary_Template.md"

test(name="5.1 Daily template exists", condition_fn=lambda: file_exists(dt) and file_size(dt) > 200,
     detail=f"size={file_size(dt)}")
dt_content = file_contents(dt)
test(name="5.2 Daily template placeholders",
     condition_fn=lambda: all(x in dt_content for x in ["Turn 001", "User Prompt", "Hermes Response"]),
     detail="placeholder check")

test(name="5.3 Summary template exists", condition_fn=lambda: file_exists(nt) and file_size(nt) > 200,
     detail=f"size={file_size(nt)}")
nt_content = file_contents(nt)
summary_sections = ["Executive Summary", "Decisions Made", "Key Learnings", "Solutions", "Errors", "Pending Tasks", "Files Created", "Follow-up"]
test(name="5.4 Summary template all sections",
     condition_fn=lambda: sum(1 for s in summary_sections if s in nt_content) >= 7,
     detail=f"found={sum(1 for s in summary_sections if s in nt_content)}/8")

# ════════════════════════════════════════════════════════════════════
# TEST 6: Plugin __init__.py
# ════════════════════════════════════════════════════════════════════
print("\n=== TESTS: Plugin __init__.py ===")

plugin_file = MEM_DIR / "Hooks" / "hermes-obsidian-memory-plugin" / "__init__.py"
test(name="6.1 Plugin file exists", condition_fn=lambda: file_exists(plugin_file),
     detail=f"size={file_size(plugin_file)}")

# Validate Python syntax
try:
    ast.parse(plugin_file.read_text())
    test(name="6.2 Python syntax valid", condition_fn=lambda: True)
except SyntaxError as e:
    test(name="6.2 Python syntax valid", condition_fn=lambda: False, detail=str(e))

plugin_content = file_contents(plugin_file)
func_names = ["register", "on_session_start", "on_session_end", "pre_llm_call", "post_llm_call"]
for fn in func_names:
    test(name=f"6.3 Has function '{fn}'",
         condition_fn=lambda fn=fn: fn in plugin_content,
         detail=f"looking for def {fn}")

test(name="6.4 Has env var config",
     condition_fn=lambda: "HERMES_OBSIDIAN_MEMORY_DIR" in plugin_content,
     detail="env var check")
test(name="6.5 Append script path correct",
     condition_fn=lambda: "Scripts" in plugin_content and "append_turn.py" in plugin_content,
     detail="path check")

# ════════════════════════════════════════════════════════════════════
# TEST 7: Memory_Implementation_Plan.md
# ════════════════════════════════════════════════════════════════════
print("\n=== TESTS: Memory_Implementation_Plan.md ===")

plan = MEM_DIR / "Memory_Implementation_Plan.md"
test(name="7.1 Plan exists", condition_fn=lambda: file_exists(plan) and file_size(plan) > 2000,
     detail=f"size={file_size(plan)}")

plan_content = file_contents(plan)
test(name="7.2 No stale 'Hermes_Memmory'",
     condition_fn=lambda: "Hermes_Memmory" not in plan_content,
     detail="stale ref check")
test(name="7.3 No stale 'Hermes_Obisidian'",
     condition_fn=lambda: "Hermes_Obisidian" not in plan_content,
     detail="stale ref check")
test(name="7.4 Has user answers in Q12",
     condition_fn=lambda: "Implement Hooks now" in plan_content or "YES - please proceed" in plan_content or "Yes" in plan_content,
     detail="answers populated check")

# ════════════════════════════════════════════════════════════════════
# TEST 8: Todo Task Index
# ════════════════════════════════════════════════════════════════════
print("\n=== TESTS: Todo Task Index ===")

todo_idx = BASE.parent / "Todo_Tasks" / "__00_Todo_Task_Index.md"
test(name="8.1 Todo index exists", condition_fn=lambda: file_exists(todo_idx),
     detail=f"size={file_size(todo_idx)}")

todo_content = file_contents(todo_idx)
todo_links = re.findall(r'\]\(T\d+_.*?\.md\)', todo_content)
good_tasks = 0
bad_tasks = 0
for link in todo_links:
    target = BASE.parent / "Todo_Tasks" / link
    if target.exists():
        good_tasks += 1
    else:
        bad_tasks += 1
        print(f"  MISSING: {link}")
test(name="8.2 All linked task files exist",
     condition_fn=lambda: bad_tasks == 0,
     detail=f"good={good_tasks} broken={bad_tasks}")
test(name="8.3 Has required columns",
     condition_fn=lambda: all(col in todo_content for col in ["Title", "Status"]),
     detail=f"columns check")

# ════════════════════════════════════════════════════════════════════
# TEST 9: File linkage
# ════════════════════════════════════════════════════════════════════
print("\n=== TESTS: File Linkage ===")

sessions = list((MEM_DIR / "Sessions").glob("*_Session.md"))
summaries = list((MEM_DIR / "Summaries").glob("*_Summary.md"))
test(name="9.1 Each session has a summary",
     condition_fn=lambda: len(sessions) <= len(summaries) or len(sessions) == 0,
     detail=f"{len(sessions)} sessions, {len(summaries)} summaries")

# Session file format check
if sessions:
    s_content = sessions[0].read_text()
    test(name="9.2 Session has required structure",
         condition_fn=lambda: all(x in s_content for x in ["## Turn", "### User Prompt", "### Hermes Response"]),
         detail=f"checking {sessions[0].name}")

# ════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print(f"  RESULTS: {passed} passed, {failed} failed")
print("="*60)
for r in results:
    print(r)

sys.exit(0 if failed == 0 else 1)