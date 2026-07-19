# Mini-ADR — Due Dates + Overdue Filter, Tags / Labels

**Status:** Accepted — 2026-07-19 (written before implementation, per the brief)

Both features extend the existing layers rather than adding new ones: field and
validation changes in `app/models.py`, filter predicates in `app/storage.py`, query
parameters on the existing `GET /tasks` route, and UI in the existing modal plus a
new compact filter bar above the board. `due_date` is a Pydantic `date` (ISO
`YYYY-MM-DD`; malformed input is a 422 for free), optional on create/update, where an
explicit `null` on PATCH *clears* the date — a deliberate contrast with `title`,
where null is an error, because "no deadline" is a valid state and "no title" is not.
Overdue is a business rule, so it is computed in the backend (`due_date < today` and
status ≠ `Done`) and exposed two ways: a computed `is_overdue` field on every task
response (the card just reads it) and an `overdue` boolean query filter that reuses
the same predicate. Tags are a `list[str]` stored per task: trimmed, non-empty,
max 10 tags of 30 chars each, duplicates rejected with 422; `GET /tasks?tag=x` does
an exact-match membership test, and the frontend enters tags comma-separated in the
modal and renders them as chips.

Alternatives AI suggested and rejected: computing overdue in the frontend (two
clocks can disagree, and the backend owns rules — Module 3's source-of-truth
principle); a separate `Tag` entity with its own CRUD routes and a join structure
(massive overbuild for in-memory storage — a plain list keeps both storage helpers
and tests small); lowercase-normalizing and silently deduplicating tags (hidden
mutation of user input — validation errors are more honest); rejecting past due
dates on create (would block recording already-overdue work); and a `GET /tags`
autocomplete endpoint (out of scope). One risk to revisit if the project grew:
`is_overdue` uses the server's local date, so a client in a different timezone can
briefly disagree with the pill near midnight — acceptable for a course project,
would need a timezone policy in production.
