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

# Reflection Log — Module 3 Hands-On

The frontend went up in the module's layer order — static layout, styling,
fetch/render, UI states, drag-and-drop, then the modal — and the AI was fastest at
exactly the layers the lecture predicts: markup, CSS, and render boilerplate came
out nearly right, while every real bug lived at a boundary. The four debugging-log
entries all fit that pattern: a Pydantic union that turned explicit null into a 500,
CSS `display: flex` silently defeating the `hidden` attribute, an edit form whose
full-payload PATCH collided with the backend's same-status rule, and an error
message erased by the board refresh one line later. None of them were visible by
reading the code "looking right" — all four were caught because the behavior
contract is an executable script (14 headless-browser checks) rather than a manual
checklist, which is the module's core lesson made literal. The refactor workflow
held up: contract green, git checkpoint, one selected section (render logic),
diff reviewed against the red-flag list, contract green again. The main correction
habit this module: when the frontend and backend disagreed, the fix always went
where the cause was — the backend rules were never loosened to make the UI's life
easier.
