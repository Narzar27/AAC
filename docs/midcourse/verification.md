# Verification — Mid-Course Project

All commands ran from the repo root on branch `mid-course-project`
(backend `venv\Scripts\python -m uvicorn app.main:app --port 8000`, frontend
`venv\Scripts\python -m http.server 5500 --directory frontend`).

## 1. Baseline (before any change)

| Check | Result |
|---|---|
| `pytest tests/ -q` | **33 passed** |
| `GET /health` on running app | **200** |
| `python -m tests.verify_frontend` (behavior contract) | **All 14 checks passed** |

## 2. Backend test results (after both features)

| Stage | Result |
|---|---|
| After Feature 1 (due dates): suite | **40 passed** (7 new) |
| After Feature 2 (tags): suite | **49 passed** (9 more new; 16 new total) |
| `python -m tests.verify_a` (Module 2 model checks) | **All 8 checks passed** |

New tests cover: valid/malformed due date, past-date-overdue, Done-never-overdue,
update + null-clears date, overdue filter true/false/invalid, tags trim/blank/
duplicate/limit 422s, replace tags, null tags 422, tags preserved on unrelated
PATCH, tag filter match/no-match/empty-param.

## 3. Manual browser checks

Performed through the executable contract (headless Chromium driving the real UI)
plus a visual screenshot review (`docs/midcourse/board.png`): due badge on dated
cards, red `Overdue · <date>` pill only on past-due non-Done tasks, tag chips,
"Overdue only" toggle narrowing the board to one card, tag filter narrowing to the
tagged card, "Clear filters" restoring all six cards, empty-column placeholders
preserved while filtered.

## 4. Behavior contract before/after refactor

| Point | Result |
|---|---|
| Before refactor (working checkpoint commit) | **49 pytest passed; all 19 contract checks passed** |
| Focused refactor | `storage.get_all_tasks` only: four sequential list-rebuild passes consolidated into a single-pass `matches()` predicate; signature, route, and behavior unchanged |
| After refactor | **49 pytest passed; all 19 contract checks passed** |

The contract grew from 14 to 19 checks (5 new checks for the two features); all
original 14 still pass, so Modules 1–3 behavior is unregressed.

## 5. Break Test evidence (two tests)

**Break Test 1 — overdue rule (Feature 1).** Removed the `status != Done` clause
from `models.is_overdue` → `test_done_task_with_past_due_date_is_not_overdue`
**failed** (`is_overdue` was `True` for a Done task). Restored the clause → full
suite green again.

**Break Test 2 — blank tag rule (Feature 2).** Disabled the empty-after-trim check
in `models._validate_tags` (`if False and not stripped:`) →
`test_create_task_with_blank_tag_returns_422` **failed** (got 201, expected 422).
Restored the check → full suite green again.

Both breaks were temporary, made exactly one test fail for the expected reason,
and were reverted before commit — proving the tests protect the rules they claim to.
