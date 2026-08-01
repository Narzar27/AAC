# Multi-stage build: dependencies are resolved in a builder stage; the runtime
# stage gets only the installed packages and the application code.
# The container runs the backend API only — the static frontend is served
# separately in local dev and is not part of this image.

FROM python:3.14-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

FROM python:3.14-slim

WORKDIR /srv
COPY --from=builder /install /usr/local
COPY app/ ./app/

# Run as a non-root user; nothing in /srv needs to be writable at runtime.
RUN useradd --create-home app
USER app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
