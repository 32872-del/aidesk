# Review: task-003

## Result

pass

## Evidence

- `aeci.py` now has a `guard` command.
- `guard_task` reads `Allowed Files` and `Forbidden Files` from a Task Card.
- `evaluate_guard` flags forbidden and out-of-scope files deterministically.
- `python -m unittest discover -s tests` passed.
- `python aeci.py guard task-003` passed for the current change set.

## Risks

- Pattern matching is intentionally simple and only supports the current Markdown task-card style.
- The command checks the current Git working tree, not an external artifact file yet.
- Guard reports are printed to stdout and events; they are not yet saved as standalone review artifacts automatically.

## Human Decision Needed

Use this guard on every future task before review. The next implementation step can either persist guard reports or add worktree helpers.
