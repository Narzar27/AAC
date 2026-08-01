# Module 4.1 — Claude Code Setup and Verified Interactions

## Setup

- Agent: Claude Code running in the terminal at the repo root (`C:\Users\nizar\Desktop\AAC`),
  branch `module-4` (created from `mid-course-project` so the submitted branch stays frozen).
- `CLAUDE.md` generated as a draft and then hand-corrected before committing — notable
  hand corrections: Python version fixed to **3.14** (the draft assumed the course demo's
  3.11; the actual venv is 3.14.6), test-client dependency corrected to `httpx2`, the
  same-status-transition rule marked explicitly (a generic FastAPI description would
  miss it), and repo-specific do-not rules added (no auth/DB/deployment, no commit
  trailers, never weaken tests).

## Verified interaction 1 — endpoints and status codes

**Claude's claim:** the API exposes POST `/tasks` (201), GET `/tasks` (200),
GET `/tasks/{id}` (200/404), PATCH `/tasks/{id}` (200/404/422), DELETE `/tasks/{id}`
(204/404), plus GET `/health`.

**Checked against `app/main.py`:** decorators at lines 31 (`status_code=201`),
36, 46 (+404 at line 50), 54 (+404 at 58, +422 at 64), and 70 (`status_code=204`,
+404 at 73). `/health` comes from the included router in `app/api/routes/health.py`.
**Verdict: matches the code — accepted.**

## Verified interaction 2 — status transition rules

**Claude's claim:** exactly three transitions are valid — `ToDo→InProgress`,
`InProgress→Done`, `Done→InProgress` — and everything else returns 422, including
re-sending the current status.

**Checked against `app/business_rules.py`:** `VALID_TRANSITIONS` (lines 16–18)
contains exactly those three pairs; `validate_status_transition` raises for any pair
not in the frozenset, and no `(x, x)` pairs are present, so same-status moves are
rejected. Confirmed behaviorally by `test_transition_same_status_returns_422`.
**Verdict: matches the code — accepted.**

## Plan-mode practice (no edits)

Asked for a plan-only proposal for a hypothetical `GET /version` endpoint: the plan
identified `app/main.py` as the only file to change, a two-line route returning
`{"version": settings.version}` reusing `app/core/config.py`, one new test, and
`pytest -k version` as verification — and correctly flagged scope risks (do not add
CI/Docker/frontend changes for this). No files were edited; the endpoint was **not**
implemented — Module 4 adds no product features.
