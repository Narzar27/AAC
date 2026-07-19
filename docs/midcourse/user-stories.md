# Mid-Course Project — User Stories

Selected features: **(1) Due dates + overdue filter**, **(2) Tags / labels**.
Stories were drafted with AI support and reviewed; corrected AI assumptions are
marked per feature at the bottom of each section.

## Feature 1 — Due dates + overdue filter

### Story 1.1 — Set a due date on a task

As a team member, I want to give a task an optional due date so that time-sensitive
work is visible.

**Acceptance criteria**
- `due_date` is optional on create and edit; ISO format `YYYY-MM-DD`.
- An invalid date (e.g. `"next week"`, `2026-13-45`) returns 422.
- A past due date is accepted on create (importing already-late work is legitimate).
- The due date appears on the task card.

### Story 1.2 — Clear a due date

As a team member, I want to remove a task's due date so that a descoped task stops
showing a deadline.

**Acceptance criteria**
- Sending `"due_date": null` on PATCH clears the date (unlike `title`, null is a
  meaningful value here — omitting the field means "no change").
- The card no longer shows a date after clearing.

### Story 1.3 — See which tasks are overdue

As a team member, I want overdue tasks visually flagged so that late work stands out.

**Acceptance criteria**
- A task is overdue when `due_date` is strictly before today **and** status is not
  `Done` — completed tasks are never overdue.
- The API returns a computed `is_overdue` field; the card shows a red "Overdue" pill
  when it is true.

### Story 1.4 — Filter to overdue tasks

As a team member, I want to filter the board to overdue tasks so that I can triage
late work.

**Acceptance criteria**
- `GET /tasks?overdue=true` returns only overdue tasks; `overdue=false` returns only
  non-overdue tasks; omitting the param returns everything.
- A non-boolean value (`overdue=maybe`) returns 422.
- The board has an "Overdue only" toggle; empty columns keep their placeholders.

**Corrected AI assumptions (Feature 1):** the draft computed overdue in the frontend
by comparing dates in JavaScript — rejected, because two clocks (browser vs server)
can disagree and the backend owns business rules; the API now returns `is_overdue`.
The draft also rejected past due dates on create ("due date must be in the future"),
which would make it impossible to record already-late work — removed.

## Feature 2 — Tags / labels

### Story 2.1 — Tag a task

As a team member, I want to add tags to a task so that work can be grouped by topic.

**Acceptance criteria**
- `tags` is an optional list of strings; defaults to an empty list.
- Each tag is trimmed; a tag that is empty after trimming returns 422.
- Limits: at most 10 tags per task, each at most 30 characters; violations return 422.
- Tags render as chips on the card.

### Story 2.2 — Edit tags

As a team member, I want to change a task's tags so that labels stay accurate.

**Acceptance criteria**
- PATCH with a `tags` list replaces the whole list (no merge semantics).
- Validation rules from creation apply.
- An unrelated update (e.g. title only) leaves tags untouched.

### Story 2.3 — Filter by tag

As a team member, I want to filter the board by a tag so that I can focus on one
topic.

**Acceptance criteria**
- `GET /tasks?tag=frontend` returns only tasks whose tags include exactly `frontend`.
- An empty tag value (`tag=`) returns 422.
- The board has a tag filter input; it combines with the overdue toggle (AND).
- No matches returns 200 with `[]`, and the columns show empty placeholders.

**Corrected AI assumptions (Feature 2):** the draft normalized all tags to lowercase
and deduplicated silently — rejected as hidden data mutation; tags are stored as
typed (trimmed only) and duplicates are rejected with a 422 so the client learns the
rule. The draft also proposed a `GET /tags` endpoint for autocomplete — out of scope
for a two-feature brief.
