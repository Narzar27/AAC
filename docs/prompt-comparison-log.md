# Prompt Comparison Log — Vague vs Strict (Module 2, Part 2.2)

The module's prompt-quality experiment for `POST /tasks`: submit a vague prompt,
review what it misses (without applying it), then submit the strict version.

## Vague prompt

> Write a POST /tasks endpoint using FastAPI.

**What the draft missed (reviewed, not applied):**
- Returned **200** instead of **201** because no status code was specified.
- Created a **new `FastAPI()` instance** instead of using the existing `app`, so the route would never be served alongside `/health`.
- **Invented its own inline `Task` model** with plain-string `status`/`priority` instead of importing `TaskCreate`/`TaskResponse` and the enums from `app/models.py`.
- Stored tasks in a **local list inside the route file**, ignoring `app/storage.py`, so GET endpoints built later would not see created tasks.
- No `response_model`, so server-managed fields and validation of the output shape were uncontrolled.

## Strict prompt

> Attached: `app/main.py`, `app/models.py`, `app/storage.py`.
> Add a `POST /tasks` route to the existing `app` in `app/main.py`.
> Requirements: accept `TaskCreate`, call `storage.add_task`, return 201 with
> `response_model=TaskResponse`. Do NOT create a new FastAPI instance, do NOT
> define new models, do NOT add auth/logging/persistence, do NOT touch other routes.
> Return only the route function.

**What changed:**
- Correct status code (201), correct models, correct storage helper — verifiable against exact expectations instead of plausible-looking guesses.
- The DO-NOT list prevented scope creep (no auth, no database, no new app).
- Attaching the real files eliminated hallucinated helpers like `storage.find_one`.

## Lesson

The vague draft was syntactically fine and would have "worked" in isolation — which
is exactly the trap. Strict prompts with file context produce code that can be
*verified*, not just code that looks right.
