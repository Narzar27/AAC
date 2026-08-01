# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: **yes** (Python 3.14/FastAPI/Pydantic v2 stack, exact run/test/contract commands)
- Docs-first/read-first guardrail included: **yes** ("default posture: read-only analysis; required edits belong in docs/")
- Unexpected app/frontend edits rule included: **yes** ("any proposed change to app/, tests/, frontend/, Dockerfile, or CI … must be rejected or explicitly flagged")

No `app/` or `frontend/` files were changed in the final project — the diff is
docs and README only, which a grader can confirm with
`git diff mid-course-project..final-project --stat`.

## AI code review mini-log

Reviewed diff: the `final-project` branch changes (release evidence, Module 4
Docker-log update, README Final Project section).

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| "docs/module4/docker-security-log.md still says runtime evidence is 'not yet executed'; now that the container ran, the two evidence docs will contradict each other" | **Useful** | Real cross-doc inconsistency — exactly the drift the claim-vs-reality habit exists for | Verified and fixed: the Module 4 log now records the actual build//health/whoami outputs from 2026-08-01 |
| "The README Final Project section duplicates run commands that exist earlier in the README, creating drift risk" | **Useful** | True; two copies of a command can diverge silently | Accepted with a constraint: commands in the new section are pasted verbatim from the ones executed for the baseline, and the claim-vs-reality log covers them |
| "The env-var scan (`env` grep for KEY/TOKEN/SECRET) proves nothing — secrets could be baked into image files instead" | **Wrong** | It ignores the two adjacent checks in the same log: `ls /srv` shows only `app/` in the image, and `.dockerignore` excludes `.env*`/`.git`; the env scan is one of three complementary checks, not the whole argument | No change; misreading recorded |
| "Add screenshots of the passing runs to release-evidence.md" | **Noise** | The brief states text logs are enough and screenshots optional; screenshots add maintenance weight without adding verifiability | Skipped, reason recorded |

## AI security mini-review

Re-run of the Module 5 read-only review against the final branch (full version:
`docs/security-review.md`). No code changes resulted — read-only by design.

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| `description` and `assignee` accept unbounded strings while every neighboring field is capped | `app/models.py` lines 87, 90 | **Valid** | Repo-specific, inconsistent with the model's own validation posture; memory-growth risk | First post-course code change (bound to 2000/100); deliberately NOT fixed now — final project protects `app/` |
| Dependency versions unpinned in `requirements*.txt` | `requirements.txt`, `requirements-dev.txt` | **Valid** | Reproducibility/supply-chain drift between local, CI, and Docker | Backlog item 2; see "rejected output" below for why it was not done today |
| Possible SQL injection in task filtering | (no file — none exists) | **False Positive** | Storage is an in-memory dict; filters are list comprehensions in `app/storage.py`; there is no SQL anywhere | None — recorded as a pattern-matching failure |
| "All user input should be validated and sanitized" | (no file cited) | **Noise** | No field, file, or failure mode; the actionable versions of this are the Valid findings above | None |

## Manual security check

I inspected the built image from the inside rather than trusting the Dockerfile
read: `docker exec tt-dev ls /srv` shows only the `app` package (no tests, docs,
`.env`, or git metadata inside the image), `docker exec tt-dev env` has zero
matches for `KEY|TOKEN|SECRET|PASS`, and `whoami` returns `app`, not root. I
also re-confirmed the XSS posture from Module 5 by grepping the frontend for
`innerHTML`/`insertAdjacentHTML`: still zero hits — task fields render via
`textContent` only. Nothing new found; both checks matter because they verify
the *artifact* (running container, rendered DOM), not the source files AI read.

## One AI output I rejected or corrected

During the final release check, the review suggested fixing the two Valid
security findings immediately — pinning all dependency versions and adding
`max_length` to `description`/`assignee` — since the fixes are small. I refused
both for this branch: the brief explicitly protects `app/` and asks for no
non-essential changes, an unverified pin set could break CI/Docker on the exact
branch being graded, and a validation change on submission day would invalidate
the recorded baseline (49 passed). Both stay ranked in
`docs/security-review.md` as the first post-course changes. (The course-long
pattern of corrected AI output is logged in `docs/module4/review-log.md` and
`docs/midcourse/prompt-log.md` — e.g. the edit-modal diff that re-sent
unchanged arrays, corrected before it shipped.)

## Three AI usage rules

1. **Never paste:** `.env` values, API keys/tokens/passwords, real customer
   names or records, or unsanitized production logs into any AI tool.
2. **Always verify:** read the full diff, confirm it touches only the scoped
   files, and run the named check (`pytest tests/ -v`, the 19-check browser
   contract, or a live container/endpoint call) before accepting; a test is
   trusted only after it has been seen to fail (Break Test).
3. **Record AI contributions by:** disclosing them in the repo's docs (prompt
   logs, correction logs, review logs in `docs/`), per this repo's convention —
   and on a team repo, by recording prompt, accepted diff, and verification in
   the PR description.

## Ownership statement

I can run every command in this repo and explain what it does, from the uvicorn
invocation to the multi-stage Dockerfile and the CI workflow. The business
rules are ones I can defend line by line — the PATCH route is traced in
`docs/governance-worksheet.md` — and every test suite has been proven honest by
deliberately breaking the behavior it protects and watching it fail. AI drafted
a large share of the code and documents, but nothing was accepted unread: the
course logs record real corrections, rejected suggestions, and two
documentation lies that my own verification caught. The evidence in `docs/` is
reproducible by a grader from a clean clone, and I am comfortable submitting
this repository as work I own.
