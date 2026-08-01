# Module 4 — Tool-Fit Reflection

**Copilot / inline autocomplete** earns its place at the line level. Writing the
Google-style docstrings and the repetitive test blocks this module is exactly its
territory: the pattern is established two functions up, and completion just has
to continue it. The verification burden is small — read the inserted lines —
which is why it is the one surface I will accept output from with the least
ceremony. It is the wrong tool the moment work crosses a file boundary: it could
not have caught that `requirements.txt` and the README disagreed, because it
never sees both at once.

**Cursor / IDE chat** was the right scope for Modules 2–3: file-level edits with
a visible diff, like building one endpoint at a time against attached models, or
the selected-section refactor of the board's render logic. Its sweet spot is
"change this function, show me the diff" — big enough to be useful, small enough
that the diff is genuinely reviewable. It gets awkward for terminal-heavy loops;
proving CI red/green from an editor sidebar is fighting the tool.

**Claude Code / terminal agent** carried Module 4 because every artifact here is
repo-level: a workflow file plus three pushed commits plus reading Actions logs;
a Dockerfile that has to agree with `.dockerignore`, `requirements.txt`, and the
README simultaneously; docs audited against code across five files. That scope
is also exactly why it needs the strictest habits — CLAUDE.md so it stops being
a smart outsider, plan-only prompts before wide edits, and diff-plus-evidence
before anything is accepted. The review triage made the risk concrete: the same
agent that correctly found real doc drift also produced two confident, wrong
mechanism claims (#5 and #6 in the review log).

No single winner: the scope of the task picks the tool, and the tool's scope
sets the strictness of the verification. Line → read the insertion; file → read
the diff and run it; repo → demand evidence (CI runs, logs, claim-vs-reality
checks) before believing anything.
