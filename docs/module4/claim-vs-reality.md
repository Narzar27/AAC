# Module 4.4 — Documentation Claim-vs-Reality Log

Inaccuracies actually caught while generating/verifying documentation this module,
plus high-risk claims that were verified against code before the docs shipped.

## Caught and fixed

| Claim (in docs before this module) | Reality | Resolution |
|---|---|---|
| README: everything needed is installed by `pip install -r requirements.txt`, "plus `python -m playwright install chromium` once" | `playwright` was **never in requirements.txt** — it had been installed ad hoc into the local venv, so on a clean checkout `python -m playwright` fails with "No module named playwright" | Created `requirements-dev.txt` (pytest, httpx2, playwright, `-r requirements.txt`), README setup rewritten to use it; runtime `requirements.txt` slimmed to FastAPI + Uvicorn (also keeps the Docker image lean) |
| README verification section: "`python -m tests.verify_frontend` — **14** browser contract checks" | The contract has been **19 checks** since the mid-course features were added; the README was never updated | README corrected to 19; the number now matches the script's own output ("All 19 contract checks passed") |

## Verified before publishing (no drift found)

| Docstring/README claim | How it was verified |
|---|---|
| PATCH returns **404 before 422** — a bad transition on a missing id is 404 | `app/main.py` `patch_task`: `get_task_by_id` + 404 raise precede `validate_status_transition`; behaviorally pinned by `test_patch_missing_task_returns_404` |
| DELETE returns **204 with an empty body**, not JSON | `status_code=204` on the route; `test_delete_task_returns_204_with_empty_body` asserts `response.content == b""` |
| Same-status PATCH is rejected (422), i.e. no idempotent status writes | `VALID_TRANSITIONS` contains no `(x, x)` pairs; `test_transition_same_status_returns_422` |
| `overdue=false` filter returns only **non-overdue** tasks (it is not "no filter") | `storage.get_all_tasks` compares `is_overdue(...) != overdue`; `test_overdue_filter_returns_only_overdue_tasks` asserts the false-branch set |

Rule applied throughout: the docstring diff was checked to be documentation-only
(`git diff --stat`: 123 insertions, 0 deletions in `app/`) and the full suite ran
green afterwards — documentation work must never smuggle in behavior changes.
