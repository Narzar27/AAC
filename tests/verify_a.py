"""Verification A — eight model-layer checks from the Module 2 guide.

Run with: python -m tests.verify_a
Every line must print PASS.
"""

import sys

from pydantic import ValidationError

from app.models import TaskCreate, TaskPriority, TaskStatus, TaskUpdate

results: list[tuple[str, bool]] = []


def check(name: str, passed: bool) -> None:
    results.append((name, passed))
    print(f"{'PASS' if passed else 'FAIL'}: {name}")


def rejected(model, **payload) -> bool:
    try:
        model(**payload)
        return False
    except ValidationError:
        return True


check("Whitespace title rejected", rejected(TaskCreate, title="   "))
check("Empty title rejected", rejected(TaskCreate, title=""))
check("Title over 200 characters rejected", rejected(TaskCreate, title="x" * 201))

task = TaskCreate(title="Test defaults")
check(
    "Defaults applied (status ToDo, priority Medium, empty description)",
    task.status == TaskStatus.TODO
    and task.priority == TaskPriority.MEDIUM
    and task.description == "",
)

check("Extra field rejected on TaskCreate", rejected(TaskCreate, title="T", extra_field="x"))
check("id rejected on TaskCreate", rejected(TaskCreate, title="T", id=99))
check("created_at rejected on TaskUpdate", rejected(TaskUpdate, created_at="2026-01-01T00:00:00Z"))
check("Invalid status rejected", rejected(TaskCreate, title="T", status="Later"))

if all(passed for _, passed in results):
    print("All 8 checks passed.")
else:
    sys.exit(1)
