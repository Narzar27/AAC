# Debugging Log — Module 3

Four-line format per the module: bug/failure, evidence, AI diagnosis, decision.

## Entry 1 — PATCH with explicit null title returns 500, not 422

1. **Bug:** New edge-case test `test_patch_null_title_returns_422` failed — sending `{"title": null}` crashed the response.
2. **Evidence:** pytest traceback ending in `fastapi.exceptions.ResponseValidationError: 1 validation error` — `TaskUpdate` accepted `None` (valid for `str | None`), storage saved `title=None`, and `TaskResponse` (title: str) blew up serializing the response.
3. **AI diagnosis:** The `TaskUpdate` title validator returned `None` unchanged, treating explicit null like "field omitted" — but `exclude_unset` already distinguishes those; a *provided* null is a client error.
4. **Decision:** Accepted as a cause fix — the validator now raises on explicit `None` (→ 422), and the test assertion stayed at 422. Weakening the test to expect 500 would have been symptom acceptance.

## Entry 2 — "Hidden" modal overlay blocks every click on the page

1. **Bug:** First contract run timed out clicking `#new-task-btn` even though the modal had never been opened.
2. **Evidence:** Playwright call log: `<div hidden id="modal-overlay">…</div> intercepts pointer events` — retried for 30s.
3. **AI diagnosis:** The author CSS `display: flex` on `.modal-overlay` overrides the `hidden` attribute's UA-stylesheet `display: none`, so the overlay was rendered (and covering the viewport) despite `hidden`.
4. **Decision:** Accepted cause fix: added a `.modal-overlay[hidden] { display: none; }` rule. Rejected the alternative of removing `hidden` logic from JS — the attribute is the right state carrier; the CSS just has to respect it.

## Entry 3 — Editing only the priority gets rejected as an invalid transition

1. **Bug:** Contract run: after changing a task's priority in the edit modal and saving, the modal stayed open instead of closing.
2. **Evidence:** PATCH returned 422 with `Invalid status transition: ToDo -> ToDo` — the form sent the full payload including the *unchanged* status, which the backend correctly rejects as a same-status move.
3. **AI diagnosis:** Edit mode built the payload from all form fields instead of diffing against the task being edited; PATCH is a partial update and should carry only changed fields.
4. **Decision:** Accepted cause fix in `modal.js`: edit mode now sends only changed fields (and skips the request entirely when nothing changed). Rejected the symptom fix of relaxing the backend's same-status rule — the backend rule is the Module 2 contract.

## Entry 4 — Rejected drag shows no error to the user

1. **Bug:** Contract run: dragging a Done card to To Do reverted correctly but the promised error message never became visible.
2. **Evidence:** `wait_for_selector("#board-message.is-error")` timed out; reading the code path showed `showMessage(error)` followed immediately by `refreshBoard()`, which overwrites the message with "Loading tasks…" and then clears it.
3. **AI diagnosis:** Ordering bug — the board refresh stomps the just-shown error, so the rejection flashes for milliseconds at most.
4. **Decision:** Accepted cause fix: on failure, await the refresh *first*, then show the error (auto-cleared after 6s). Rejected suppressing the refresh — the revert to server truth is required by contract item 7.

## Break Test evidence (backend, Part 6)

- Temporarily added `(InProgress, ToDo)` to `VALID_TRANSITIONS` →
  `test_patch_inprogress_back_to_todo_returns_422_with_message` failed (200 ≠ 422). Restored the rule → suite green (33 passed).

## Tool/workflow comparison (brief)

Browser-based chat (Modules 1–2 style) was fine for planning and isolated files;
editor/agent-style AI with the real repo attached caught cross-file issues
(payload shape vs backend rule) that a detached chat would have guessed at. The
biggest win this module was making verification executable: the behavior contract
found four real bugs that "it looks right" review missed.
