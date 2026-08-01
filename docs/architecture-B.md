# Architecture (Strategy B — structured context)

*Run with structured context: AGENTS.md plus one-line summaries of every file.
Accurate and complete, but noticeably longer than the task needs — kept
verbatim as the experiment artifact.*

## System overview
Task Tracker is a two-part local application: a FastAPI backend (port 8000)
owning all data and rules, and a dependency-free vanilla-JS Kanban frontend
(static files on port 5500) that renders whatever the API says. CORS in
`app/main.py` pins the two local frontend origins.

## Backend
- `app/main.py`: app construction, CORS, five CRUD routes + `/health` router;
  PATCH checks existence (404) before transition validation (422) and applies
  only fields present in the payload (`exclude_unset`).
- `app/models.py`: `TaskStatus`/`TaskPriority` enums; `TaskCreate`/`TaskUpdate`
  (`extra="forbid"`, trimmed title 1–200, tags ≤10×≤30 deduplicated, null
  semantics: title/tags null → 422, due_date null → clear) and `TaskResponse`
  with computed `is_overdue` (`due_date < today and status != Done`).
- `app/business_rules.py`: `VALID_TRANSITIONS` frozenset (ToDo→InProgress,
  InProgress→Done, Done→InProgress); same-status moves rejected.
- `app/storage.py`: in-memory `dict[int, dict]`, insertion-ordered, single-pass
  predicate filtering (status/priority/overdue/tag), `_reset()` for tests.

## Frontend
- `js/api.js` (only fetch layer; flattens FastAPI error bodies) →
  `js/board.js` (render, four UI states, drag-and-drop that PATCHes on
  column change and reverts-then-messages on 422) →
  `js/modal.js` (create/edit; trims title client-side; sends only changed
  fields; 422 keeps modal open) → `js/main.js` (wiring + filter bar).

## Data flow
UI event → `api.js` fetch → route → Pydantic validation → business rule →
storage mutation → `TaskResponse` re-validation → JSON → `board.js` re-render
from server truth (the board never trusts its own optimistic state).

## Testing and verification
49 pytest tests (CRUD, validation, transitions, filters, edge cases) with an
autouse storage reset; `tests/verify_a.py` (8 model checks);
`tests/verify_frontend.py` (19 Playwright checks driving the real board);
CI runs pytest on push/PR (Python 3.14); tests proven by deliberate breakage.

## Known limits
In-memory storage (restart = empty board), no auth/accounts, no real database,
single-process assumption, `is_overdue` uses server-local date; Docker image is
backend-only. All deliberate course-scope decisions.
