# Module 4.3 — Docker Artifacts and Security Log

## Design (verified by file inspection)

[`Dockerfile`](../../Dockerfile): multi-stage — a builder stage resolves
dependencies from `requirements.txt` (runtime set only: FastAPI + Uvicorn; test
tools live in `requirements-dev.txt` and never enter the image), and the runtime
stage copies the installed packages plus `app/` only. The CMD runs
`uvicorn app.main:app --host 0.0.0.0 --port 8000` with **no `--reload`**.

## Three-line security log

1. **Non-root user:** `RUN useradd --create-home app` followed by `USER app`
   appears **before** `CMD` in the Dockerfile, so the server process runs as
   `app`, not root.
2. **Slim runtime base:** both stages use the explicit `python:3.14-slim` tag —
   no `python:latest`, and the version matches the local venv and CI (3.14).
3. **No baked secrets:** the Dockerfile copies only `requirements.txt` and
   `app/`; [`.dockerignore`](../../.dockerignore) additionally excludes `.env*`,
   `.git`, `venv`/`.venv`, caches, `tests/`, `docs/`, `frontend/`, and editor/OS
   files, so no secret or local file can leak in via a broad COPY later.

## Runtime verification (executed 2026-08-01, final project)

Originally deferred; captured during the final-project release check:

```
docker build -t task-tracker:dev .   -> build succeeded; image size 233MB
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
GET http://localhost:8000/health     -> 200 {"status":"ok","timestamp":"2026-08-01T12:30:18.867622+00:00"}
docker exec tt-dev whoami            -> app        (non-root confirmed)
docker exec tt-dev ls /srv           -> app        (only the application package inside)
docker exec tt-dev env               -> 0 matches for KEY|TOKEN|SECRET|PASS
docker stop tt-dev
```

All three security-log properties now have runtime evidence, not just
file-inspection evidence.
