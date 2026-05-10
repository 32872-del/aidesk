# aidesk

A personal workspace for multi-AI development. It does not write code for you; it keeps your agents from stepping on each other's toes by sharing tasks, memory, and guardrails across sessions.

个人开发者多 AI 协作工作区实验。

这个仓库当前目标不是先做完整平台，而是把蓝图里的核心工作流跑起来：

1. 用 Task Card 描述任务目标、边界和验收标准。
2. 用 Context Pack 给执行 Agent 提供刚好够用的上下文。
3. 用 Git worktree 作为任务沙箱，避免多个 Agent 直接污染主目录。
4. 用 Artifact、Review、Episode 记录产物、验收和复盘。
5. 让 Supervisor 只基于仓库状态给建议，而不是依赖聊天记忆。

## 当前阶段

阶段 A：手工工作流。

今天先完成：

- 初始化 Git 仓库。
- 创建 `.aeci/` 工作区骨架。
- 准备第一张任务卡和第一份 Context Pack。
- 手动跑通一次“任务卡 -> Context Pack -> Agent -> artifact -> review -> episode”的闭环。

## 目录

```text
.aeci/
  blueprint.md
  config.toml
  events.jsonl
  tasks/
  contexts/
  agents/
  lessons/
  episodes/
  artifacts/
  reviews/
  sandboxes/
  exports/
```

根目录里的 `Agent工作区_个人开发者蓝图.md` 是完整蓝图原文，`.aeci/blueprint.md` 是给日常 Agent 工作使用的短版稳定蓝图。

## CLI

当前只有一个最小标准库 CLI：

```powershell
python aeci.py status
python aeci.py task new "Write next task" --objective "Capture the next bounded task."
python aeci.py context task-002
```

测试命令：

```powershell
python -m unittest discover -s tests
```

## 下一步

短期路线写在 `.aeci/roadmap.md`。当前建议先做：

1. `task-002`：最小 CLI。
2. `task-003`：基础 guard 检查。
3. `task-004`：手工 worktree 沙箱流程。
