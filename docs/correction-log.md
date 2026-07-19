# Correction Log — Module 2

AI output that was inspected and corrected before (or instead of) applying it.

1. **Structure mismatch with Module 1 (Part 2.1).** Module 1 scaffolded `app/models/`
   and `app/storage/` as packages; Module 2 specifies flat `app/models.py` and
   `app/storage.py`. Replaced the placeholder packages with modules so imports match
   the course prompts exactly (`from app.models import TaskCreate`).

2. **Requirements changed between modules (Part 2.3).** The Module 1 user stories said
   `Done` is terminal and same-status updates are idempotent (200). The Module 2
   transition matrix supersedes both: `Done -> InProgress` is now a valid reopen, and
   same-status moves return 422. Updated Story 5 in `docs/user-stories.md` instead of
   letting the docs and the code drift apart.

3. **Same-status transitions in the generated set (Part 2.3).** The first draft of
   `VALID_TRANSITIONS` included `(status, status)` pairs "for idempotency". Removed —
   the module's rule set explicitly rejects no-op moves, and the six-call matrix
   (`200, 200, 422, 200, 422, 200`) fails otherwise.

4. **404-before-422 ordering in PATCH (Part 2.3).** An early draft validated the
   status transition before checking the task existed, so patching a missing id with
   a bad transition returned 422 instead of 404. Reordered: fetch task, 404 if
   missing, then validate the transition only when `status` is present in the payload.

5. **DELETE response body (Part 2.2).** Draft returned `{"message": "deleted"}` with
   status 204. A 204 must have an empty body; the route now returns nothing and the
   test asserts `response.content == b""` rather than calling `.json()`.

6. **`min_length=1` is not blank-title validation (Part 2.1).** Field constraints
   alone would accept `"   "`. Kept `min_length`/`max_length` for length bounds but
   added a `@field_validator` that strips whitespace before the emptiness check, per
   verification A checks 1–2.
