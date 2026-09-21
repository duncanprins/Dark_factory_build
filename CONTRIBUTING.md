# Contributing

Dark Factory Build is a simple Python task tracker CLI that manages local tasks in a JSON file and is developed through the AI Dark Factory workflow; contributions should keep the tool small, clear, and aligned with the existing command-line behavior.

## Local setup

Run the CLI directly with Python from the repository root:

```bash
python task_tracker.py add "Write tests for task listing"
python task_tracker.py list
python task_tracker.py list --status open
python task_tracker.py done 1
python task_tracker.py delete 1
```

Run the test suite with:

```bash
python -m unittest
```

## Pull requests

- Keep changes focused on one issue or behavior at a time.
- Include or update tests for CLI behavior changes.
- Update README or related docs when commands, options, or workflows change.
