# task-003: Add Basic Guard Command

## Objective

Add a CLI command that checks changed files against a task card's allowed and forbidden file scopes.

## Background

The blueprint treats guard checks as a core deterministic safety layer. Before adding automated dispatch or MCP, the local workspace needs a simple way to spot out-of-scope changes.

## Type

implementation

## Risk

medium

## Allowed Files

- `aeci.py`
- `tests/**`
- `.aeci/tasks/task-003.md`
- `.aeci/events.jsonl`
- `README.md`

## Forbidden Files

- `.git/**`
- `Agent工作区_个人开发者蓝图.md`
- `Agent工作区_个人开发者蓝图.txt`

## Acceptance Criteria

- `python aeci.py guard task-XXX` reports changed files.
- The command flags files matching `Forbidden Files`.
- The command flags files outside `Allowed Files` when allowed files are specified.
- The command appends a `guard_ran` event.
- Tests cover allowed, forbidden, and out-of-scope cases.

## Recommended Agent

backend-worker

## Recommended Checks

- `python -m unittest discover -s tests`
- `python aeci.py guard task-003`
