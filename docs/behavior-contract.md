# Behavior Contract — Module 3 Frontend

The 8-item contract the board must satisfy before and after any refactor.
It is executable: `python -m tests.verify_frontend` drives every item in headless
Chromium against the live backend (plus the five modal flows). Run it with:

```bash
# terminal 1
venv\Scripts\python -m uvicorn app.main:app --port 8000
# terminal 2
venv\Scripts\python -m http.server 5500 --directory frontend
# terminal 3
venv\Scripts\python -m tests.verify_frontend
```

| # | Behavior | Pre-refactor | Post-refactor |
|---|----------|--------------|---------------|
| 1 | Three columns render (To Do / In Progress / Done) with counts | PASS | PASS |
| 2 | Cards sort High → Medium → Low, ties broken by lower id | PASS | PASS |
| 3 | Loading state shows while the fetch is pending | PASS | PASS |
| 4 | Empty columns show a clear placeholder | PASS | PASS |
| 5 | Backend unreachable → visible error state, not a blank board | PASS | PASS |
| 6 | Valid drag persists via PATCH /tasks/{id} | PASS | PASS |
| 7 | Rejected drag (422) reverts the card and shows the server message | PASS | PASS |
| 8 | Same-column drop sends no PATCH request | PASS | PASS |

Modal flows (also in the script): whitespace-only title blocks the request with a
visible error; create appears in the right column/priority slot; edit reorders or
moves the card; server 422 keeps the modal open with the message; Escape, Cancel,
X, and overlay click all dismiss and clear stale state.

## Refactor record

- **Checkpoint:** git commit before the refactor (repo initialized for this purpose).
- **Selected section:** render logic in `frontend/js/board.js` only — extracted an
  `el(tag, className, text, ...children)` helper to replace repeated
  `createElement` boilerplate in `buildColumn`/`buildCard`.
- **Diff red flags checked:** status strings, URLs/methods, class names, and
  data attributes all unchanged; `.trim()` validation and 422 handling untouched.
- **Verification:** all 14 contract checks re-ran green after the refactor, and the
  33-test backend suite still passes.
