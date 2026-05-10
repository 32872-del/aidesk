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

## Not This Week

- Web UI.
- MCP server.
- Automatic Agent dispatch.
- Automatic merge.
- Database-backed state projection.
- Multi-user/team features.

## Working Rule

Every new automation must remove a real repeated manual step. If it does not make the next task easier, keep it as documentation.
