# Task Tracker — Architecture

Final architecture document, merged from the three context-strategy runs
(`architecture-A/B/C.md`). Structure and detail come from Strategy B, trimmed
to what a new teammate needs; Strategy C's honesty conventions are kept.

## System overview

Two-part local application. A FastAPI backend on port 8000 owns all data,
validation, and business rules. A dependency-free vanilla-JS Kanban board,
served as static files on port 5500, renders whatever the API returns and never
re-implements a rule. CORS in `app/main.py` allows exactly the two local
frontend origins.

## Backend structure

| File | Responsibility |
|---|---|
| `app/main.py` | App + CORS + five CRUD routes (`/tasks…`) and the `/health` router. PATCH order: 404 existence check → transition validation (only if `status` present) → apply `exclude_unset` fields. |
| `app/models.py` | All field validation. Strict input models (`extra="forbid"`, no server-managed fields); trimmed title 1–200; tags ≤10 × ≤30 chars, no duplicates; null semantics — `title`/`tags: null` → 422, `due_date: null` → clears. `TaskResponse.is_overdue` computed: `due_date < today and status != Done`. |
| `app/business_rules.py` | `VALID_TRANSITIONS`: ToDo→InProgress, InProgress→Done, Done→InProgress. Everything else 422, including same-status. |
| `app/storage.py` | In-memory `dict[int, dict]`, integer auto-ids, UTC timestamps, AND-combined filters (status/priority/overdue/tag), `_reset()` for test isolation. |

Contract: POST 201 · GET 200 (`[]` when empty) · PATCH 200 · DELETE 204 empty
body · missing id 404 · validation/transition failures 422.

## Frontend structure

`js/api.js` is the only module that talks to the network (and flattens FastAPI
error bodies) → `js/board.js` renders columns/cards, owns the four UI states
(loading, per-column empty, ready, error) and drag-and-drop → `js/modal.js`
owns create/edit (client-side title trim, only-changed-fields PATCH, 422 keeps
the modal open) → `js/main.js` wires it together plus the overdue/tag filter bar.

## Data flow

UI event → fetch → route → Pydantic validation → business rule → storage
mutation → `TaskResponse` re-validation → JSON → full board re-render from
server truth. On a rejected drag the board refreshes first, then shows the
server's message — the UI never keeps optimistic state the server refused.

## Testing and verification

49 pytest tests with autouse storage reset; `tests/verify_a.py` (8 model
checks); `tests/verify_frontend.py` (19 Playwright checks against the live
board); CI (Python 3.14) on every push/PR, proven green→red→green. Tests are
trusted only after deliberate-breakage proof.

## Known limits (deliberate)

In-memory storage — restart empties the board; no auth/accounts; single-process
assumption; `is_overdue` uses the server's local date; Docker image is
backend-only. See `docs/decisions/` for the reasoning.

---

## Context-strategy comparison log

- **Most accurate file-level description:** B — structured context produced the
  only run that got every mechanism right, at the cost of ~40% extra length.
- **Most invention:** A — with nothing to read it confidently supplied a
  persistence layer, a service layer, and env-based config, none of which exist.
- **Most honest:** C — it refused to describe the frontend, tests, or the
  transition table it hadn't seen, and said so explicitly.
- **Fastest for a new teammate:** this merged doc; of the raw runs, B.

**Context strategy rule:** For correctness-sensitive work (security review,
behavior claims, audits), use targeted context (C) so the output states its own
boundaries instead of guessing. For onboarding and survey documents, use
structured context (B) and then cut length by hand — and treat minimal-context
output (A) as brainstorming only, never as a source of facts.
