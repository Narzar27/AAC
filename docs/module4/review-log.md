# Module 4.5 — AI Review Triage Log

Reviewed diff: branch `module-4` against `mid-course-project` — a real diff
containing the CI workflow, Dockerfile, `.dockerignore`, the requirements split,
docstrings, README rewrite, and CLAUDE.md. Every AI review comment below was
checked against the actual files before being bucketed.

| # | AI review comment (summarized) | Bucket | Evidence / justification | Action |
|---|---|---|---|---|
| 1 | README's test instructions still tell users to `pip install -r requirements.txt`, but pytest/httpx2 moved to `requirements-dev.txt` — tests break on a clean checkout | **Useful** | Confirmed: the setup section predated the split. A new-teammate walkthrough of the README would fail at `pytest` | Fixed — setup section now installs `requirements-dev.txt` and explains the split |
| 2 | `.dockerignore` excludes `frontend/`, so the image serves the API only — if the README's Docker section doesn't say so, users will expect the board at `:8000` | **Useful** | Confirmed: the container has no static file mounting; only FastAPI routes exist | Fixed — README and Dockerfile header state the image is backend-only |
| 3 | Consider pinning the base image by digest (`python:3.14-slim@sha256:…`) for supply-chain reproducibility | **Noise** | Technically valid, but the course requires an explicit slim tag, not digest pinning; adds maintenance burden with no course-relevant benefit | Skipped, reason recorded |
| 4 | CI could add `actions/cache` for pip to speed up runs | **Noise** | True but the install step takes seconds for four packages; caching adds YAML complexity for negligible gain | Skipped, reason recorded |
| 5 | Excluding `tests/` in `.dockerignore` will break CI because pytest won't find the test files | **Wrong** | CI checks out the repo with `actions/checkout` (git), which does not read `.dockerignore`; that file affects only the `docker build` context. Run #1/#3 being green with `tests/` excluded proves it | No change — misunderstanding recorded |
| 6 | `USER app` before `EXPOSE 8000` may prevent binding the port as non-root | **Wrong** | Port 8000 is not a privileged port (<1024), and `EXPOSE` is documentation metadata, not a bind operation; non-root uvicorn binds 8000 without issue | No change — misunderstanding recorded |

## Human review vs AI review

My own pass over the same diff caught #1 independently (it is the kind of drift a
human following the README notices immediately) and additionally questioned
whether `CLAUDE.md` should be excluded from the Docker image (it is — via
`.dockerignore`). The AI pass was better at breadth: it read every file in the
diff and surfaced #2, which I had not written down. It was worst exactly where
the lecture predicts: #5 and #6 are fluent, confident, and wrong in ways that
would each have cost real time to "fix".

## Personal AI-review rule

I will use AI review as a broad first pass over the whole diff, but no comment
becomes an action item until I have opened the cited file and reproduced the
claim myself — and a comment that names a mechanism (like `.dockerignore`
affecting CI) gets verified at the mechanism level, not by plausibility.
