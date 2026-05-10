# task-004: Document Manual Worktree Workflow

## Objective

Write the first manual sandbox/worktree workflow so execution Agents can work outside the main workspace.

## Background

The blueprint recommends Git worktree as the default sandbox boundary. Before automating worktree creation, the project should document the exact manual commands and cleanup steps that work on Windows.

## Type

documentation

## Risk

low

## Allowed Files

- `README.md`
- `.aeci/roadmap.md`
- `.aeci/tasks/task-004.md`
- `.aeci/contexts/**`
- `.aeci/reviews/task-004.md`
- `.aeci/episodes/task-004.md`
- `.aeci/events.jsonl`

## Forbidden Files

- `.git/**`
- `Agent工作区_个人开发者蓝图.md`
- `Agent工作区_个人开发者蓝图.txt`

## Acceptance Criteria

- README contains a short manual worktree workflow.
- The workflow includes create, dispatch, collect diff, review, and cleanup steps.
- Windows path considerations are noted.
- A Context Pack exists for this task.

## Recommended Agent

doc-maintainer

## Recommended Checks

- `python aeci.py status`
- `python aeci.py guard task-004`
- `git status --short --branch`
