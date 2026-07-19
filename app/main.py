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
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    tag: str | None = Query(default=None, min_length=1),
):
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue, tag=tag)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: int):
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def patch_task(task_id: int, payload: TaskUpdate):
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
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
