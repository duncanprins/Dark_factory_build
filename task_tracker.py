#!/usr/bin/env python3
"""Task Tracker CLI — minimal task management via JSON storage."""

import json
import sys
from pathlib import Path

TASKS_FILE = Path("tasks.json")


def load_tasks():
    if not TASKS_FILE.exists():
        return []
    return json.loads(TASKS_FILE.read_text())


def save_tasks(tasks):
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))


def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1


def cmd_add(title):
    tasks = load_tasks()
    task = {"id": next_id(tasks), "title": title, "status": "open"}
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task #{task['id']}: {title}")


def cmd_list(status=None):
    tasks = load_tasks()
    filtered = [t for t in tasks if status is None or t["status"] == status]
    if not filtered:
        print("No tasks found.")
        return
    for t in filtered:
        mark = "x" if t["status"] == "done" else " "
        print(f"[{mark}] #{t['id']}: {t['title']}")


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
            print("Usage: task_tracker.py add <title>")
            sys.exit(1)
        cmd_add(" ".join(args[1:]))

    elif command == "list":
        status = None
        if "--status" in args:
            idx = args.index("--status")
            if idx + 1 < len(args):
                status = args[idx + 1]
        cmd_list(status)

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
