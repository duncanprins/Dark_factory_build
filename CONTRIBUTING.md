# Contributing

Dark Factory Build is a simple Python task tracker CLI that stores tasks in a local JSON file and is maintained through the AI Dark Factory workflow. Contributions should keep the tool small, easy to run locally, and aligned with the existing command-line behavior.

## Local setup

This project does not require a package manager or dependency installation for normal use. From the repo root, run the CLI directly with Python:

```bash
python task_tracker.py add "Write tests for task listing"
python task_tracker.py list
python task_tracker.py list --status open
python task_tracker.py done 1
python task_tracker.py delete 1
```

Tasks are persisted to `tasks.json` in the working directory. Factory constraints and workflow rules live in `.archon/factory-rules.md`.

## Pull requests

- Keep changes focused on one issue or behavior at a time.
- Include or update tests when changing CLI behavior or task persistence.
- Run the relevant local validation before opening the pull request.
