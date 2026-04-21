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


if __name__ == "__main__":
    unittest.main()
