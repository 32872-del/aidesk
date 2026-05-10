# task-002: Build Minimal AECI CLI

## Objective

Create a tiny local CLI that can create task cards, generate a starter Context Pack, and append events to `.aeci/events.jsonl`.

## Background

The blueprint says Week 2 should stabilize task cards and event logging, while Week 3 should generate Context Packs. A small CLI can reduce copying without committing to a full platform.

## Type

implementation

## Risk

medium

## Allowed Files

- `aeci.py`
- `pyproject.toml`
- `tests/**`
- `.aeci/templates/**`
- `.aeci/events.jsonl`

## Forbidden Files

- `.git/**`
- `Agent工作区_个人开发者蓝图.md`
- `Agent工作区_个人开发者蓝图.txt`

## Acceptance Criteria

- `python aeci.py task new "..."` creates a new task file.
- `python aeci.py context task-XXX` creates a starter Context Pack.
- Each command appends a JSONL event.
- The CLI uses only the Python standard library unless a dependency is explicitly justified.
- Basic tests or smoke checks are documented.

## Recommended Agent

backend-worker

## Recommended Checks

- `python aeci.py --help`
- `python aeci.py status`
