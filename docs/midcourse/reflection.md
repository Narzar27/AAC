# Reflection — Mid-Course Project

The main tool for this project was Claude Code, an agentic assistant working
directly inside the repository — a step up in autonomy from the browser chat of
Module 1 and the editor assistant of Module 3. It handled planning drafts (user
stories, the mini-ADR), the model/storage/route changes, the frontend integration,
and test generation. Playwright in headless Chromium was the second essential tool:
the behavior contract from Module 3 was extended to 19 checks so that "verified in
the app" means a machine drove the real board, not that the board looked right.
pytest remained the backend safety net, growing from 33 to 49 tests.

The moment AI clearly helped was scaffolding symmetry. Once the due-date feature
established the pattern — field in three models, predicate in one place, query
parameter, storage filter, test block — the tags feature came out almost entirely
correct on the first pass because the prompt could point at the pattern instead of
describing everything from scratch. That whole feature, tests included, took a
fraction of the time the first one did.

The moment it slowed me down was the weak due-date prompt. The draft made
`due_date` required, banned past dates, and computed overdue in the browser —
three plausible-sounding decisions that would have broken every existing test,
made it impossible to record already-late work, and split a business rule across
two clocks. Reviewing and rewriting that prompt cost more time than the strong
prompt would have cost up front, which is the course's point about specifications.

The place review changed the result was the edit-modal diff. The generated tags
integration reused the Module 3 changed-fields comparison, which uses `!==` — and
two arrays are never strictly equal in JavaScript, so an untouched tag list would
have been silently re-sent on every edit. Nothing failed today; the backend has no
rule against re-sending tags. But the same latent pattern is exactly what produced
the Module 3 bug where re-sending an unchanged status hit the 422 same-status
rule. Catching it required actually reading the diff against the old code rather
than trusting a green run — the clearest example this project of owning the code
the AI drafted.
