# Reflection Log — Module 1 Hands-On

One entry per hands-on activity: what AI got right, what I corrected, and an
assumption AI made that I had to catch.

## Part A — AI-assisted requirements

- **AI got right:** Fast, well-structured first draft — seven stories in the
  story/acceptance-criteria format with sensible coverage of create, view, filter,
  update, status, delete, and validation.
- **I corrected:** The status-transition story allowed `Done` tasks to move back to
  `ToDo`. I replaced it with an explicit transition table where `Done` is terminal,
  and changed delete-missing-id from 200 to 404.
- **Assumption AI made:** That the app has user accounts ("as a logged-in user...").
  Auth and per-user lists are excluded from scope, so I removed that story entirely.

## Part B — AI-assisted architecture

- **AI got right:** A clear trade-off comparison between JSON-file storage and
  SQLite/SQLModel, mapped against simplicity, testability, local run, and familiarity.
- **I corrected:** The first proposal bundled the decision with a full production
  setup. I narrowed the ADR to what Module 1 actually needs and moved the storage
  upgrade to a named future risk instead of building it now.
- **Assumption AI made:** That the project would be containerized with Docker and
  use PostgreSQL by default. Neither was requested; both are documented as rejected
  in ADR-001.

## Part C — Scaffold the project skeleton

- **AI got right:** The folder layout matched the spec on the first pass
  (`app/api/routes`, `app/core`, `app/models`, `app/storage`, `tests/`), and
  `/health` plus Swagger worked on the first run — verified with pytest (2 passed)
  and a live `curl` returning 200.
- **I corrected:** The test dependency. Running pytest surfaced a deprecation
  warning — starlette's TestClient now wants `httpx2` instead of `httpx` — so I
  updated `requirements.txt` and re-ran the tests clean. "It passed" wasn't enough;
  reading the output caught it.
- **Assumption AI made:** That a `timestamp` in the health payload should come from
  local time. I used timezone-aware UTC (`datetime.now(timezone.utc)`) so the value
  is unambiguous — naive local timestamps are a classic subtle bug.

# Reflection Log — Module 2 Hands-On

The editor-based assistant was strongest at the mechanical layers: the Pydantic
models, storage helpers, and CRUD routes came out nearly right on the first strict
prompt, and all eight verify_a checks plus the 200/200/422/200/422/200 transition
matrix passed on the first live run. Where it guessed was at the boundaries between
requirements: an early draft validated status transitions before checking the task
existed (422 where a 404 belonged), included same-status pairs in VALID_TRANSITIONS,
and returned a JSON body on DELETE 204 — all caught by review against the module's
checklists, not by the AI. The Break Test was the most convincing step: disabling the
transition validator made exactly the three invalid-transition tests fail, and
neutering the blank-title check made exactly the two blank-title tests fail, which is
evidence the 28-test suite protects real behavior rather than just passing. The
biggest judgment call was documentation drift — Module 2's transition rules
contradict the Module 1 user stories (Done is now reopenable, no-ops are rejected),
so Story 5 was rewritten rather than leaving the docs lying about the code.
