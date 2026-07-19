# ADR-001 — Task Tracker Architecture (Module 1, Part B)

**Status:** Accepted — 2026-07-11

For Module 1 the Task Tracker is a single FastAPI application with a layered folder
structure (`app/api/routes` for endpoints, `app/models` for Pydantic schemas,
`app/storage` for persistence, `app/core` for configuration) and, for now, no real
database — storage will start in-memory/JSON-file when CRUD arrives in later modules.
I chose this because it scores well on all four course criteria: it is simple enough to
hold in my head and maintain alone; the layer separation makes tests easy to write
(the health tests already run against the app object with no server or database);
it runs locally with two commands (`pip install -r requirements.txt` and
`uvicorn app.main:app --reload`); and Python, FastAPI, and pytest are tools I already
know or can pick up quickly from the Swagger-first workflow. I rejected two assumptions
the AI offered: PostgreSQL with SQLAlchemy (a production database adds migration and
setup complexity that Module 1 explicitly excludes) and Docker with docker-compose
(deployment packaging hides the ask–inspect–run–test–refine loop the module is trying
to teach). The main risk I would revisit if the project grew is the storage choice:
file/in-memory storage has no concurrency safety or query capability, so at the point
where multiple users or filtering performance matter, I would migrate the `app/storage`
layer to SQLite/SQLModel — the layered structure is there precisely so that swap stays
contained.
