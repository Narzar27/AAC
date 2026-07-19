# Task Tracker — Reviewed User Stories (Module 1, Part A)

Seven stories drafted with AI assistance, then reviewed against the Module 1 scope.
Corrections to the AI draft are documented at the bottom.

## Story 1 — Create a task

As a team member, I want to create a task so that I can track a piece of work.

**Acceptance criteria**
- Title is required; a missing, empty, or whitespace-only title returns 422 with a clear error message.
- Description is optional.
- Status defaults to `ToDo` and priority defaults to `Medium` when not provided.
- The created task is returned with a generated `id` and appears in the task list.

## Story 2 — View all tasks

As a team member, I want to view all tasks so that I can see the state of the board.

**Acceptance criteria**
- `GET /tasks` returns a list (possibly empty) in a consistent JSON shape.
- Every task includes `id`, `title`, `description`, `status`, `priority`, and `assignee`.

## Story 3 — Filter tasks

As a team member, I want to filter tasks by status and priority so that I can focus on relevant work.

**Acceptance criteria**
- Filtering by `status`, `priority`, or both returns only matching tasks.
- An invalid filter value (e.g. `status=Later`) returns 422, not an empty list, so typos are visible.
- No filters means all tasks are returned.

## Story 4 — Update task details

As a team member, I want to edit a task's title, description, priority, and assignee so that task information stays accurate.

**Acceptance criteria**
- Only the provided fields change; omitted fields keep their values.
- Validation rules from creation (non-empty title, allowed enum values) also apply on update.
- Updating a non-existent task returns 404.

## Story 5 — Move a task through statuses

As a team member, I want to change a task's status so that the board reflects real progress.

**Acceptance criteria** *(revised in Module 2 to match the lecture's transition matrix)*
- Valid statuses are exactly `ToDo`, `InProgress`, and `Done`.
- Allowed transitions: `ToDo → InProgress` (work starts), `InProgress → Done` (work finishes), `Done → InProgress` (a completed task can be reopened).
- All other transitions return 422 with the allowed transitions in the error detail — including `ToDo → Done` (cannot skip `InProgress`) and `Done → ToDo` (cannot revert to the beginning).
- Re-sending the current status is rejected with 422; no-op moves are not valid transitions.
- Updates that do not include a `status` field skip transition validation entirely.

## Story 6 — Delete a task

As a team member, I want to delete a task so that the board only shows relevant work.

**Acceptance criteria**
- Deleting an existing task returns 204 and removes it from the list.
- Deleting a non-existent id returns 404, not a generic 200.
- Deleting the same task twice returns 404 on the second call.

## Story 7 — Validate task data

As an API consumer, I want invalid task data rejected consistently so that I can rely on the data shape.

**Acceptance criteria**
- Title is stripped of surrounding whitespace before the emptiness check.
- `status` outside `ToDo | InProgress | Done` and `priority` outside `Low | Medium | High` return 422.
- Error responses use FastAPI's structured `detail` format naming the offending field.

---

## Documented corrections to the AI draft

1. **Status transitions (Story 5).** The draft allowed any status to move to any other, including `Done → ToDo`. Corrected to an explicit transition table. (Module 1 initially made `Done` terminal; Module 2's transition matrix revised this — `Done → InProgress` is a valid reopen, and same-status no-ops are rejected. Story 5 reflects the Module 2 rules.)
2. **Out-of-scope assumption removed.** The draft included a story about user accounts and "my tasks" per user. Removed — authentication and per-user task lists are explicitly excluded from the project scope.
3. **Silent-failure delete (Story 6).** The draft returned 200 for deleting a missing id. Corrected to 404 so clients can distinguish success from a no-op — this matches the "spot the flaw" exercise in the notes.
4. **Filter typo behavior (Story 3).** The draft returned an empty list for invalid filter values. Corrected to 422 so a typo doesn't silently look like "no tasks".
