import json
import sys
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

    def tearDown(self):
        if task_tracker.TASKS_FILE.exists():
            task_tracker.TASKS_FILE.unlink()

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

    def test_list_default_shows_only_open(self):
        task_tracker.cmd_add("Open task")
        task_tracker.cmd_add("Done task")
        task_tracker.cmd_done(2)
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list(status="open")
        self.assertEqual(mock_print.call_count, 1)
        output = mock_print.call_args_list[0][0][0]
        self.assertIn("Open task", output)

    def test_list_done_flag_shows_only_done(self):
        task_tracker.cmd_add("Open task")
        task_tracker.cmd_add("Done task")
        task_tracker.cmd_done(2)
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list(status="done")
        self.assertEqual(mock_print.call_count, 1)
        output = mock_print.call_args_list[0][0][0]
        self.assertIn("Done task", output)

    def test_list_done_flag_empty_when_none_done(self):
        task_tracker.cmd_add("Open task")
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list(status="done")
        mock_print.assert_called_with("No tasks found.")

    def test_list_done_flag_excludes_open_tasks(self):
        task_tracker.cmd_add("Open task")
        task_tracker.cmd_add("Done task")
        task_tracker.cmd_done(2)
        with patch("builtins.print") as mock_print:
            task_tracker.cmd_list(status="done")
        calls = [str(c) for c in mock_print.call_args_list]
        self.assertFalse(any("Open task" in c for c in calls))

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


class TestPublish(unittest.TestCase):
    def setUp(self):
        task_tracker.TASKS_FILE = Path("/tmp/test_tasks.json")
        if task_tracker.TASKS_FILE.exists():
            task_tracker.TASKS_FILE.unlink()

    def tearDown(self):
        if task_tracker.TASKS_FILE.exists():
            task_tracker.TASKS_FILE.unlink()
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
