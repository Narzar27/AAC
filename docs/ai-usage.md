# AI Usage Rules — Task Tracker

Concrete rules distilled from Modules 1–5. The test for each rule: a teammate
can read it and know whether a specific behavior violates it.

## Never paste

1. Never paste `.env` files or values, API keys, tokens, passwords, or private
   certificates into any AI tool — including "just to ask what it does."
2. Never paste real customer names, emails, or records; reproduce bugs with
   synthetic data first, then share the synthetic version.
3. Never paste production logs or incident traces without first stripping
   hostnames, internal URLs, user identifiers, and secrets.
4. Committing identity metadata (name/email) to a public repo is a deliberate
   decision, made once per repo — not a default.

## Always verify

5. Before accepting any AI diff: read every changed file in the diff, confirm
   the change touches only what the task scoped, and run the named verification
   (`pytest tests/ -v`, `python -m tests.verify_frontend`, or the manual check).
6. A generated test is trusted only after a Break Test: break the behavior,
   watch the test fail for that reason, restore, watch it pass.
7. Documentation claims about status codes, commands, or behavior get checked
   against the code or a live run before commit (claim-vs-reality habit —
   two real doc lies were caught this way in Module 4).
8. AI review comments become action items only after I reproduce the claim in
   the cited file; "Wrong" comments get recorded, not fixed.
9. For security or correctness questions, require file citations; an answer
   without a file path is a hypothesis, not a finding.

## Recording AI contributions

10. AI-assisted work in this repo is disclosed in the course docs (prompt logs,
    correction logs, reflections in `docs/`), not in commit trailers — that is
    this repo's convention; on a team repo I would follow the team's convention
    instead, recording prompt, accepted diff, and verification in the PR.
11. Non-obvious decisions get a decision note (`docs/decisions/`) at the time
    they are made; "why" evaporates within a module if not written down.
