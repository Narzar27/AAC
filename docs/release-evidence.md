# Release Evidence

## Baseline

- Branch: `final-project` (created from the merged course state; no product changes)
- Date: 2026-08-01
- Local app run command: `venv\Scripts\python -m uvicorn app.main:app --port 8000`
- /health result: `200 {"status":"ok","timestamp":"2026-08-01T12:26:05.157021+00:00"}`
- Frontend check: served with `venv\Scripts\python -m http.server 5500 --directory frontend`
  and opened at http://localhost:5500 — the Kanban board renders and the create/edit
  flow works; as stronger-than-eyeball evidence, the executable behavior contract
  (`python -m tests.verify_frontend`) drove the live board through create, edit,
  drag-and-drop, filters, and dismissal: **All 19 contract checks passed.**
- Test command: `venv\Scripts\python -m pytest tests/ -v`
- Test result: **49 passed** (no failures, none pre-existing)

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest run: green on the `final-project` branch push —
  https://github.com/Narzar27/AAC/actions/runs/30699842610 (success).
  Prior green→red→green proof from Module 4 is linked in `docs/module4/ci-evidence.md`.
- Test command used by CI: `pytest tests/ -v` on pinned Python **3.14**
  (matches the local venv), after `pip install -r requirements-dev.txt`
- Shortcut check: no `continue-on-error` / no `|| true` / no `--exit-zero` /
  pytest is not skipped or piped — verified by reading the workflow line by line
  (9 lines of steps; nothing swallows a failure).

## Docker evidence

- Build command: `docker build -t task-tracker:dev .` → succeeded; image size 233MB
- Run command: `docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev`
- /health check: `GET http://localhost:8000/health` from the running container →
  `200 {"status":"ok","timestamp":"2026-08-01T12:30:18.867622+00:00"}`
- Non-root check: `docker exec tt-dev whoami` → **`app`** (not root)
- No-baked-secrets check: `docker exec tt-dev ls /srv` → only `app` (no tests,
  docs, env files); `docker exec tt-dev env` → 0 matches for
  `KEY|TOKEN|SECRET|PASS`; `.dockerignore` excludes `.env*`, `.git`, venvs, caches.
- Runtime command in the image: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  (no `--reload`).

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README "Run with Docker" section: the four commands work as written and `whoami` returns `app` | Executed all four commands today (build, run, curl /health, exec whoami) | All match: 200 on /health, `whoami` → `app` | None needed |
| README: "storage is in-memory, so a container restart starts with an empty board" | Started a **fresh** container and called `GET /tasks` | `200 []` — empty list on a fresh container, as claimed | None needed |
| README: `python -m tests.verify_frontend` runs **19** browser contract checks | Ran the script against live servers | Output: "All 19 contract checks passed" — count matches | None needed |
| README/CI claim: CI runs pytest on push and pull request on Python 3.14 | `.github/workflows/ci.yml` triggers block + today's green run on the branch push | Push trigger confirmed live (run 30699842610); `python-version: "3.14"` pinned in the workflow | None needed |

(Two doc lies were caught and fixed by this same habit in Module 4 — the
phantom `playwright` in requirements and a stale contract-check count; see
`docs/module4/claim-vs-reality.md`. Today's pass found no new drift.)
