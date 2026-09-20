# Contributing

Dark Factory Build is a small Python task tracker CLI that is developed through Archon-driven factory workflows, so contributions should stay focused, easy to validate, and aligned with the repository rules.

## Local setup

Clone the repository, then run the CLI directly with Python from the repo root. The tool stores tasks in a local `tasks.json` file.

```bash
python task_tracker.py add "Write tests for task listing"
python task_tracker.py list
python task_tracker.py list --status open
python task_tracker.py done 1
python task_tracker.py delete 1
```

Run the test suite with:

```bash
python -m unittest discover tests
```

Review `.archon/factory-rules.md` for the project constraints and workflow rules.

## Pull requests

- Keep changes scoped to the issue being implemented.
- Include or update tests for behavior changes.
- Document validation commands and results in the pull request description.
