# Dark Factory Build — Task Tracker CLI

A simple Python CLI tool for managing tasks in a local JSON file.
Built incrementally by the AI Dark Factory (Archon-based coding factory).

## Features

- Add, list, complete, and delete tasks
- Persist tasks to a local JSON file
- Filter tasks by status (`--status open/done`)
- Sort tasks by priority or due date (`--priority`, `--sort-due`)
- Colorized priority tags in terminal output (`--color`)

## Usage

```bash
python task_tracker.py add "Write tests for task listing"
python task_tracker.py add "Deploy hotfix" --priority high --due-date 2026-04-30
python task_tracker.py list
python task_tracker.py list --status open
python task_tracker.py list --priority          # sort by priority
python task_tracker.py list --sort-due          # sort by due date
python task_tracker.py list --color             # ANSI color for priority tags
python task_tracker.py list --color --no-color  # --no-color overrides --color (plain output)
python task_tracker.py done 1
python task_tracker.py delete 1
```

## Development

This project is managed by the AI Dark Factory.
Issues are automatically triaged, implemented, and reviewed via Archon workflows.

See `.archon/factory-rules.md` for factory constraints and rules.
