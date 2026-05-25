FROM python:3.14-slim-trixie@sha256:c845af9399020c7e562969a13689e929074a10fd057acd1b1fad06a2fb068e97 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.16@sha256:440fd6477af86a2f1b38080c539f1672cd22acb1b1a47e321dba5158ab08864d /uv /uvx /bin/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
        libcrypt-dev \
        libpcre2-dev \
        libssl-dev && \
    rm -rf /var/lib/apt/lists/*

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

FROM python:3.14-slim-trixie@sha256:c845af9399020c7e562969a13689e929074a10fd057acd1b1fad06a2fb068e97 AS final

ARG PROJECT_COMMIT_HASH=local
ARG PROJECT_BUILD_DATE=

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        postgresql-client \
        gosu \
        libpcre2-8-0 && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROJECT_COMMIT_HASH=$PROJECT_COMMIT_HASH
ENV PROJECT_BUILD_DATE=$PROJECT_BUILD_DATE

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . /app

RUN git describe --tags --always > PROJECT_VERSION && \
    date --iso-8601=seconds > PROJECT_BUILD_DATE && \
    git rev-parse HEAD > PROJECT_COMMIT_HASH && \
    rm -rf .git

EXPOSE 3030

ENV PATH="/opt/venv/bin:/app/docker/remote/bin:${PATH}"

ENTRYPOINT ["/app/docker/remote/entrypoint.sh"]
CMD ["django"]
