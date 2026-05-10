#!/usr/bin/env python
"""Small local CLI for the Agent Workspace.

The first version intentionally uses only the Python standard library and
human-readable files. It is a workflow helper, not the future protocol layer.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
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


@dataclass(frozen=True)
class GuardResult:
    task_id: str
    changed_files: List[str]
    allowed_patterns: List[str]
    forbidden_patterns: List[str]
    forbidden_violations: List[str]
    out_of_scope_files: List[str]

    @property
    def passed(self) -> bool:
        return not self.forbidden_violations and not self.out_of_scope_files


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


def section_bullets(content: str, heading: str) -> List[str]:
    section = extract_section(content, heading, "")
    items: List[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        item = line[2:].strip()
        if item.startswith("`") and item.endswith("`") and len(item) >= 2:
            item = item[1:-1]
        item = item.strip()
        if item and item.upper() != "TBD":
            items.append(normalize_path_text(item))
    return items


def normalize_path_text(value: str) -> str:
    return value.replace("\\", "/").strip("/")


def matches_pattern(path: str, pattern: str) -> bool:
    clean_path = normalize_path_text(path)
    clean_pattern = normalize_path_text(pattern)
    if not clean_pattern:
        return False
    if clean_pattern.endswith("/**"):
        prefix = clean_pattern[:-3]
        return clean_path == prefix or clean_path.startswith(prefix + "/")
    return fnmatch.fnmatchcase(clean_path, clean_pattern)


def any_pattern_matches(path: str, patterns: Iterable[str]) -> bool:
    return any(matches_pattern(path, pattern) for pattern in patterns)


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


def git_changed_files(root: Path) -> List[str]:
    tracked = git_lines(root, ["diff", "--name-only", "HEAD", "--"])
    untracked = git_lines(root, ["ls-files", "--others", "--exclude-standard"])
    return sorted({normalize_path_text(path) for path in tracked + untracked if path.strip()})


def git_lines(root: Path, args: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise WorkspaceError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def evaluate_guard(
    task_id: str,
    changed_files: Iterable[str],
    allowed_patterns: Iterable[str],
    forbidden_patterns: Iterable[str],
) -> GuardResult:
    changed = sorted({normalize_path_text(path) for path in changed_files if path.strip()})
    allowed = [normalize_path_text(pattern) for pattern in allowed_patterns if pattern.strip()]
    forbidden = [normalize_path_text(pattern) for pattern in forbidden_patterns if pattern.strip()]
    forbidden_violations = [path for path in changed if any_pattern_matches(path, forbidden)]
    out_of_scope = [
        path
        for path in changed
        if allowed and not any_pattern_matches(path, allowed)
    ]
    return GuardResult(
        task_id=task_id,
        changed_files=changed,
        allowed_patterns=allowed,
        forbidden_patterns=forbidden,
        forbidden_violations=forbidden_violations,
        out_of_scope_files=out_of_scope,
    )


def guard_task(root: Path, task_id: str, changed_files: Optional[Iterable[str]] = None) -> GuardResult:
    require_workspace(root)
    task_path = aeci_dir(root) / "tasks" / f"{task_id}.md"
    if not task_path.exists():
        raise WorkspaceError(f"Task card not found: {task_path}")

    task_content = read_text(task_path)
    changed = list(changed_files) if changed_files is not None else git_changed_files(root)
    result = evaluate_guard(
        task_id=task_id,
        changed_files=changed,
        allowed_patterns=section_bullets(task_content, "Allowed Files"),
        forbidden_patterns=section_bullets(task_content, "Forbidden Files"),
    )
    append_event(
        root,
        "guard_ran",
        task_id=task_id,
        passed=result.passed,
        changed_files=result.changed_files,
        forbidden_violations=result.forbidden_violations,
        out_of_scope_files=result.out_of_scope_files,
    )
    return result


def guard_output(result: GuardResult) -> str:
    lines = [
        f"Guard: {result.task_id}",
        f"Result: {'pass' if result.passed else 'fail'}",
        f"Changed files: {len(result.changed_files)}",
    ]
    lines.extend(f"- {path}" for path in result.changed_files)
    if result.forbidden_violations:
        lines.append("Forbidden violations:")
        lines.extend(f"- {path}" for path in result.forbidden_violations)
    if result.out_of_scope_files:
        lines.append("Out-of-scope files:")
        lines.extend(f"- {path}" for path in result.out_of_scope_files)
    return "\n".join(lines)


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

    guard_parser = subparsers.add_parser("guard", help="check changed files against a task card")
    guard_parser.add_argument("task_id", help="task id, for example task-003")

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

        if args.command == "guard":
            result = guard_task(root, args.task_id)
            print(guard_output(result))
            return 0 if result.passed else 1

    except WorkspaceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(run())
