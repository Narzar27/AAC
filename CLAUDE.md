# CLAUDE.md — Task Tracker (AI-Assisted Coding course)

Project memory for AI agents working in this repository. Facts below are verified
against the code; do not guess beyond them.

## Tech stack

- Python 3.14 (local venv is 3.14.6 — CI must match; do NOT assume 3.11)
- FastAPI + Pydantic v2 (uses `@field_validator`, `computed_field`, `model_dump`)
- Uvicorn (dev server), pytest + httpx2 (starlette's TestClient wants `httpx2`, not `httpx`)
- Frontend: vanilla JavaScript ES modules — no framework, no build step, no npm
- Playwright (chromium) for the browser behavior contract

## Run and test commands (from the repo root)

```
venv\Scripts\python -m uvicorn app.main:app --reload --port 8000   # backend
venv\Scripts\python -m http.server 5500 --directory frontend        # frontend
venv\Scripts\python -m pytest tests/ -v                             # backend suite (49 tests)
venv\Scripts\python -m tests.verify_a                               # 8 model checks
venv\Scripts\python -m tests.verify_frontend                        # 19 browser checks (both servers must be running)
```

## Architecture

- `app/main.py` — FastAPI app, CORS middleware, five CRUD routes (+ `/health` router)
- `app/models.py` — enums, TaskCreate/TaskUpdate/TaskResponse, `is_overdue` predicate, tag validation
- `app/storage.py` — in-memory dict storage; helpers `add_task`, `get_all_tasks`, `get_task_by_id`, `update_task`, `delete_task`, `_reset`
- `app/business_rules.py` — `VALID_TRANSITIONS` + `validate_status_transition`
- `frontend/js/` — `api.js` (only module that fetches), `board.js` (render + drag-drop + filters), `modal.js` (create/edit form), `main.js` (wiring)
- `tests/` — pytest suite, `conftest.py` fixtures (autouse storage reset), verify scripts

## Business rules (do not guess — enforced in code)

- Statuses: `ToDo`, `InProgress`, `Done`. Priorities: `Low`, `Medium`, `High`.
- Valid transitions ONLY: `ToDo→InProgress`, `InProgress→Done`, `Done→InProgress`.
  Everything else is 422, **including same-status no-ops**.
- PATCH checks 404 (missing task) before transition validation, and skips transition
  validation when `status` is not in the payload.
- Title: required, trimmed, 1–200 chars; whitespace-only → 422. Explicit `null` title/tags
  on PATCH → 422 (omit the field instead); explicit `null` due_date CLEARS the date.
- Tags: trimmed, non-empty, ≤10 tags × ≤30 chars, duplicates rejected (422).
- Overdue = `due_date < today AND status != Done`, computed in the BACKEND
  (`models.is_overdue`; exposed as `is_overdue` on responses and the `overdue` query filter).
- Status codes: POST 201, GET 200 (empty list is 200 `[]`), PATCH 200, DELETE 204
  (empty body), missing id 404, validation/transition errors 422.

## UI states and frontend conventions

- Board states: loading, empty-per-column placeholder, ready, error banner.
- Drag-and-drop PATCHes only on column change; same-column drop sends no request.
- Rejected moves: refresh to server truth FIRST, then show the error message.
- Edit modal sends only changed fields (arrays compared by JSON.stringify).

## CORS / local dev

- Backend on port 8000; frontend static server on port 5500.
- Allowed origins: `http://localhost:5500` and `http://127.0.0.1:5500` (see `app/main.py`).

## Do-not rules

- Do NOT add authentication, user accounts, a database, multi-tenancy, real-time
  features, or deployment automation — permanently out of course scope.
- Do NOT relax backend validation to make the frontend's life easier.
- Do NOT add `Co-Authored-By: Claude` trailers to commits in this repo.
- Do NOT weaken tests to make them pass; fix the source or flag the test as wrong.
- Storage is in-memory by design; restarting the backend resets all tasks.
