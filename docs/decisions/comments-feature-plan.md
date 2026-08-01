# Comments Feature — Plan Review (Module 5.4, plan only, NOT implemented)

Two plans for a task-comments feature were produced and compared: a generic one
(no repo access) and a repo-grounded one (agent required to read `app/models.py`,
`app/main.py`, `app/storage.py`, `tests/test_tasks.py`, `frontend/js/modal.js`,
`AGENTS.md` first). The grounded plan was then critiqued section by section as
tech lead. **No code was written; `app/` is untouched.**

## What the generic plan proposed (and assumed wrong)

A reasonable blog-post plan: SQLAlchemy `Comment` model with a foreign key and
Alembic migration, UUID primary keys, a `CommentService` class, JWT-scoped
"author = current user", React component for the thread, and pagination.
Five of those six assumptions are wrong for this repo: there is no database, no
migrations, no service classes, no auth (author is a plain field here), and no
React. Only the endpoint shapes survived contact with the codebase.

## Repo-grounded plan, with tech-lead critique labels

| # | Plan section | Label | Notes |
|---|---|---|---|
| 1 | **Model:** `CommentCreate` (author 1–100, body 1–2000, both trimmed non-blank via the existing `_validate_title`-style validators, `extra="forbid"`) and `CommentResponse` (`id: int`, `task_id`, `author`, `body`, `created_at` UTC) in `app/models.py` | **Right** | Matches project conventions: integer ids like tasks (the lecture's UUID suggestion is not project-consistent), server-managed fields kept out of input models. |
| 2 | **Storage:** per-task comment dict in `app/storage.py` with `add_comment(task_id, payload)`, `get_comments(task_id)`, `delete_comment(task_id, comment_id)`, wired into `_reset()`; deleting a task deletes its comments | **Right** | Extends the in-memory pattern instead of inventing persistence; the task-delete cascade is the detail generic plans miss. |
| 3 | **API:** `POST /tasks/{id}/comments` → 201, `GET /tasks/{id}/comments` → 200 (possibly `[]`), `DELETE /tasks/{id}/comments/{comment_id}` → 204 empty body; 404 when the task (or comment) doesn't exist, checked before validation | **Right** | Status codes and 404-before-422 ordering copy the established contract. |
| 4 | **Tests** as named by the plan | **Missing** | The list covered create/list/delete happy paths and blank-body 422 but omitted: comment on a *nonexistent task* → 404, author/body over-length → 422, comments removed when the parent task is deleted, and a Break Test target. All four are required by this repo's testing bar. |
| 5 | **Sequencing:** the draft put the modal-UI comments section second, right after the model | **Needs-Resequencing** | House order is model → storage → routes → tests → frontend → docs; every module was built that way and the 422-handling in the modal depends on the API contract being final. |
| 6 | **Frontend:** comments section inside the edit modal (list + add form + delete), count badge on cards, errors shown via the existing `field-error` pattern, only changed data sent | **Right** | Correctly reuses `api.js` request helper and modal error handling rather than new fetch code. |
| 7 | **Docs:** README API table rows + CLAUDE.md/AGENTS.md business-rule updates | **Missing** | The plan forgot `tests/verify_frontend.py` — the behavior contract would need 2–3 new checks, and this repo treats the contract as part of "done." |

## Three-line comparison

1. The generic plan was fluent and 80% inapplicable — five structural assumptions
   (DB, migrations, UUIDs, auth, React) don't exist in this repo.
2. The grounded plan needed repo reading to get ids, storage shape, status codes,
   and error ordering right — and still required a tech-lead pass, which caught
   missing edge-case tests and a sequencing error.
3. A generic plan is fine for brainstorming scope on a greenfield idea; the
   moment a plan names files, it must be grounded or it is confidently wrong.
