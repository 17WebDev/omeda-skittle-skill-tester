# syntax=docker/dockerfile:1

# ---- Builder: resolve and install dependencies into a venv ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Bytecode-compile for faster cold starts; copy (not symlink) into the venv so
# it can be lifted into the runtime stage cleanly.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install third-party deps first, keyed only on the lockfiles, so this layer is
# cached and not invalidated by application code changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Now add the project source and install the package itself.
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---- Runtime: slim image with just the venv + source ----
FROM python:3.12-slim-bookworm AS runtime

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app /app

# Put the venv on PATH so `uvicorn` resolves without `uv run`.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser
EXPOSE 8000

# No --reload in the image; that's a dev-only convenience.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
