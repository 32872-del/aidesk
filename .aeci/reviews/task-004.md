# Review: task-004

## Result

pass

## Evidence

- README documents the manual worktree sandbox flow.
- `.aeci/roadmap.md` includes create, dispatch, collect diff, review, and cleanup steps.
- Windows path and file-lock considerations are documented.
- `.aeci/contexts/task-004.codex.md` already exists.
- `python aeci.py guard task-004` passed for this change set.

## Risks

- The artifact path in the manual diff command depends on the current sandbox depth.
- Worktree creation and cleanup are still manual.
- No command yet persists guard output as a standalone artifact.

## Human Decision Needed

Use this manual workflow once on the next real implementation task before automating worktree creation.
