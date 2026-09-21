# Dark Factory Build — Task Tracker CLI

A simple Python CLI tool for managing tasks in a local append-only JSONL file.
Built incrementally by the AI Dark Factory (Archon-based coding factory).

## Features

- Add, list, complete, and delete tasks
- Persist tasks to a local `tasks.jsonl` event log
- Filter tasks by status

Existing `tasks.json` data is loaded as a legacy base when `tasks.jsonl`
does not yet contain replacement events.

## Usage

```bash
python task_tracker.py add "Write tests for task listing"
python task_tracker.py list
python task_tracker.py list --status open
python task_tracker.py done 1
python task_tracker.py delete 1
```

## Development

This project is managed by the AI Dark Factory.
Issues are automatically triaged, implemented, and reviewed via Archon workflows.

See `.archon/factory-rules.md` for factory constraints and rules.
