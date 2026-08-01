# My AI Playbook — one page

*(Revised after the final project: the release check added one more proof of
the "evidence before acceptance" rule — my own Docker docs said "verified"
things that hadn't run yet until the runtime pass made them true.)*

## When I reach for AI first

Scaffolding a known pattern (the tags feature came out nearly right in one pass
because the due-dates feature had established the shape); generating test
suites against an explicit contract; repo-wide drift hunting (it found the
README teaching a broken install); first-pass code review for breadth; turning
messy evidence into structured docs.

## When I do not reach for AI first

Deciding scope or requirements (course rules like "Done is reopenable" came
from the brief, not the model — AI happily invented the opposite); security
conclusions (it claimed SQL injection in a repo with no SQL); anything where I
couldn't yet explain the last generated block I accepted — understanding debt
compounds faster than code debt.

## My non-negotiables

- Never paste: `.env` values, API keys/tokens/passwords, real customer names or
  records, unsanitized production logs.
- No AI diff is accepted unread, and never outside the task's scoped files.
- A test I haven't seen fail is not yet a test (Break Test rule).
- The backend rule never bends to make generated frontend code work.

## My review rules

Read the full diff → check scope (only intended files) → run the named
verification (pytest / behavior contract / live call) → for review comments,
reproduce the claim in the cited file before acting; label Useful/Noise/Wrong
and never "fix" a Wrong. For docs, spot-check claims against code — fluent is
not correct (two README lies survived three modules before the audit habit
caught them).

## What I am still figuring out

How to keep contract docs (README, CLAUDE.md) in sync without a human audit
each module; when a second AI pass reviewing the first is worth the tokens;
how team conventions for AI attribution should work outside a solo course repo.

## Decision Card

| Decision | My answer |
|---|---|
| New feature | Terminal agent (Claude Code) with a strict constrained prompt + the repo's pattern files attached; plan-only first if it spans >2 files. |
| Code review | AI first pass for breadth, then my own pass on the same diff; only verified comments become actions (Module 4: 2 of 6 AI comments were flat wrong). |
| Debugging | Paste the exact failing test + full error output into the agent — never a paraphrase; the ResponseValidationError root-cause in seconds proved the value of raw evidence. |
| Infrastructure | Agent drafts Dockerfile/CI, I inspect against a red-flag list (no `continue-on-error`, no `\|\| true`, pinned versions) and demand runtime proof — a green check is only trusted after an intentional red, and a Dockerfile only after the container answered `/health` and `whoami` (final project: 200 + `app`). |
| Never paste | `.env` contents, credentials/tokens/keys, customer PII, raw production logs. |
| One rule | **Evidence before acceptance** — every artifact (code, test, doc, review comment, security finding) is graded against something that actually ran, not against how plausible it sounds. |

*30-day check (due ~2026-08-31): re-read this page. Am I still following it?*
