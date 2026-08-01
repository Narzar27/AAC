from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.api.routes import health
from app.business_rules import InvalidStatusTransition, validate_status_transition
from app.core.config import settings
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Task Tracker REST API - Module 2 backend",
)

# Local frontend origins (Module 3): the board is served as static files on a
# different port, so the browser needs CORS approval for cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router)


@app.post("/tasks", response_model=TaskResponse, status_code=201, tags=["tasks"])
def create_task(payload: TaskCreate):
    """Create a task.

    Args:
        payload: Validated task input; server-managed fields (id, timestamps)
            are rejected by the model with 422.

    Returns:
        The stored task with generated ``id``, timestamps, and computed
        ``is_overdue``, as 201 Created.
    """
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    tag: str | None = Query(default=None, min_length=1),
):
    """List tasks, optionally filtered.

    All filters combine with AND. No matches returns 200 with an empty list,
    never 404. Invalid enum/boolean values and an empty ``tag`` return 422.

    Args:
        status: Keep only tasks with this exact status.
        priority: Keep only tasks with this exact priority.
        overdue: True keeps only overdue tasks; False keeps only non-overdue.
        tag: Keep only tasks whose tag list contains this exact tag.

    Returns:
        Possibly-empty list of tasks, as 200 OK.
    """
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue, tag=tag)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: int):
    """Return a single task by id.

    Raises:
        HTTPException: 404 if no task has this id.
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def patch_task(task_id: int, payload: TaskUpdate):
    """Partially update a task; only fields present in the payload change.

    Existence is checked before transition validation, so a bad transition on
    a missing id returns 404, not 422. Transition rules run only when
    ``status`` is present in the payload (see ``app.business_rules``).

    Raises:
        HTTPException: 404 if the task does not exist; 422 for an invalid
            status transition (including re-sending the current status).
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.status is not None:
        try:
            validate_status_transition(task["status"], payload.status)
        except InvalidStatusTransition as exc:
            raise HTTPException(status_code=422, detail=str(exc))

    updates = payload.model_dump(exclude_unset=True)
    return storage.update_task(task_id, updates)


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"])
def remove_task(task_id: int):
    """Delete a task, returning 204 with an empty body.

    Raises:
        HTTPException: 404 if the task does not exist (including a repeat
            delete of an already-deleted id).
    """
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
