# Architecture (Strategy A — minimal context)

*Run with minimal context: "write a one-page architecture doc for this FastAPI
task tracker." Kept verbatim as the experiment artifact; inaccuracies are
annotated in the comparison inside `architecture.md`.*

The application is a FastAPI service exposing a REST API for task management,
following the typical layered layout: request models validate input, a routing
layer maps HTTP verbs to CRUD operations, and a persistence layer stores tasks.
Endpoints follow REST conventions (`GET/POST /tasks`, `GET/PATCH/DELETE
/tasks/{id}`) with Pydantic handling validation errors as HTTP 422.

Data is likely persisted in a lightweight store such as SQLite or a JSON file
⚠️, giving durability between restarts ⚠️. Business rules are typically
enforced in a service layer between routes and storage ⚠️. The frontend is a
single-page interface that consumes the API via fetch/AJAX, and tests use
FastAPI's TestClient. Configuration follows twelve-factor conventions with
environment variables controlling ports and origins ⚠️.

Deployment is containerized with Docker and validated by a CI pipeline that
runs the test suite on each push.

*⚠️ = invented or generic claims — wrong for this repo (no persistence, no
service layer, no env-based config); see the comparison log.*
