# Governance Worksheet — Module 5.3

A retrospective of what actually crossed the AI boundary during Modules 1–5,
in both directions, with a risk level and reason per row.

## What I shared with AI

| Shared | Risk | Reason |
|---|---|---|
| The entire Task Tracker codebase (models, routes, storage, tests, frontend, Dockerfile, CI YAML) | **Low** | Course-only toy project, now deliberately public on GitHub; contains no secrets or real data. |
| Module lecture-note and brief PDFs | **Low** | Course materials distributed to students; no personal or proprietary content beyond the university's own docs. |
| pytest failure output, Playwright call logs, and stack traces during debugging | **Low** | Traces reference only toy code and local paths under my user folder; no tokens or real data — but path leakage is the category to watch on real projects. |
| My name and work email in git commit metadata (public repo) | **Medium** | Deliberate for course attribution, but it permanently ties a work identity to this public repo — on a client project this would need an explicit decision. |
| GitHub repo URL and Actions run metadata | **Low** | Public by design for submission. |
| Real customer data, credentials, `.env` values, tokens | **— (never shared)** | Nothing of this class existed in the project; the never-paste rule in `ai-usage.md` keeps it that way. |

## What I received from AI

| Received | Still understand it? | Notes |
|---|---|---|
| Backend: Pydantic models + validators, storage helpers, five routes, transition rules | Yes | Traced repeatedly through tests and Break Tests; the PATCH route is traced line-by-line below. |
| Test suites (49 pytest tests, verify_a, 19-check Playwright contract) | Yes | Trust earned through deliberate breakage — every important test has been proven to fail when its behavior breaks. |
| Frontend board/modal/api modules incl. drag-and-drop | Mostly | The DataTransfer drag-event flow is the piece I'd re-derive slowest; traced during Module 3 debugging. |
| Dockerfile, .dockerignore, CI workflow | Yes | Verified by inspection + CI runs; Docker runtime evidence still pending (see docker-security-log.md). |
| All course docs drafts (ADRs, logs, plans) | Yes | Rewritten/reviewed before commit; they document decisions I can defend. |

## Line-by-line trace of one accepted block

Block: the `patch_task` route in `app/main.py` — accepted in Module 2, edited in
Module 3, never previously traced line by line.

| Line | What it does / why it's needed / what breaks without it |
|---|---|
| `@app.patch("/tasks/{task_id}", response_model=TaskResponse, ...)` | Registers the route and forces every response through `TaskResponse` — without `response_model`, raw storage dicts (and any junk in them) would serialize straight to clients. |
| `def patch_task(task_id: int, payload: TaskUpdate):` | FastAPI converts/validates the path id (non-int → 422) and parses the body into `TaskUpdate`, whose `extra="forbid"` rejects unknown fields. Without the typed payload, unvalidated JSON reaches storage. |
| `task = storage.get_task_by_id(task_id)` | Fetches current state *first*; needed both for the 404 check and as the `current` side of transition validation. |
| `if task is None: raise HTTPException(404, ...)` | Missing id ends here — ordering guarantees a bad transition on a missing task is 404, not 422 (pinned by a test). |
| `if payload.status is not None:` | Transition rules run only when the client is actually changing status; without this, title-only edits would be rejected (the exact bug found in Module 3 when the modal sent unchanged status). |
| `try: validate_status_transition(task["status"], payload.status)` | Delegates the business rule to `business_rules.py`; checks the *pair*, not just enum validity. |
| `except InvalidStatusTransition as exc: raise HTTPException(422, str(exc))` | Converts the domain error into the API contract (422 + human-readable allowed transitions). Swallowing it would silently allow invalid moves. |
| `updates = payload.model_dump(exclude_unset=True)` | The core PATCH semantics: only fields the client actually sent. Without `exclude_unset`, every omitted field would overwrite stored values with `None`. |
| `return storage.update_task(task_id, updates)` | Applies the change and bumps `updated_at`; returns the record, which `response_model` re-validates on the way out. |

No line remains that I cannot explain.

## Pattern changes

Kept: strict prompts with negative constraints; evidence before acceptance;
Break Tests for any test I intend to trust. Stopped: accepting full payloads on
edit forms (send only changed fields); assuming a green run means the doc/README
still tells the truth. The binding rules live in [`ai-usage.md`](ai-usage.md).
