#!/usr/bin/env python3
"""Task Tracker CLI — minimal task management via JSON storage."""

import datetime
import html
import json
import sys
from pathlib import Path

TASKS_FILE = Path("tasks.json")
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
ANSI_COLORS = {
    "high": "\033[31;1m",   # red bold
    "medium": "\033[33m",   # yellow
    "low": "\033[32m",      # green
}
ANSI_RESET = "\033[0m"


def parse_flag(args, flag):
    """Extract a flag value from args list. Returns (value_or_none, remaining_args)."""
    if flag not in args:
        return None, args
    idx = args.index(flag)
    if idx + 1 >= len(args):
        return None, args
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


def colorize_priority(priority, use_color):
    """Wrap priority string in ANSI color codes if use_color is True.

    Returns the priority string unchanged if use_color is False or if
    the priority value is not found in ANSI_COLORS.
    """
    if not use_color:
        return priority
    code = ANSI_COLORS.get(priority, "")
    return f"{code}{priority}{ANSI_RESET}" if code else priority


def cmd_add(title, priority="medium", due_date=None):
    if due_date is not None:
        try:
            datetime.date.fromisoformat(due_date)
        except ValueError:
            print("Invalid due-date format. Use YYYY-MM-DD.")
            return
    tasks = load_tasks()
    task = {"id": next_id(tasks), "title": title, "status": "open", "priority": priority, "due_date": due_date}
    tasks.append(task)
    save_tasks(tasks)
    due_str = f" (due: {due_date})" if due_date else ""
    print(f"Added task #{task['id']}: {title} [{priority}]{due_str}")


def cmd_list(status=None, sort_priority=False, sort_due=False, use_color=False):
    tasks = load_tasks()
    filtered = [t for t in tasks if status is None or t["status"] == status]
    if not filtered:
        print("No tasks found.")
        return
    if sort_priority:
        filtered.sort(key=lambda t: PRIORITY_RANK.get(t.get("priority", "medium"), 1))
    if sort_due:
        filtered.sort(key=lambda t: (t.get("due_date") is None, t.get("due_date") or ""))
    for t in filtered:
        mark = "x" if t["status"] == "done" else " "
        priority = t.get("priority", "medium")
        due_date = t.get("due_date")
        due_str = f" (due: {due_date})" if due_date else ""
        colored_priority = colorize_priority(priority, use_color)
        print(f"[{mark}] #{t['id']}: {t['title']} [{colored_priority}]{due_str}")


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


def cmd_publish():
    tasks = load_tasks()
    open_tasks = [t for t in tasks if t.get("status") == "open"]
    open_tasks.sort(key=lambda t: PRIORITY_RANK.get(t.get("priority", "medium"), 1))

    if open_tasks:
        rows = ""
        for t in open_tasks:
            priority = t.get("priority", "medium")
            due_date = html.escape(t.get("due_date") or "\u2014")
            rows += (
                f'<tr><td>{t["id"]}</td>'
                f"<td>{html.escape(t['title'])}</td>"
                f'<td class="{priority}">{priority}</td>'
                f"<td>{due_date}</td></tr>\n"
            )
        body_content = (
            "<table>\n<thead><tr>"
            "<th>ID</th><th>Title</th><th>Priority</th><th>Due Date</th>"
            "</tr></thead>\n<tbody>\n" + rows + "</tbody>\n</table>"
        )
    else:
        body_content = "<p>No open tasks.</p>"

    page = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="UTF-8">\n<title>Open Tasks</title>\n<style>\n'
        "body { font-family: sans-serif; max-width: 800px; margin: 2rem auto; }\n"
        "table { border-collapse: collapse; width: 100%; }\n"
        "th, td { border: 1px solid #ccc; padding: 0.5rem 1rem; text-align: left; }\n"
        "th { background: #f5f5f5; }\n"
        ".high { color: #c0392b; font-weight: bold; }\n"
        ".medium { color: #e67e22; }\n"
        ".low { color: #27ae60; }\n"
        "</style>\n</head>\n<body>\n"
        f"<h1>Open Tasks</h1>\n{body_content}\n"
        "</body>\n</html>\n"
    )

    Path("tasks.html").write_text(page)
    count = len(open_tasks)
    noun = "task" if count == 1 else "tasks"
    print(f"Published {count} {noun} to tasks.html")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: task_tracker.py <command> [args]")
        print("Commands: add, list, done, delete, publish")
        sys.exit(1)

    command = args[0]

    if command == "add":
        if len(args) < 2:
            print("Usage: task_tracker.py add <title> [--priority low|medium|high] [--due-date YYYY-MM-DD]")
            sys.exit(1)
        add_args = args[1:]
        priority, add_args = parse_flag(add_args, "--priority")
        priority = priority or "medium"
        due_date, add_args = parse_flag(add_args, "--due-date")
        title = " ".join(add_args)
        cmd_add(title, priority, due_date)

    elif command == "list":
        sort_priority = "--priority" in args
        sort_due = "--sort-due" in args
        use_color = "--color" in args
        status, _ = parse_flag(args, "--status")
        cmd_list(status, sort_priority, sort_due, use_color)

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

    elif command == "publish":
        cmd_publish()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
