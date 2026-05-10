# AECI Roadmap

## Today

Goal: make the project usable as a basic local Agent Workspace.

1. Link local Git repo to GitHub.
2. Keep the original blueprint as source material.
3. Maintain a short stable project blueprint in `.aeci/blueprint.md`.
4. Provide a minimal `aeci.py` CLI:
   - `status`
   - `task new`
   - `context`
5. Keep task cards, context packs, agent profiles, reviews, episodes, and events in plain files.
6. Capture the next several tasks so another Agent can pick them up.

## This Week

1. Use the CLI for every new task instead of hand-writing files from scratch.
2. Run at least one real task through:
   Task Card -> Context Pack -> Agent -> artifact -> review -> episode.
3. Add a basic guard command that checks changed files against allowed/forbidden scopes.
4. Add a worktree helper only after the manual sandbox workflow is clear.

## Manual Sandbox Workflow

Use Git worktree as the first execution sandbox. Automation can come later; for now the goal is a repeatable manual loop.

1. Pick a Task Card, for example `.aeci/tasks/task-004.md`.
2. Generate or refresh a Context Pack:
   `python aeci.py context task-004`.
3. Create a short branch and worktree:
   `git worktree add .aeci/sandboxes/task-004 -b work/task-004 main`.
4. Open the sandbox path in the target Agent.
5. Give the Agent the Context Pack and tell it to stay inside the Task Card scope.
6. In the sandbox, run the relevant checks.
7. In the sandbox, collect the patch:
   `git diff -- . > ../artifacts/task-004.diff`.
8. Back in the main workspace, inspect changed files and run:
   `python aeci.py guard task-004`.
9. Write Review and Episode files.
10. When finished, remove the worktree:
    `git worktree remove .aeci/sandboxes/task-004`.

On Windows, keep sandbox paths short and close editors or terminals inside the worktree before cleanup. File locks can prevent `git worktree remove` from finishing.

## Not This Week

- Web UI.
- MCP server.
- Automatic Agent dispatch.
- Automatic merge.
- Database-backed state projection.
- Multi-user/team features.

## Working Rule

Every new automation must remove a real repeated manual step. If it does not make the next task easier, keep it as documentation.
