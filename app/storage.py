"""In-memory task storage. Tasks live in a dict for Module 2; a real
database is out of scope until a later module."""

from datetime import datetime, timezone

from app.models import TaskCreate, TaskPriority, TaskStatus

_tasks: dict[int, dict] = {}
_next_id: int = 1


def _now() -> datetime:
    return datetime.now(timezone.utc)


def add_task(task: TaskCreate) -> dict:
    global _next_id
    now = _now()
    record = {
        "id": _next_id,
        **task.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    _tasks[_next_id] = record
    _next_id += 1
    return record


def get_all_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[dict]:
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [t for t in tasks if t["status"] == status]
    if priority is not None:
        tasks = [t for t in tasks if t["priority"] == priority]
    return tasks


def get_task_by_id(task_id: int) -> dict | None:
    return _tasks.get(task_id)


def update_task(task_id: int, updates: dict) -> dict | None:
    task = _tasks.get(task_id)
    if task is None:
        return None
    task.update(updates)
    task["updated_at"] = _now()
    return task


def delete_task(task_id: int) -> bool:
    return _tasks.pop(task_id, None) is not None


def _reset() -> None:
    global _next_id
    _tasks.clear()
    _next_id = 1
