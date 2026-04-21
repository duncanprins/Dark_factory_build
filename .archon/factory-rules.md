# Factory Rules — Dark Factory Build

## Project

A Python CLI task tracker. Single-file implementation (`task_tracker.py`).
Tasks are stored in `tasks.json`. No external dependencies beyond the Python standard library.

## What the factory MAY do

- Implement features described in GitHub issues
- Add, modify, or refactor code in `task_tracker.py`
- Update `tasks.json` schema if needed (with backwards compatibility)
- Write or update tests in `tests/`
- Update `README.md` to reflect new features
- Create new files if clearly needed (e.g. `tests/test_task_tracker.py`)

## What the factory MAY NOT do

- Change the project language (must stay Python)
- Add external dependencies (no pip packages beyond stdlib)
- Delete existing tests unless they are explicitly broken and unfixable
- Modify `.archon/factory-rules.md` without human review
- Push directly to `main` — all changes go via PR

## Code style

- Python 3.10+
- No type annotations required, but welcome
- Functions over classes for now (keep it simple)
- Inline docstrings only where non-obvious
- Tests in `tests/test_task_tracker.py` using stdlib `unittest`

## Issue format expected

A good issue has:
- Clear title: what feature or fix
- Description: what the expected behavior is
- Optional: example input/output

## Branching

- `main` — stable, factory-maintained
- Feature branches: `feature/<issue-number>-<short-slug>`

## Definition of done (per issue)

- Feature works as described
- At least one test added or updated
- README updated if the public interface changed
- PR created and passes validation
