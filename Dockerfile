#checkov:skip=CKV_DOCKER_2: Health check is not required
FROM python:3.14-slim-trixie@sha256:fbecd461fc72d21b2143c6eaba25143738079154a6d0ea3da3aec724f50eed4a AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.16@sha256:440fd6477af86a2f1b38080c539f1672cd22acb1b1a47e321dba5158ab08864d /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./

ARG DEV=false
# avoid symlinks that break when copying between stages
ENV UV_LINK_MODE=copy
# install outside /app so local volume mounts don't shadow the venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN if [ "$DEV" = "true" ]; then \
      uv sync --locked; \
    else \
      uv sync --locked --no-dev; \
    fi

FROM python:3.14-slim-trixie@sha256:fbecd461fc72d21b2143c6eaba25143738079154a6d0ea3da3aec724f50eed4a AS final

ARG DEV=false
ARG PROJECT_COMMIT_HASH=local
ARG PROJECT_BUILD_DATE=

# hadolint ignore=DL3008
RUN if [ "$DEV" = "true" ]; then \
      apt-get update && \
      apt-get install -y --no-install-recommends gosu && \
      rm -rf /var/lib/apt/lists/*; \
    fi

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROJECT_COMMIT_HASH=$PROJECT_COMMIT_HASH
ENV PROJECT_BUILD_DATE=$PROJECT_BUILD_DATE

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . /app

ENV PATH="/opt/venv/bin:/app/docker/bin:${PATH}"

RUN DJANGO_SETTINGS_MODULE=project.settings.common \
    addgroup --gid 10001 app && \
    adduser --uid 10001 --ingroup app --disabled-password app && \
    mkdir -p /appdata/static && \
    python manage.py collectstatic --no-input && \
    chown -R 10001:10001 /app /appdata

EXPOSE 8000

USER app

CMD ["django-gunicorn"]
