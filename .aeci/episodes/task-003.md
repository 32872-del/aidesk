# Episode: task-003

## Summary

Added a deterministic guard command that compares current Git changes with a task card's allowed and forbidden file scopes.

## What Changed

- Added `GuardResult` and pure guard evaluation helpers.
- Added Git working-tree changed-file collection.
- Added `python aeci.py guard task-XXX`.
- Added unit tests for allowed, forbidden, and out-of-scope files.
- Added README usage for the guard command.

## Outcome

The workspace can now run a basic scope check before reviewing an Agent's changes.

## Lesson Candidate

Guard logic should stay deterministic and testable. Keep pattern matching simple until real task history shows where richer rules are needed.

## Next Step

Run `task-004`: document the manual worktree flow so future Agent work can happen outside the main checkout.
