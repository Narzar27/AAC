# Task Tracker — Modules 1–3

Task Tracker for the AI-Assisted Coding course. Module 1 built the FastAPI skeleton
with `/health`; Module 2 turned it into a working backend (strict Pydantic v2 models,
in-memory storage, five CRUD endpoints, status-transition rules, tested suite);
Module 3 added the browser frontend: a Kanban board with priority-sorted columns,
drag-and-drop status updates persisted through the API, and a create/edit modal with
client- and server-side validation. Still deliberately excluded: auth, real database,
deployment.

![Kanban board](docs/board.png)

## Mid-course project (branch `mid-course-project`)

Two features added end-to-end with the course AI-assisted workflow:

1. **Due dates + overdue filter** — optional `due_date` (`YYYY-MM-DD`, null clears
   it on edit), a backend-computed `is_overdue` field, `GET /tasks?overdue=`,
   a due/overdue badge on cards, and an "Overdue only" board toggle.
2. **Tags / labels** — validated `tags` list (trimmed, non-empty, ≤10 × ≤30 chars,
   no duplicates), `GET /tasks?tag=`, comma-separated input in the modal, tag chips
   on cards, and a tag filter in the board's filter bar.

Documentation for the project (user stories, mini-ADR, prompt log, verification
evidence, reflection) lives in [`docs/midcourse/`](docs/midcourse/). How to run the
backend, frontend, and tests is below — nothing extra is needed beyond
`pip install -r requirements.txt` (plus `python -m playwright install chromium`
once, for the browser contract).

## Project structure

```
app/
  main.py            # FastAPI app + five CRUD routes (PATCH enforces transitions)
  models.py          # Pydantic v2 models, TaskStatus/TaskPriority enums, validators
  storage.py         # in-memory storage helpers (add/get/update/delete/_reset)
  business_rules.py  # VALID_TRANSITIONS + validate_status_transition
  api/routes/        # health router
  core/              # configuration
frontend/
  index.html         # Kanban board page + create/edit modal markup
  css/styles.css
  js/api.js          # fetch layer — the only module that talks to the backend
  js/board.js        # column/card rendering, UI states, drag-and-drop
  js/modal.js        # create/edit form, client validation, 422 handling
  js/main.js         # entry point wiring board + modal
tests/
  verify_a.py        # Module 2 Verification A (8 model checks)
  verify_frontend.py # Module 3 executable behavior contract (headless Chromium)
  conftest.py        # TestClient, autouse storage reset, created_task fixtures
  test_tasks.py      # CRUD, validation, transition, delete, PATCH edge cases
  test_health.py
docs/                # user stories, ADR, behavior contract, debugging + other logs
```

## API

| Method | Path | Success | Errors |
|---|---|---|---|
| POST | `/tasks` | 201 + task | 422 invalid body |
| GET | `/tasks?status=&priority=&overdue=&tag=` | 200 + list (possibly `[]`) | 422 invalid filter value |
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

To run the frontend, serve `frontend/` on port 5500 (CORS is configured for it)
in a second terminal, with the backend running on port 8000:

```bash
python -m http.server 5500 --directory frontend
# open http://localhost:5500
```

## Verification

```bash
python -m tests.verify_a         # 8 model checks, all PASS
pytest tests/ -v                 # full backend suite
python -m tests.verify_frontend  # 14 browser contract checks (needs both servers
                                 # running and playwright chromium installed)
```
