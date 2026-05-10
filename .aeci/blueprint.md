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

- Task cards become too heavy and slow down work.
- Context packs become too long and recreate the original context problem.
- Supervisor gives generic advice without citing repository evidence.
- Agent patches exceed authorized file scope.

## Next Milestone

Complete one full manual task loop:

Task Card -> Context Pack -> sandbox/worktree -> artifact -> review -> episode.
