import json
import tempfile
import unittest
from pathlib import Path

import aeci


class AeciCliTests(unittest.TestCase):
    def make_workspace(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".aeci" / "tasks").mkdir(parents=True)
        (root / ".aeci" / "contexts").mkdir()
        (root / ".aeci" / "agents").mkdir()
        (root / ".aeci" / "templates").mkdir()
        (root / ".aeci" / "config.toml").write_text(
            '[workspace]\nname = "test-workspace"\nphase = "manual-workflow"\n',
            encoding="utf-8",
        )
        (root / ".aeci" / "blueprint.md").write_text("# Blueprint\n\nKeep it small.\n", encoding="utf-8")
        (root / ".aeci" / "events.jsonl").write_text("", encoding="utf-8")
        return temp, root

    def test_create_task_appends_event(self):
        temp, root = self.make_workspace()
        with temp:
            record = aeci.create_task(
                root=root,
                title="Plan next task",
                objective="Create a useful task card.",
                background=None,
                task_type="planning",
                risk="low",
                allowed_files=[".aeci/tasks/**"],
                forbidden_files=[".git/**"],
                acceptance_criteria=["Task card exists."],
                recommended_agent="doc-maintainer",
                recommended_checks=["python aeci.py status"],
            )

            self.assertEqual(record.task_id, "task-001")
            self.assertTrue(record.path.exists())
            events = [json.loads(line) for line in (root / ".aeci" / "events.jsonl").read_text().splitlines()]
            self.assertEqual(events[0]["type"], "task_created")
            self.assertEqual(events[0]["task_id"], "task-001")

    def test_create_context_from_task_card(self):
        temp, root = self.make_workspace()
        with temp:
            aeci.create_task(
                root=root,
                title="Build CLI",
                objective="Create starter CLI.",
                background=None,
                task_type="implementation",
                risk="medium",
                allowed_files=["aeci.py"],
                forbidden_files=[".git/**"],
                acceptance_criteria=["Status command works."],
                recommended_agent="backend-worker",
                recommended_checks=["python aeci.py status"],
            )

            context_path = aeci.create_context(root, "task-001", "codex")
            content = context_path.read_text(encoding="utf-8")

            self.assertIn("# Context Pack: task-001", content)
            self.assertIn("Create starter CLI.", content)
            self.assertIn("- aeci.py", content)
            self.assertIn("backend-worker", content)

    def test_status_counts_workspace_files(self):
        temp, root = self.make_workspace()
        with temp:
            aeci.create_task(
                root=root,
                title="Build CLI",
                objective=None,
                background=None,
                task_type="implementation",
                risk="medium",
                allowed_files=[],
                forbidden_files=[],
                acceptance_criteria=[],
                recommended_agent="backend-worker",
                recommended_checks=[],
            )

            lines = aeci.status_lines(root)

            self.assertIn("Workspace: test-workspace", lines)
            self.assertIn("Phase: manual-workflow", lines)
            self.assertIn("Tasks: 1", lines)

    def test_guard_passes_allowed_files(self):
        temp, root = self.make_workspace()
        with temp:
            aeci.create_task(
                root=root,
                title="Guard task",
                objective="Check allowed files.",
                background=None,
                task_type="implementation",
                risk="medium",
                allowed_files=["src/**", "tests/**"],
                forbidden_files=[".git/**"],
                acceptance_criteria=["Guard passes."],
                recommended_agent="backend-worker",
                recommended_checks=[],
            )

            result = aeci.guard_task(root, "task-001", changed_files=["src/app.py", "tests/test_app.py"])

            self.assertTrue(result.passed)
            self.assertEqual(result.forbidden_violations, [])
            self.assertEqual(result.out_of_scope_files, [])
            events = [json.loads(line) for line in (root / ".aeci" / "events.jsonl").read_text().splitlines()]
            self.assertEqual(events[-1]["type"], "guard_ran")
            self.assertTrue(events[-1]["passed"])

    def test_guard_flags_forbidden_files(self):
        temp, root = self.make_workspace()
        with temp:
            aeci.create_task(
                root=root,
                title="Guard task",
                objective="Check forbidden files.",
                background=None,
                task_type="implementation",
                risk="medium",
                allowed_files=["src/**", "Agent工作区_个人开发者蓝图.md"],
                forbidden_files=["Agent工作区_个人开发者蓝图.md"],
                acceptance_criteria=["Guard fails."],
                recommended_agent="backend-worker",
                recommended_checks=[],
            )

            result = aeci.guard_task(root, "task-001", changed_files=["Agent工作区_个人开发者蓝图.md"])

            self.assertFalse(result.passed)
            self.assertEqual(result.forbidden_violations, ["Agent工作区_个人开发者蓝图.md"])
            self.assertEqual(result.out_of_scope_files, [])

    def test_guard_flags_out_of_scope_files(self):
        temp, root = self.make_workspace()
        with temp:
            aeci.create_task(
                root=root,
                title="Guard task",
                objective="Check scope.",
                background=None,
                task_type="implementation",
                risk="medium",
                allowed_files=["src/**"],
                forbidden_files=[".git/**"],
                acceptance_criteria=["Guard fails."],
                recommended_agent="backend-worker",
                recommended_checks=[],
            )

            result = aeci.guard_task(root, "task-001", changed_files=["README.md", "src/app.py"])

            self.assertFalse(result.passed)
            self.assertEqual(result.forbidden_violations, [])
            self.assertEqual(result.out_of_scope_files, ["README.md"])


if __name__ == "__main__":
    unittest.main()
