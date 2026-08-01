# Module 4.2 — CI Green → Red → Green Evidence

Workflow: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — one `test`
job on `ubuntu-latest`, Python pinned to **3.14** (the repo's real version; the
course demo's 3.11 would test a version nobody runs here), installs
`requirements-dev.txt`, runs `pytest tests/ -v`. Inspected against the red-flag
list before committing: no `continue-on-error`, no `|| true`, no `--exit-zero`, no
output piping that hides the exit code, no deployment steps, file at the repo root.

| Step | Commit | Run | Result |
|---|---|---|---|
| **Green** | `6c5c585` (workflow added) | [run #1](https://github.com/Narzar27/AAC/actions/runs/30698456650) | ✅ success — 49 passed |
| **Red (intentional)** | `c936e48` — one test assertion changed from 201 to 200 | [run #2](https://github.com/Narzar27/AAC/actions/runs/30698648690) | ❌ failure |
| **Green again** | `2fb9e8e` — assertion restored, workflow untouched | [run #3](https://github.com/Narzar27/AAC/actions/runs/30698673365) | ✅ success |

The red run failed for the intended reason: the job's step breakdown (via the
Actions API) shows `Set up job`, `checkout`, `setup-python`, and
`Install dependencies` all **success**, and `Run tests` **failure** — i.e. pytest
exited non-zero on `test_create_task_returns_201_with_server_fields`, the exact
test broken on purpose. The failure was in a test expectation only (production
code untouched), was confirmed locally before pushing, and the restore commit
changed nothing in the workflow itself — CI returned to green because the code
was fixed, not because the failure was hidden.
