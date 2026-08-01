# Architecture (Strategy C — targeted context)

*Run limited to three anchor files — `app/main.py`, `app/models.py`,
`app/storage.py` — with the instruction to state plainly what is not visible.
Kept verbatim as the experiment artifact.*

## What the anchor files show

A single FastAPI app in `app/main.py` with five task routes and CORS pinned to
two localhost:5500 origins. Validation lives entirely in `app/models.py`
(Pydantic v2): strict input models rejecting extra fields and server-managed
values, field rules for title/tags/due_date, and a `TaskResponse` that computes
`is_overdue` from `due_date` and status. Transition enforcement is imported
from `app/business_rules.py` and called by PATCH only when a status is present,
after the 404 existence check. Storage (`app/storage.py`) is a module-level
in-memory dict with integer auto-ids, UTC timestamps, AND-combined filter
predicates, and a `_reset()` helper — data does not survive a restart.

## Not visible from the files I read

- The contents of `app/business_rules.py` — PATCH clearly delegates to
  `validate_status_transition`, but the allowed transition pairs are not
  visible from the anchor set.
- The `/health` route implementation (only its router import is visible).
- Any frontend behavior: `frontend/` was not read; nothing here can honestly
  describe the UI, its states, or how it handles 422s.
- Tests: `_reset()` implies test isolation exists, but test names, counts, and
  coverage are not visible.
- CI, Docker, and docs: not read; no claims made.
