# Task Tracker API — Modules 1–2

Task Tracker backend for the AI-Assisted Coding course. Module 1 built the FastAPI
skeleton with `/health`; Module 2 turned it into a working backend: strict Pydantic v2
models, in-memory storage, five CRUD endpoints, status-transition business rules, and
a pytest suite proven with a Break Test. Still deliberately excluded: auth, real
database, deployment.

## Project structure

```
app/
  main.py            # FastAPI app + five CRUD routes (PATCH enforces transitions)
  models.py          # Pydantic v2 models, TaskStatus/TaskPriority enums, validators
  storage.py         # in-memory storage helpers (add/get/update/delete/_reset)
  business_rules.py  # VALID_TRANSITIONS + validate_status_transition
  api/routes/        # health router
  core/              # configuration
tests/
  verify_a.py        # Module 2 Verification A (8 model checks)
  conftest.py        # TestClient, autouse storage reset, created_task fixtures
  test_tasks.py      # CRUD, validation, transition, delete tests
  test_health.py
docs/                # user stories, ADR, prompt/correction/reflection logs
```

## API

| Method | Path | Success | Errors |
|---|---|---|---|
| POST | `/tasks` | 201 + task | 422 invalid body |
| GET | `/tasks?status=&priority=` | 200 + list (possibly `[]`) | 422 invalid filter value |
| GET | `/tasks/{id}` | 200 + task | 404 missing |
| PATCH | `/tasks/{id}` | 200 + task | 404 missing, 422 invalid payload/transition |
| DELETE | `/tasks/{id}` | 204, empty body | 404 missing |
| GET | `/health` | 200 | — |

Status transitions (enforced in the backend): `ToDo → InProgress`,
`InProgress → Done`, `Done → InProgress`. Everything else — including
same-status no-ops — returns 422.

## Setup and run

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger docs: http://localhost:8000/docs

## Verification

```bash
python -m tests.verify_a     # 8 model checks, all PASS
pytest tests/ -v             # full suite
```
