#!/usr/bin/env python3
"""Task Tracker CLI — minimal task management via append-only JSONL storage."""

import datetime
import html
import json
import os
import sys
import uuid
from pathlib import Path

TASKS_FILE = Path("tasks.jsonl")
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


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


def _legacy_tasks_file():
    if TASKS_FILE.suffix == ".jsonl":
        return TASKS_FILE.with_suffix(".json")
    return TASKS_FILE


def _read_events():
    if not TASKS_FILE.exists():
        legacy_file = _legacy_tasks_file()
        if legacy_file.exists():
            return [{"op": "add", "task": task, "event_id": str(uuid.uuid4())} for task in json.loads(legacy_file.read_text())]
        return []

    events = []
    for line in TASKS_FILE.read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def _replay_tasks(include_event_ids=False):
    tasks = []
    by_id = {}
    next_task_id = 1

    for event in _read_events():
        op = event.get("op")
        if op == "add":
            source = event.get("task", event)
            task_id = source.get("id", next_task_id)
            task = {
                "id": task_id,
                "title": source["title"],
                "status": source.get("status", "open"),
                "priority": source.get("priority", "medium"),
                "due_date": source.get("due_date"),
            }
            if include_event_ids:
                task["_event_id"] = event.get("event_id")
            tasks.append(task)
            by_id[task_id] = task
            next_task_id = max(next_task_id, task_id + 1)
        elif op == "done":
            task = by_id.get(event.get("task_id"))
            if task is not None:
                task["status"] = "done"
        elif op == "delete":
            task = by_id.pop(event.get("task_id"), None)
            if task is not None:
                tasks.remove(task)

    return tasks


def load_tasks():
    tasks = _replay_tasks()
    for task in tasks:
        task.pop("_event_id", None)
    return tasks


def save_tasks(tasks):
    events = []
    for task in tasks:
        event_id = str(uuid.uuid4())
        events.append({"op": "add", "event_id": event_id, "task": task})
        if task.get("status") == "done":
            events.append({"op": "done", "task_id": task["id"]})
    _write_events(events)


def _write_events(events):
    content = "".join(json.dumps(event, separators=(",", ":")) + "\n" for event in events)
    TASKS_FILE.write_text(content)


def _append_event(event):
    _migrate_legacy_file()
    line = json.dumps(event, separators=(",", ":")) + "\n"
    flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
    fd = os.open(TASKS_FILE, flags, 0o666)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def _migrate_legacy_file():
    if TASKS_FILE.exists():
        return

    legacy_file = _legacy_tasks_file()
    if not legacy_file.exists():
        return

    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(TASKS_FILE, flags, 0o666)
    except FileExistsError:
        return

    try:
        legacy_tasks = json.loads(legacy_file.read_text())
        events = [{"op": "add", "event_id": str(uuid.uuid4()), "task": task} for task in legacy_tasks]
        content = "".join(json.dumps(event, separators=(",", ":")) + "\n" for event in events)
        os.write(fd, content.encode("utf-8"))
    finally:
        os.close(fd)


def cmd_add(title, priority="medium", due_date=None):
    if due_date is not None:
        try:
            datetime.date.fromisoformat(due_date)
        except ValueError:
            print("Invalid due-date format. Use YYYY-MM-DD.")
            return
    event_id = str(uuid.uuid4())
    event = {
        "op": "add",
        "event_id": event_id,
        "task": {"title": title, "status": "open", "priority": priority, "due_date": due_date},
    }
    _append_event(event)
    task = next(t for t in _replay_tasks(include_event_ids=True) if t.get("_event_id") == event_id)
    due_str = f" (due: {due_date})" if due_date else ""
    print(f"Added task #{task['id']}: {title} [{priority}]{due_str}")


def cmd_list(status=None, sort_priority=False, sort_due=False):
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
        print(f"[{mark}] #{t['id']}: {t['title']} [{priority}]{due_str}")


def cmd_done(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            _append_event({"op": "done", "task_id": task_id})
            print(f"Marked #{task_id} as done.")
            return
    print(f"Task #{task_id} not found.")


def cmd_delete(task_id):
    tasks = load_tasks()
    if not any(t["id"] == task_id for t in tasks):
        print(f"Task #{task_id} not found.")
        return
    _append_event({"op": "delete", "task_id": task_id})
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

    elif command == "publish":
        cmd_publish()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
