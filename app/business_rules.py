"""Status-transition rules for tasks.

Enforced in the backend because UI guards can be bypassed by calling the
API directly. Same-status "transitions" are deliberately not valid.
"""

from app.models import TaskStatus


class InvalidStatusTransition(ValueError):
    pass


VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset(
    {
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS),  # work has started
        (TaskStatus.IN_PROGRESS, TaskStatus.DONE),  # work is finished
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS),  # a completed task can be reopened
    }
)


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted(f"{c.value} -> {n.value}" for c, n in VALID_TRANSITIONS)
        raise InvalidStatusTransition(
            f"Invalid status transition: {current.value} -> {new.value}. "
            f"Allowed transitions: {', '.join(allowed)}."
        )
