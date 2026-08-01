"""Pydantic v2 models and field-level validation rules for tasks.

Client input models (`TaskCreate`, `TaskUpdate`) forbid extra fields and never
accept server-managed values (id, timestamps). `TaskResponse` is the only
shape the API returns and carries the computed `is_overdue` flag.
"""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def is_overdue(due_date: date | None, status: TaskStatus) -> bool:
    """Business rule: overdue = past its due date and not Done.

    Single source of truth — used both by the API's computed response field
    and by the storage-layer `overdue` filter.
    """
    return due_date is not None and due_date < date.today() and status != TaskStatus.DONE


def _validate_title(value: str) -> str:
    """Strip surrounding whitespace and reject titles that end up empty.

    Args:
        value: Raw title from the client.

    Returns:
        The trimmed title.

    Raises:
        ValueError: If the title is empty or whitespace-only (surfaces as 422).
    """
    stripped = value.strip()
    if not stripped:
        raise ValueError("title must not be empty or whitespace-only")
    return stripped


MAX_TAG_LENGTH = 30


def _validate_tags(tags: list[str]) -> list[str]:
    """Trim each tag and enforce the tag rules.

    Args:
        tags: Raw tag list from the client (count is capped at 10 by the
            Field constraint on the models, not here).

    Returns:
        Trimmed tags in their original order and case.

    Raises:
        ValueError: If a tag is empty after trimming, longer than
            ``MAX_TAG_LENGTH``, or a duplicate (surfaces as 422).
    """
    cleaned: list[str] = []
    for tag in tags:
        stripped = tag.strip()
        if not stripped:
            raise ValueError("tags must not be empty or whitespace-only")
        if len(stripped) > MAX_TAG_LENGTH:
            raise ValueError(f"tags must be at most {MAX_TAG_LENGTH} characters")
        if stripped in cleaned:
            raise ValueError(f"duplicate tag: {stripped}")
        cleaned.append(stripped)
    return cleaned


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: str | None = None
    due_date: date | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        return _validate_title(value)

    @field_validator("tags")
    @classmethod
    def tags_valid(cls, value: list[str]) -> list[str]:
        return _validate_tags(value)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee: str | None = None
    # Unlike title, an explicit null is meaningful here: it clears the due date.
    due_date: date | None = None
    tags: list[str] | None = Field(default=None, max_length=10)

    @field_validator("tags")
    @classmethod
    def tags_valid(cls, value: list[str] | None) -> list[str]:
        # Runs only when tags is present. Null is ambiguous — send [] to clear.
        if value is None:
            raise ValueError("tags cannot be null; send [] to clear them")
        return _validate_tags(value)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str | None) -> str:
        # This validator only runs when title is present in the payload, so an
        # explicit null is a client error — omitting the field means "no change".
        if value is None:
            raise ValueError("title cannot be null; omit the field to keep it unchanged")
        return _validate_title(value)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: str | None
    due_date: date | None = None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_overdue(self) -> bool:
        return is_overdue(self.due_date, self.status)
