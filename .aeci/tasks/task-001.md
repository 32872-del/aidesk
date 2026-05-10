# task-001: Bootstrap Manual Agent Workflow

## Objective

Create the first usable repository structure for the Agent Workspace and prepare one manual workflow loop.

## Background

The source blueprint recommends starting with a manual process before building automation. The first useful artifact should make future Agent work less chaotic: a short blueprint, task card, context pack, agent profiles, and review/episode locations.

## Type

documentation / workflow

## Risk

low

## Allowed Files

- `README.md`
- `.gitignore`
- `.gitattributes`
- `.editorconfig`
- `.aeci/**`

## Forbidden Files

- `.git/**`
- `Agent工作区_个人开发者蓝图.md`
- `Agent工作区_个人开发者蓝图.txt`

## Acceptance Criteria

- Git repository is initialized on `main`.
- `.aeci/` contains the baseline directories from the blueprint.
- A short stable `.aeci/blueprint.md` exists.
- At least one Agent Profile exists.
- At least one Context Pack exists for this task.
- `events.jsonl` records initialization.
- The next task is clear enough to hand to another Agent.

## Recommended Agent

doc-maintainer

## Recommended Checks

- `git status --short --branch`
- `rg --files`
