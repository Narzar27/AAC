# AGENTS.md — Task Tracker (repo-level agent instructions)

Instructions for AI agent threads working in this repository. Companion to
`CLAUDE.md` (terminal-agent memory); this file adds the Module 5 boundaries.

## Stack and commands

- Python 3.14, FastAPI, Pydantic v2, Uvicorn; vanilla-JS ES-module frontend (no build step).
- Install: `pip install -r requirements-dev.txt` (runtime-only set: `requirements.txt`).
- Run API: `venv\Scripts\python -m uvicorn app.main:app --reload --port 8000`
- Run frontend: `venv\Scripts\python -m http.server 5500 --directory frontend`
- Tests: `venv\Scripts\python -m pytest tests/ -v` (49 tests) · model checks: `python -m tests.verify_a`
- Browser contract: `python -m tests.verify_frontend` (19 checks; both servers must be running).

## Project rules

- Statuses `ToDo/InProgress/Done`; valid transitions only `ToDo→InProgress`,
  `InProgress→Done`, `Done→InProgress`; everything else 422 including same-status.
- POST 201 · GET 200 (empty list = `[]`) · PATCH 200 · DELETE 204 empty body · missing id 404.
- Backend owns all validation and business rules; the frontend never re-implements them.
- Storage is an in-memory dict by design (see `docs/decisions/in-memory-storage.md`).
- Out of scope permanently: auth, user accounts, databases, multi-tenancy,
  real-time, deployment automation. Do not add them.

## Module 5 boundaries

- Default posture: **read-only analysis**. Required edits belong in `docs/` (and this file).
- Any proposed change to `app/`, `tests/`, `frontend/`, `Dockerfile`, or CI is out of
  scope for Module 5 and must be rejected or explicitly flagged for later work.
- One bounded task per thread; do not mix security review, planning, and playbook work.

## Review expectations

- Cite the file (and function) for every claim; mark anything uncertain as [VERIFY]
  instead of guessing. Say "no finding" rather than inventing one.
- Never invent project structure; this repo has no database, no auth, no SQL.
- Ask before broad multi-file edits; explain every proposed diff before it is applied.
- Do not add `Co-Authored-By` trailers to commits.
