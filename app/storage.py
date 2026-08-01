"""In-memory task storage. Tasks live in a dict for Module 2; a real
database is out of scope until a later module."""

from datetime import datetime, timezone

from app.models import TaskCreate, TaskPriority, TaskStatus, is_overdue

_tasks: dict[int, dict] = {}
_next_id: int = 1


def _now() -> datetime:
    return datetime.now(timezone.utc)


def add_task(task: TaskCreate) -> dict:
    """Store a new task and return its full record.

    Args:
        task: Validated creation payload.

    Returns:
        The stored record with generated ``id`` and UTC ``created_at`` /
        ``updated_at`` timestamps.
    """
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
    overdue: bool | None = None,
    tag: str | None = None,
) -> list[dict]:
    """Return tasks matching every provided filter (AND semantics).

    Args:
        status: Exact status to keep, or None for no status filter.
        priority: Exact priority to keep, or None for no priority filter.
        overdue: True keeps overdue tasks only, False keeps non-overdue only,
            None disables the filter.
        tag: Exact tag membership to require, or None for no tag filter.

    Returns:
        Possibly-empty list of task records in insertion order.
    """

    def matches(task: dict) -> bool:
        if status is not None and task["status"] != status:
            return False
        if priority is not None and task["priority"] != priority:
            return False
        if overdue is not None and is_overdue(task["due_date"], task["status"]) != overdue:
            return False
        if tag is not None and tag not in task["tags"]:
            return False
        return True

    return [task for task in _tasks.values() if matches(task)]


def get_task_by_id(task_id: int) -> dict | None:
    """Return the task record for ``task_id``, or None if absent."""
    return _tasks.get(task_id)


def update_task(task_id: int, updates: dict) -> dict | None:
    """Apply field updates to a stored task and bump ``updated_at``.

    Args:
        task_id: Id of the task to change.
        updates: Field/value pairs to overwrite; callers pass only fields
            that were present in the PATCH payload.

    Returns:
        The updated record, or None if the task does not exist.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None
    task.update(updates)
    task["updated_at"] = _now()
    return task


def delete_task(task_id: int) -> bool:
    """Remove a task; True if it existed, False if the id was unknown."""
    return _tasks.pop(task_id, None) is not None


def _reset() -> None:
    """Clear all tasks and restart id numbering (test isolation helper)."""
    global _next_id
    _tasks.clear()
    _next_id = 1
