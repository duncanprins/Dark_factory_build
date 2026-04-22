#!/usr/bin/env python3
"""Task Tracker CLI — minimal task management via JSON storage."""

import datetime
import json
import sys
from pathlib import Path

TASKS_FILE = Path("tasks.json")


def parse_flag(args, flag):
    """Extract a flag value from args list. Returns (value, remaining_args).

    remaining_args excludes both the flag and its value.  If the flag is
    absent, returns (None, args) unchanged.  If the flag is present but has
    no following value, prints an error and exits with code 1.
    """
    if flag not in args:
        return None, args
    idx = args.index(flag)
    if idx + 1 >= len(args):
        print(f"Error: {flag} requires a value.", file=sys.stderr)
        sys.exit(1)
    value = args[idx + 1]
    remaining = args[:idx] + args[idx + 2:]
    return value, remaining


def load_tasks():
    if not TASKS_FILE.exists():
        return []
    return json.loads(TASKS_FILE.read_text())


def save_tasks(tasks):
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))


def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1


def cmd_add(title, priority="medium", due_date=None):
    """Add a new task.

    Args:
        title: Task description string.
        priority: "low", "medium" (default), or "high".
        due_date: Date string "YYYY-MM-DD" or None. Stored as explicit null
                  in tasks.json when None. Invalid format prints an error
                  and exits with code 1.
    """
    if due_date is not None:
        try:
            datetime.datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid due-date format. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)
    tasks = load_tasks()
    task = {"id": next_id(tasks), "title": title, "status": "open", "priority": priority, "due_date": due_date}
    tasks.append(task)
    save_tasks(tasks)
    due_str = f" (due: {due_date})" if due_date else ""
    print(f"Added task #{task['id']}: {title} [{priority}]{due_str}")


def cmd_list(status=None, sort_priority=False, sort_due=False):
    tasks = load_tasks()
    filtered = [t for t in tasks if status is None or t["status"] == status]
    if not filtered:
        print("No tasks found.")
        return
    PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
    if sort_priority:
        filtered.sort(key=lambda t: PRIORITY_RANK.get(t.get("priority", "medium"), 1))
    if sort_due:
        # Sort by date ascending; tasks with no due_date sort last.
        # Tuple key: (is_undated, date_str) — True > False pushes undated to end.
        filtered.sort(key=lambda t: (t.get("due_date") is None, t.get("due_date") or ""))
    for t in filtered:
        mark = "x" if t["status"] == "done" else " "
        priority = t.get("priority", "medium")
        due_date = t.get("due_date")
        due_str = f" (due: {due_date})" if due_date else ""
        print(f"[{mark}] #{t['id']}: {t['title']} [{priority}]{due_str}")


def cmd_done(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "done"
            save_tasks(tasks)
            print(f"Marked #{task_id} as done.")
            return
    print(f"Task #{task_id} not found.")


def cmd_delete(task_id):
    tasks = load_tasks()
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == before:
        print(f"Task #{task_id} not found.")
        return
    save_tasks(tasks)
    print(f"Deleted task #{task_id}.")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: task_tracker.py <command> [args]")
        print("Commands: add, list, done, delete")
        sys.exit(1)

    command = args[0]

    if command == "add":
        if len(args) < 2:
            print("Usage: task_tracker.py add <title> [--priority low|medium|high] [--due-date YYYY-MM-DD]")
            sys.exit(1)
        add_args = args[1:]
        priority, add_args = parse_flag(add_args, "--priority")
        if priority is None:
            priority = "medium"
        due_date, add_args = parse_flag(add_args, "--due-date")
        title = " ".join(add_args)
        cmd_add(title, priority, due_date)

    elif command == "list":
        status = None
        sort_priority = "--priority" in args
        sort_due = "--sort-due" in args
        if "--status" in args:
            idx = args.index("--status")
            if idx + 1 < len(args):
                status = args[idx + 1]
        cmd_list(status, sort_priority, sort_due)

    elif command == "done":
        if len(args) < 2:
            print("Usage: task_tracker.py done <id>")
            sys.exit(1)
        cmd_done(int(args[1]))

    elif command == "delete":
        if len(args) < 2:
            print("Usage: task_tracker.py delete <id>")
            sys.exit(1)
        cmd_delete(int(args[1]))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
