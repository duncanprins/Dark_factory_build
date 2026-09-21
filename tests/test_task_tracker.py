import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))
import task_tracker


class TestTaskTracker(unittest.TestCase):
    def setUp(self):
        task_tracker.TASKS_FILE = Path("/tmp/test_tasks.json")
        if task_tracker.TASKS_FILE.exists():
            task_tracker.TASKS_FILE.unlink()
        if task_tracker.tasks_log_file().exists():
            task_tracker.tasks_log_file().unlink()

    def tearDown(self):
        if task_tracker.TASKS_FILE.exists():
            task_tracker.TASKS_FILE.unlink()
        if task_tracker.tasks_log_file().exists():
            task_tracker.tasks_log_file().unlink()

    def test_add_task(self):
        task_tracker.cmd_add("Do something")
        tasks = task_tracker.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Do something")
        self.assertEqual(tasks[0]["status"], "open")
        self.assertEqual(tasks[0]["id"], 1)
        self.assertEqual(tasks[0]["priority"], "medium")

    def test_add_multiple_tasks(self):
        task_tracker.cmd_add("First task")
        task_tracker.cmd_add("Second task")
        tasks = task_tracker.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[1]["id"], 2)

    def test_list_all(self):
        task_tracker.cmd_add("Task A")
        task_tracker.cmd_add("Task B")
        task_tracker.cmd_done(1)
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list()
        self.assertEqual(mock_print.call_count, 2)

    def test_list_by_status(self):
        task_tracker.cmd_add("Open task")
        task_tracker.cmd_add("Done task")
        task_tracker.cmd_done(2)
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list(status="open")
        self.assertEqual(mock_print.call_count, 1)

    def test_done(self):
        task_tracker.cmd_add("Complete me")
        task_tracker.cmd_done(1)
        tasks = task_tracker.load_tasks()
        self.assertEqual(tasks[0]["status"], "done")

    def test_done_nonexistent(self):
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_done(99)
        mock_print.assert_called_with("Task #99 not found.")

    def test_delete(self):
        task_tracker.cmd_add("Delete me")
        task_tracker.cmd_delete(1)
        tasks = task_tracker.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_nonexistent(self):
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_delete(99)
        mock_print.assert_called_with("Task #99 not found.")


    def test_add_task_with_priority(self):
        task_tracker.cmd_add("Urgent task", priority="high")
        tasks = task_tracker.load_tasks()
        self.assertEqual(tasks[0]["priority"], "high")

    def test_add_task_default_priority(self):
        task_tracker.cmd_add("Normal task")
        tasks = task_tracker.load_tasks()
        self.assertEqual(tasks[0]["priority"], "medium")

    def test_list_sorted_by_priority(self):
        task_tracker.cmd_add("Low task", priority="low")
        task_tracker.cmd_add("High task", priority="high")
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list(sort_priority=True)
        calls = [str(c) for c in mock_print.call_args_list]
        high_idx = next(i for i, c in enumerate(calls) if "High task" in c)
        low_idx = next(i for i, c in enumerate(calls) if "Low task" in c)
        self.assertLess(high_idx, low_idx)

    def test_list_shows_priority_tag(self):
        task_tracker.cmd_add("Tagged task", priority="high")
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list()
        output = mock_print.call_args_list[0][0][0]
        self.assertIn("[high]", output)

    def test_backward_compat_no_priority(self):
        tasks = [{"id": 1, "title": "Old task", "status": "open"}]
        task_tracker.save_tasks(tasks)
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list()
        output = mock_print.call_args_list[0][0][0]
        self.assertIn("[medium]", output)

    def test_add_task_with_due_date(self):
        task_tracker.cmd_add("Dated task", due_date="2026-05-01")
        tasks = task_tracker.load_tasks()
        self.assertEqual(tasks[0]["due_date"], "2026-05-01")

    def test_add_task_default_due_date(self):
        task_tracker.cmd_add("No date task")
        tasks = task_tracker.load_tasks()
        self.assertIsNone(tasks[0].get("due_date"))

    def test_list_shows_due_date(self):
        task_tracker.cmd_add("Dated task", due_date="2026-05-01")
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list()
        output = mock_print.call_args_list[0][0][0]
        self.assertIn("(due: 2026-05-01)", output)

    def test_list_no_due_date_omitted(self):
        task_tracker.cmd_add("Plain task")
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list()
        output = mock_print.call_args_list[0][0][0]
        self.assertNotIn("(due:", output)

    def test_list_sorted_by_due_date(self):
        task_tracker.cmd_add("Later task", due_date="2026-06-01")
        task_tracker.cmd_add("Earlier task", due_date="2026-04-25")
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list(sort_due=True)
        calls = [str(c) for c in mock_print.call_args_list]
        earlier_idx = next(i for i, c in enumerate(calls) if "Earlier task" in c)
        later_idx = next(i for i, c in enumerate(calls) if "Later task" in c)
        self.assertLess(earlier_idx, later_idx)

    def test_list_sort_due_date_none_last(self):
        task_tracker.cmd_add("No date task")
        task_tracker.cmd_add("Dated task", due_date="2026-04-25")
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list(sort_due=True)
        calls = [str(c) for c in mock_print.call_args_list]
        dated_idx = next(i for i, c in enumerate(calls) if "Dated task" in c)
        undated_idx = next(i for i, c in enumerate(calls) if "No date task" in c)
        self.assertLess(dated_idx, undated_idx)

    def test_add_invalid_due_date(self):
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_add("Bad date task", due_date="not-a-date")
        mock_print.assert_called_with("Invalid due-date format. Use YYYY-MM-DD.")
        tasks = task_tracker.load_tasks()
        self.assertEqual(len(tasks), 0)

    def test_backward_compat_no_due_date(self):
        tasks = [{"id": 1, "title": "Old task", "status": "open", "priority": "medium"}]
        task_tracker.save_tasks(tasks)
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list()
        output = mock_print.call_args_list[0][0][0]
        self.assertNotIn("(due:", output)

    def test_add_writes_jsonl_event_log(self):
        task_tracker.cmd_add("Logged task", priority="high")
        self.assertTrue(task_tracker.tasks_log_file().exists())
        lines = task_tracker.tasks_log_file().read_text().splitlines()
        self.assertEqual(len(lines), 1)
        event = json.loads(lines[0])
        self.assertEqual(event["op"], "add")
        self.assertEqual(event["task"]["title"], "Logged task")
        self.assertFalse(task_tracker.TASKS_FILE.exists())

    def test_load_replays_jsonl_events(self):
        events = [
            {"op": "add", "task": {"id": 1, "title": "Keep", "status": "open", "priority": "medium"}},
            {"op": "add", "task": {"id": 2, "title": "Remove", "status": "open", "priority": "medium"}},
            {"op": "done", "id": 1},
            {"op": "delete", "id": 2},
        ]
        task_tracker.tasks_log_file().write_text("\n".join(json.dumps(event) for event in events) + "\n")

        tasks = task_tracker.load_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Keep")
        self.assertEqual(tasks[0]["status"], "done")

    def test_legacy_json_migrates_before_append(self):
        task_tracker.TASKS_FILE.write_text(
            json.dumps([{"id": 1, "title": "Old task", "status": "open", "priority": "medium"}])
        )

        task_tracker.cmd_add("New task")
        tasks = task_tracker.load_tasks()
        events = [json.loads(line) for line in task_tracker.tasks_log_file().read_text().splitlines()]

        self.assertEqual([task["title"] for task in tasks], ["Old task", "New task"])
        self.assertEqual(tasks[1]["id"], 2)
        self.assertEqual(events[0]["op"], "snapshot")
        self.assertEqual(events[1]["op"], "add")

    def test_concurrent_adds_keep_all_tasks(self):
        script = Path(__file__).parent.parent / "task_tracker.py"
        with tempfile.TemporaryDirectory() as tmpdir:
            processes = [
                subprocess.Popen(
                    [sys.executable, str(script), "add", f"Task {idx}"],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for idx in range(8)
            ]
            results = [process.communicate(timeout=5) for process in processes]
            exit_codes = [process.returncode for process in processes]

            self.assertEqual(exit_codes, [0] * 8, results)
            events = [
                json.loads(line)
                for line in (Path(tmpdir) / "tasks.jsonl").read_text().splitlines()
                if line.strip()
            ]
            added_tasks = [event["task"] for event in events if event["op"] == "add"]

        self.assertEqual(len(added_tasks), 8)
        self.assertEqual(sorted(task["id"] for task in added_tasks), list(range(1, 9)))
        self.assertEqual(sorted(task["title"] for task in added_tasks), [f"Task {idx}" for idx in range(8)])


class TestPublish(unittest.TestCase):
    def setUp(self):
        task_tracker.TASKS_FILE = Path("/tmp/test_tasks.json")
        if task_tracker.TASKS_FILE.exists():
            task_tracker.TASKS_FILE.unlink()
        if task_tracker.tasks_log_file().exists():
            task_tracker.tasks_log_file().unlink()

    def tearDown(self):
        if task_tracker.TASKS_FILE.exists():
            task_tracker.TASKS_FILE.unlink()
        if task_tracker.tasks_log_file().exists():
            task_tracker.tasks_log_file().unlink()
        html_file = Path("tasks.html")
        if html_file.exists():
            html_file.unlink()

    def test_publish_creates_html_file(self):
        task_tracker.cmd_add("Test task", priority="high")
        task_tracker.cmd_publish()
        self.assertTrue(Path("tasks.html").exists())

    def test_publish_prints_count(self):
        task_tracker.cmd_add("Task one")
        task_tracker.cmd_add("Task two")
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_publish()
        mock_print.assert_called_with("Published 2 tasks to tasks.html")

    def test_publish_empty_tasks(self):
        task_tracker.cmd_publish()
        content = Path("tasks.html").read_text()
        self.assertIn("No open tasks.", content)
        self.assertIn("<!DOCTYPE html>", content)

    def test_publish_only_open_tasks(self):
        task_tracker.cmd_add("Open task")
        task_tracker.cmd_add("Done task")
        task_tracker.cmd_done(2)
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_publish()
        mock_print.assert_called_with("Published 1 task to tasks.html")
        content = Path("tasks.html").read_text()
        self.assertIn("Open task", content)
        self.assertNotIn("Done task", content)

    def test_publish_sorted_by_priority(self):
        task_tracker.cmd_add("Low task", priority="low")
        task_tracker.cmd_add("High task", priority="high")
        task_tracker.cmd_add("Medium task", priority="medium")
        task_tracker.cmd_publish()
        content = Path("tasks.html").read_text()
        high_pos = content.index("High task")
        medium_pos = content.index("Medium task")
        low_pos = content.index("Low task")
        self.assertLess(high_pos, medium_pos)
        self.assertLess(medium_pos, low_pos)

    def test_publish_includes_due_date(self):
        tasks = [{"id": 1, "title": "Dated task", "status": "open", "priority": "high", "due_date": "2026-05-01"}]
        task_tracker.save_tasks(tasks)
        task_tracker.cmd_publish()
        content = Path("tasks.html").read_text()
        self.assertIn("2026-05-01", content)

    def test_publish_no_due_date_shows_dash(self):
        task_tracker.cmd_add("No date task")
        task_tracker.cmd_publish()
        content = Path("tasks.html").read_text()
        self.assertIn("\u2014", content)

    def test_publish_overwrites_existing(self):
        Path("tasks.html").write_text("old content")
        task_tracker.cmd_publish()
        content = Path("tasks.html").read_text()
        self.assertNotIn("old content", content)
        self.assertIn("<!DOCTYPE html>", content)


if __name__ == "__main__":
    unittest.main()
