# Dark Factory Build — Task Tracker CLI

A simple Python CLI tool for managing tasks in a local JSON file.
Built incrementally by the AI Dark Factory (Archon-based coding factory).

## Features

- Add, list, complete, and delete tasks
- Persist tasks to a local JSON file
- Filter tasks by status
- Color-coded priority output (`--color` flag on `list`)

## Usage

```bash
python task_tracker.py add "Write tests for task listing"
python task_tracker.py list
python task_tracker.py list --status open
python task_tracker.py done 1
python task_tracker.py delete 1
python task_tracker.py list --color             # colored priority output (red/yellow/green by priority)
python task_tracker.py list --color --no-color  # --no-color overrides --color (useful when --color is set by an alias)
```

## Development

This project is managed by the AI Dark Factory.
Issues are automatically triaged, implemented, and reviewed via Archon workflows.

See `.archon/factory-rules.md` for factory constraints and rules.
