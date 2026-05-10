#!/usr/bin/env python
"""Small local CLI for the Agent Workspace.

The first version intentionally uses only the Python standard library and
human-readable files. It is a workflow helper, not the future protocol layer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional


TASK_RE = re.compile(r"^task-(\d{3,})\.md$")


TASK_TEMPLATE = """# {{task_id}}: {{title}}

## Objective

{{objective}}

## Background

{{background}}

## Type

{{task_type}}

## Risk

{{risk}}

## Allowed Files

{{allowed_files}}

## Forbidden Files

{{forbidden_files}}

## Acceptance Criteria

{{acceptance_criteria}}

## Recommended Agent

{{recommended_agent}}

## Recommended Checks

{{recommended_checks}}
"""


CONTEXT_TEMPLATE = """# Context Pack: {{task_id}}

## Task

{{task_title}}

## Project Summary

{{blueprint_summary}}

## Task Objective

{{objective}}

## Allowed Files

{{allowed_files}}

## Forbidden Files

{{forbidden_files}}

## Acceptance Criteria

{{acceptance_criteria}}

## Recommended Agent

{{recommended_agent}}

## Applicable Lessons

- None yet.

## Submission Instructions

Work only inside the allowed scope. Submit changed files, test output, notes, and any risk. Do not merge directly.
"""


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    title: str
    path: Path


class WorkspaceError(RuntimeError):
    pass


def aeci_dir(root: Path) -> Path:
    return root / ".aeci"


def require_workspace(root: Path) -> None:
    if not aeci_dir(root).is_dir():
        raise WorkspaceError(f"Missing workspace directory: {aeci_dir(root)}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def load_template(root: Path, name: str, fallback: str) -> str:
    template_path = aeci_dir(root) / "templates" / name
    if template_path.exists():
        return read_text(template_path)
    return fallback


def render_template(template: str, values: Dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def format_bullets(items: Iterable[str], default: str = "TBD") -> str:
    clean_items = [item.strip() for item in items if item and item.strip()]
    if not clean_items:
        clean_items = [default]
    return "\n".join(f"- {item}" for item in clean_items)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def append_event(root: Path, event_type: str, **fields: object) -> None:
    event = {
        "ts": now_iso(),
        "type": event_type,
        "actor": "aeci-cli",
        **fields,
    }
    events_path = aeci_dir(root) / "events.jsonl"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    with events_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")


def relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def task_records(root: Path) -> List[TaskRecord]:
    tasks_dir = aeci_dir(root) / "tasks"
    if not tasks_dir.exists():
        return []

    records: List[TaskRecord] = []
    for path in tasks_dir.glob("task-*.md"):
        match = TASK_RE.match(path.name)
        if not match:
            continue
        title = read_task_title(path)
        records.append(TaskRecord(task_id=path.stem, title=title, path=path))
    return sorted(records, key=lambda record: record.task_id)


def read_task_title(path: Path) -> str:
    for line in read_text(path).splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            task_match = re.match(r"task-\d{3,}: ", title)
            if task_match:
                return title[task_match.end() :]
            prefix = f"{path.stem}: "
            if title.startswith(prefix):
                return title[len(prefix) :]
            return title
    return path.stem


def next_task_id(root: Path) -> str:
    max_number = 0
    for record in task_records(root):
        match = re.match(r"task-(\d+)$", record.task_id)
        if match:
            max_number = max(max_number, int(match.group(1)))
    return f"task-{max_number + 1:03d}"


def extract_section(content: str, heading: str, default: str = "TBD") -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*\n(?P<body>.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        return default
    body = match.group("body").strip()
    return body or default


def summarize_blueprint(root: Path, max_chars: int = 1400) -> str:
    path = aeci_dir(root) / "blueprint.md"
    if not path.exists():
        return "No project blueprint found."

    content = read_text(path).strip()
    if len(content) <= max_chars:
        return content
    return content[: max_chars - 3].rstrip() + "..."


def create_task(
    root: Path,
    title: str,
    objective: Optional[str],
    background: Optional[str],
    task_type: str,
    risk: str,
    allowed_files: Iterable[str],
    forbidden_files: Iterable[str],
    acceptance_criteria: Iterable[str],
    recommended_agent: str,
    recommended_checks: Iterable[str],
) -> TaskRecord:
    require_workspace(root)
    task_id = next_task_id(root)
    task_path = aeci_dir(root) / "tasks" / f"{task_id}.md"
    if task_path.exists():
        raise WorkspaceError(f"Task already exists: {task_path}")

    values = {
        "task_id": task_id,
        "title": title,
        "objective": objective or "TBD",
        "background": background or "Created by `aeci.py task new`; fill this before dispatch.",
        "task_type": task_type,
        "risk": risk,
        "allowed_files": format_bullets(allowed_files),
        "forbidden_files": format_bullets(forbidden_files, ".git/**"),
        "acceptance_criteria": format_bullets(acceptance_criteria),
        "recommended_agent": recommended_agent,
        "recommended_checks": format_bullets(recommended_checks, "python aeci.py status"),
    }
    content = render_template(load_template(root, "task.md", TASK_TEMPLATE), values)
    write_text(task_path, content)
    append_event(
        root,
        "task_created",
        task_id=task_id,
        title=title,
        path=relative_posix(task_path, root),
    )
    return TaskRecord(task_id=task_id, title=title, path=task_path)


def create_context(root: Path, task_id: str, agent: str = "codex") -> Path:
    require_workspace(root)
    task_path = aeci_dir(root) / "tasks" / f"{task_id}.md"
    if not task_path.exists():
        raise WorkspaceError(f"Task card not found: {task_path}")

    task_content = read_text(task_path)
    task_title = read_task_title(task_path)
    context_path = aeci_dir(root) / "contexts" / f"{task_id}.{agent}.md"
    values = {
        "task_id": task_id,
        "task_title": task_title,
        "blueprint_summary": summarize_blueprint(root),
        "objective": extract_section(task_content, "Objective"),
        "allowed_files": extract_section(task_content, "Allowed Files"),
        "forbidden_files": extract_section(task_content, "Forbidden Files"),
        "acceptance_criteria": extract_section(task_content, "Acceptance Criteria"),
        "recommended_agent": extract_section(task_content, "Recommended Agent"),
    }
    content = render_template(load_template(root, "context.md", CONTEXT_TEMPLATE), values)
    write_text(context_path, content)
    append_event(
        root,
        "context_generated",
        task_id=task_id,
        agent=agent,
        path=relative_posix(context_path, root),
    )
    return context_path


def load_simple_config(root: Path) -> Dict[str, str]:
    path = aeci_dir(root) / "config.toml"
    if not path.exists():
        return {}

    result: Dict[str, str] = {}
    section = ""
    for raw_line in read_text(path).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line.strip("[]")
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"')
        result[f"{section}.{key}" if section else key] = value
    return result


def event_count(root: Path) -> int:
    path = aeci_dir(root) / "events.jsonl"
    if not path.exists():
        return 0
    return sum(1 for line in read_text(path).splitlines() if line.strip())


def status_lines(root: Path) -> List[str]:
    require_workspace(root)
    config = load_simple_config(root)
    tasks = task_records(root)
    contexts = list((aeci_dir(root) / "contexts").glob("*.md"))
    agents = list((aeci_dir(root) / "agents").glob("*.md"))

    lines = [
        f"Workspace: {config.get('workspace.name', root.name)}",
        f"Phase: {config.get('workspace.phase', 'unknown')}",
        f"Tasks: {len(tasks)}",
        f"Contexts: {len(contexts)}",
        f"Agents: {len(agents)}",
        f"Events: {event_count(root)}",
    ]
    if tasks:
        latest = tasks[-1]
        lines.append(f"Latest task: {latest.task_id} - {latest.title}")
    return lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aeci", description="Local Agent Workspace helper")
    parser.add_argument("--root", default=".", help="workspace root, defaults to current directory")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="show workspace summary")

    task_parser = subparsers.add_parser("task", help="task operations")
    task_subparsers = task_parser.add_subparsers(dest="task_command", required=True)
    task_new = task_subparsers.add_parser("new", help="create a task card")
    task_new.add_argument("title", help="task title")
    task_new.add_argument("--objective")
    task_new.add_argument("--background")
    task_new.add_argument("--type", default="planning", dest="task_type")
    task_new.add_argument("--risk", default="low")
    task_new.add_argument("--agent", default="doc-maintainer", dest="recommended_agent")
    task_new.add_argument("--allowed", action="append", default=[], dest="allowed_files")
    task_new.add_argument("--forbidden", action="append", default=[], dest="forbidden_files")
    task_new.add_argument("--acceptance", action="append", default=[], dest="acceptance_criteria")
    task_new.add_argument("--check", action="append", default=[], dest="recommended_checks")

    context_parser = subparsers.add_parser("context", help="create a Context Pack")
    context_parser.add_argument("task_id", help="task id, for example task-002")
    context_parser.add_argument("--agent", default="codex", help="target agent format suffix")

    return parser


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    try:
        if args.command == "status":
            print("\n".join(status_lines(root)))
            return 0

        if args.command == "task" and args.task_command == "new":
            record = create_task(
                root=root,
                title=args.title,
                objective=args.objective,
                background=args.background,
                task_type=args.task_type,
                risk=args.risk,
                allowed_files=args.allowed_files,
                forbidden_files=args.forbidden_files,
                acceptance_criteria=args.acceptance_criteria,
                recommended_agent=args.recommended_agent,
                recommended_checks=args.recommended_checks,
            )
            print(f"Created {record.task_id}: {record.path.relative_to(root)}")
            return 0

        if args.command == "context":
            path = create_context(root, args.task_id, args.agent)
            print(f"Created context: {path.relative_to(root)}")
            return 0

    except WorkspaceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(run())
