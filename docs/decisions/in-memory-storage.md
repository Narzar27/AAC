# Decision note: In-memory dict as the task storage layer

## Context

The Task Tracker needed a storage layer from Module 2 onward, and every later
module built on top of it: transition rules, filters (status, priority, overdue,
tag), a 49-test pytest suite, and a browser contract that resets state between
checks. The course explicitly excludes a production database, but "no database"
still leaves real choices: a JSON file on disk, SQLite, or plain process memory.

## Decision

Tasks live in a module-level `dict[int, dict]` in `app/storage.py`, with a
monotonically increasing integer id and a small set of helper functions
(`add_task`, `get_all_tasks`, `get_task_by_id`, `update_task`, `delete_task`,
`_reset`). Everything above it — routes, rules, tests, frontend — talks only to
those helpers, never to the dict.

## Alternatives considered

- **JSON file storage.** Survives restarts and was discussed in Module 1's
  architecture options. Rejected: file locking and partial-write handling add
  failure modes that would leak into every test, for durability nobody needs in
  a course project.
- **SQLite + SQLModel.** The most realistic option and the obvious migration
  target. Rejected for now: it drags schema migrations, session management, and
  ORM behavior into modules whose lessons were about prompting, validation, and
  verification — the storage layer would have stopped being the simplest thing
  in the repo.

## Trade-offs

What it makes easier: tests are fast (the whole suite runs in under a second)
and perfectly isolated (`_reset()` is one line in an autouse fixture); the
filter logic is a readable predicate instead of query-builder code; nothing in
the repo needs setup beyond `pip install`. What it makes worse: every restart
erases all data, which surprises anyone who expects a tracker to remember their
tasks; there is no concurrency safety beyond CPython's per-request serialization
in this single-process setup; and `updated_at`-style logic has to be hand-rolled
where a database would give it to us.

## Consequences

The helper-function boundary is now the contract: the mid-course refactor
rewrote `get_all_tasks` internals with zero changes elsewhere, which is exactly
the property we wanted. The Docker image can stay stateless (no volume mounts).
The frontend and tests both assume a restart equals a clean slate — the
`verify_frontend` contract depends on it. Anyone adding persistence later has a
single file to swap and 49 tests to tell them if they broke the contract.

## Open questions

- At what point does the demo need data to survive a restart? That is the real
  trigger for the SQLite migration, not code aesthetics.
- If two uvicorn workers ever run, the dict silently becomes per-worker state —
  do we guard against that with a startup assertion, or document it?
- `_reset()` is private-by-underscore but imported by tests; if the storage
  layer is swapped, does the test-isolation contract move into a fixture that
  owns the storage instead?

I would do this differently by defining the storage helpers as an explicit
interface (even just a Protocol) on day one — the functions grew one signature
at a time across three modules, and the shape only became a deliberate contract
in hindsight.
