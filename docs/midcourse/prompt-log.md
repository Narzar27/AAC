# Prompt Log — Mid-Course Project

Meaningful prompts per feature, with what the AI returned and what was accepted,
edited, or rejected. The assistant used was Claude Code working directly in the
repository (see reflection.md for the tool breakdown).

## Feature 1 — Due dates + overdue filter

### Prompt 1.1 — weak prompt, then the rewrite

**Weak version (submitted first, output reviewed but not applied):**

> Add due dates to tasks.

The draft added a *required* `due_date` (breaking every existing test and client),
rejected past dates on create, and computed "overdue" in the frontend with
`new Date()` comparisons.

**Strong rewrite (applied):**

> In app/models.py add an optional `due_date: date | None = None` to TaskCreate,
> TaskUpdate, and TaskResponse (Pydantic v2, ISO YYYY-MM-DD, malformed input must
> 422). On TaskUpdate an explicit null CLEARS the date — unlike title, where null
> is an error. Past dates are allowed on create. Do not add new endpoints, do not
> touch the transition rules, do not compute overdue in the frontend.

**Outcome:** accepted after inspection — checked that Pydantic's `date` parsing
produces the 422 (no hand-rolled date parsing), and that `exclude_unset` still
distinguishes "omitted" from "null".

### Prompt 1.2 — decision prompt before code (where does overdue live?)

> List options for computing "overdue" with trade-offs. Do not write code yet.

Returned three options: frontend-only (JS date comparison), backend computed field,
or a stored boolean updated on write. **Rejected** frontend-only (browser clock vs
server clock can disagree; backend owns business rules) and the stored boolean
(goes stale at midnight without a write). **Accepted** the computed field:
`is_overdue` on TaskResponse plus the same predicate behind a `GET /tasks?overdue=`
filter — one function, `models.is_overdue`, used by both.

### Prompt 1.3 — tests

> Write pytest tests for due dates using the existing fixture pattern: valid date
> echo, malformed date 422, past date -> is_overdue true, Done task with past date
> NOT overdue, update + clear via null, overdue filter true/false, invalid filter
> value 422.

Returned 7 tests; accepted unchanged. Break Test performed on the Done-exclusion
rule (see verification.md).

### Prompt 1.4 — frontend integration

> Add a due-date input to the modal, a due/overdue badge on cards (read
> `is_overdue` from the API — do not recompute), and an "Overdue only" toggle in a
> new filter bar. Preserve all existing behavior-contract items.

**Edited before accepting:** the draft sent `overdue=false` whenever the checkbox
was unchecked, which would have *filtered out* overdue tasks in the default view.
Fixed so the parameter is only sent when the toggle is on.

## Feature 2 — Tags / labels

### Prompt 2.1 — constrained model prompt

> Add `tags: list[str]` to the task models. Rules: trim each tag; empty-after-trim,
> longer than 30 chars, more than 10 tags, or duplicates all return 422. Do NOT
> lowercase-normalize, do NOT silently dedupe, do NOT create a Tag entity or new
> endpoints. On TaskUpdate, tags replaces the whole list; explicit null is a 422
> ("send [] to clear").

Accepted. The negative constraints exist because the first exploratory answer
proposed a normalized `Tag` model with its own CRUD routes and a `GET /tags`
autocomplete endpoint — rejected as overbuild for in-memory storage (recorded in
the mini-ADR).

### Prompt 2.2 — tests

> One test per validation rule plus: filter by tag returns only matches, unknown
> tag returns 200 [], empty tag query param 422, and tags preserved after an
> unrelated title-only PATCH.

Returned 9 tests; accepted. Break Test performed on the blank-tag rule.

### Prompt 2.3 — frontend integration (and the bug review caught)

> Add a comma-separated tags input to the modal (parse -> trimmed list, drop empty
> entries client-side), tag chips on cards, and a tag filter input in the filter
> bar (debounced). Edit mode must keep sending only changed fields.

**Edited before accepting:** the changed-fields diff from Module 3 compares with
`!==`, and two arrays are never `===` — so an untouched tags list would have been
re-sent on every edit (harmless today, but it defeats the only-changed-fields
contract and would mask future backend rules). Added an array-aware `valuesEqual`
and verified the fix in the browser contract run.
