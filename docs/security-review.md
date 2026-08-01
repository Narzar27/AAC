# Security Review — Task Tracker (Module 5.2)

Read-only audit. No code was changed as part of this review; fixes are backlog
items. Every AI finding is graded **Valid / False Positive / Noise** with a
one-sentence justification, then reconciled against a manual scan.

## AI findings (graded)

| # | Finding | File evidence | Risk | Grade | Why this grade |
|---|---|---|---|---|---|
| 1 | No authentication/authorization on any task endpoint; anyone who can reach the API can create, edit, and delete every task | `app/main.py` (all five routes have no dependency/guard) | Full data tampering if ever exposed beyond localhost | **Valid** | Real and correctly framed: intentional course scope (documented in README/AGENTS.md), but it must be re-stated as a blocking risk before any non-local deployment. |
| 2 | `description` and `assignee` accept unbounded strings — `title` is capped at 200 and tags at 10×30, but these two fields have no `max_length` | `app/models.py` lines 87, 90 (`description: str = ""`, `assignee: str | None = None`) | A client can POST multi-megabyte bodies that live forever in process memory and inflate every GET response | **Valid** | Repo-specific, cites the exact gap, and is inconsistent with the validation posture of the neighboring fields. |
| 3 | Task creation is unbounded — no cap on task count, no rate limiting | `app/storage.py` (`_tasks` dict grows without limit), `app/main.py` POST route | Trivial memory-exhaustion DoS for a public instance; combined with #2 it compounds | **Valid** | Concrete and tied to the in-memory design; acceptable locally, real for any shared deployment. |
| 4 | Dependencies are unpinned (`fastapi`, `uvicorn[standard]`, `pytest`, … with no versions), so builds are not reproducible and a compromised/breaking release installs silently | `requirements.txt`, `requirements-dev.txt` | Supply-chain and reproducibility risk; CI, Docker, and local can drift apart | **Valid** | True in this repo and actionable (pin or constrain versions); severity moderate for a course project. |
| 5 | Possible SQL injection in task filtering | (none) | — | **False Positive** | There is no SQL anywhere — storage is a Python dict and filters are list comprehensions in `app/storage.py`; the finding pattern-matched "filtering" to injection. |
| 6 | CORS is dangerously open | `app/main.py` CORS middleware | — | **False Positive** | The config is the opposite of open: two pinned localhost origins, four methods, `Content-Type` only — appropriate for local dev and already documented. |
| 7 | "All user input should be validated and sanitized" | (no file cited) | — | **Noise** | Generic OWASP-style advice with no field, file, or failure mode; the specific gaps it could mean are already findings #2–#3. |
| 8 | GitHub Actions uses tag references (`actions/checkout@v4`) instead of commit-SHA pins | `.github/workflows/ci.yml` | A hijacked action tag could run arbitrary code in CI | **Noise** | Technically true but low-stakes here: the workflow has no secrets and no deploy permissions, and tag-pinning majors is standard practice at this project's risk level. |

## Manual scan (my own pass, independent of the AI output)

- **XSS via task fields — checked, no finding:** every render path in
  `frontend/js/board.js` and `modal.js` uses `createElement`/`textContent`;
  `innerHTML`/`insertAdjacentHTML` appear nowhere in `frontend/` (grep: 0 hits).
  A task titled `<img onerror=...>` renders as literal text.
- **Secrets — checked, no finding:** `.env` is gitignored and dockerignored;
  `.env.example` contains no real values; no tokens/keys anywhere in history.
- **Error leakage — checked, minor note:** FastAPI's default 422 bodies and our
  transition messages expose field names and allowed transitions. That is
  API-contract information, not internals; acceptable.
- **Container posture — checked, no finding:** non-root `USER app` before CMD,
  slim pinned base, no `--reload`, test/dev files excluded from the image.
- **My finding (You-only): commit metadata exposes a work email** in a public
  repo (`nizar.afiouni@…` on every commit). Accepted deliberately for course
  attribution, but it belongs in the governance worksheet as a Medium-risk share.

## Reconciliation

| Agreement (AI + me) | AI-only | You-only (me) |
|---|---|---|
| #1 no-auth boundary; #2 unbounded description/assignee; #3 unbounded task creation | #4 unpinned dependencies (I had not written it down — verified true and kept); #8 action-tag pinning (graded Noise) | XSS render-path check with negative result; commit-email exposure; confirmation that CORS/container findings the AI got wrong are actually safe |

## Top-3 backlog (Valid findings, ranked)

1. **Bound the unbounded fields** (`description` ≤ 2000, `assignee` ≤ 100 in
   `app/models.py`) — smallest change, closes #2 and shrinks #3's blast radius.
   Owner: backend. *Not fixed in Module 5 — read-only module; this is the first
   post-course code change.*
2. **Pin dependency versions** in `requirements*.txt` (exact pins or `~=`
   constraints) so local, CI, and Docker resolve identically. Owner: tooling.
3. **Gate any exposure beyond localhost on an auth decision** — keep the no-auth
   scope for the course, but the README/decision docs must stay the tripwire:
   no port-forwarding or hosting until #1 is addressed. Owner: project.
