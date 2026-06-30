# Changelog — Hermes Obsidian Memory Skill

## v1.0.0 (2026-06-30)

- Initial release.
- Append-only daily session logging (manual + plugin hook auto-capture).
- Nightly compressed summaries with task cross-checking against Todo Index.
- Context recovery — plugin injects last 3 summaries into new sessions.
- TDD-tested: every component has a .TEST.md spec, 42 tests pass.
- Built with Test-Driven Development: `.TEST.md` specs written first, implementation second, all 42 tests passing before release.
- Plugin hooks for automatic capture (pre_llm_call + post_llm_call).
- Hermes cron integration for nightly summarization.
- Templates, scripts, and full documentation included.
