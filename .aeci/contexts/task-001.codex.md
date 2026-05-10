# Context Pack: task-001

## Task

Bootstrap the repository and create the first manual Agent Workspace structure.

## Project Summary

This project is a local-first coordination layer for personal developers using multiple AI coding tools. It should manage task cards, context packs, agent profiles, event logs, sandboxes, artifacts, reviews, and lessons. The first phase is deliberately manual.

## Relevant Blueprint Points

- Start with manual workflow before protocol or automation.
- Store state in local deterministic files.
- Use Task Card and Context Pack as first stable objects.
- Use sandbox/worktree for execution.
- Keep Supervisor as advisor and reviewer, not an unchecked decision maker.

## Allowed Changes

- Repository metadata and documentation.
- `.aeci/` workspace skeleton.
- Task/context/profile templates and starter files.

## Forbidden Changes

- Do not rewrite the original long blueprint files.
- Do not add a web UI, MCP server, or large framework yet.

## Acceptance Criteria

- Repository has Git initialized on `main`.
- `.aeci/` has the first practical structure.
- README explains what this repo is and what today's first milestone is.
- The next implementation task is captured as a Task Card.

## Submission Instructions

Return a summary of changed files, the current Git status, and any remaining setup gap. Do not merge external patches automatically.
