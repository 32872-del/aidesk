# Episode: task-002

## Summary

Added a minimal local CLI and short-term planning files so the workspace can create task cards, generate Context Packs, and record events.

## What Changed

- Added `aeci.py`.
- Added `pyproject.toml`.
- Added task and context templates.
- Added unit tests for task creation, context generation, and status reporting.
- Added `.aeci/roadmap.md`.
- Added `task-003` for guard checks.
- Added `task-004` for manual worktree documentation.

## Outcome

The project now has a tiny executable core. It is still file-first and manual, but future tasks no longer need to start from a blank document.

## Lesson Candidate

Keep the first CLI narrow: task creation, context generation, and events are enough to reduce immediate manual repetition without committing to a platform architecture.

## Next Step

Implement `task-003`: a basic guard command that compares changed files with a task card's allowed and forbidden file scopes.
