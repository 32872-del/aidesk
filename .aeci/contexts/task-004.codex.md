# Context Pack: task-004

## Task

Document Manual Worktree Workflow

## Project Summary

# Project Blueprint

## Goal

Build a local-first Agent Workspace for a personal developer. The workspace coordinates multiple AI coding tools around shared tasks, context, permissions, sandboxes, artifacts, reviews, logs, and lessons.

## Current Phase

Phase A: manual workflow validation.

We are not building a full autonomous AI company, enterprise platform, or protocol layer yet. First, prove the workflow is useful in one real repository.

## Core Principles

- Deterministic files are the source of truth.
- Supervisor AI advises, summarizes, and prepares work, but does not silently own project state.
- Each task should have a Task Card and, when needed, a Context Pack.
- Execution Agents should work in a sandbox or Git worktree.
- Artifacts must be reviewed before merge.
- Lessons are proposed first; stable lessons require human confirmation.

## Initial Modules

- Task Card storage in `.aeci/tasks/`.
- Context Pack storage in `.aeci/contexts/`.
- Agent Profiles in `.aeci/agents/`.
- Event log in `.aeci/events.jsonl`.
- Reviews in `.aeci/reviews/`.
- Episodes in `.aeci/episodes/`.
- Artifact storage in `.aeci/artifacts/`.

## Not Doing Yet

- Automatic dispatch to external Agent products.
- Automatic merge of patches.
- MCP server implementation.
- Web UI.
- Team or enterprise features.
- Long-term protocol standardization.

## Risks

- Task cards become too heavy and sl...

## Task Objective

Write the first manual sandbox/worktree workflow so execution Agents can work outside the main workspace.

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

## Applicable Lessons

- None yet.

## Submission Instructions

Work only inside the allowed scope. Submit changed files, test output, notes, and any risk. Do not merge directly.
