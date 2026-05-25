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

ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv sync --locked

FROM python:3.14-slim-trixie@sha256:c845af9399020c7e562969a13689e929074a10fd057acd1b1fad06a2fb068e97 AS final

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        netcat-traditional \
        gosu \
        libpcre2-8-0 && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . /app

EXPOSE 8000

ENV PATH="/opt/venv/bin:/app/docker/local/bin:${PATH}"

ENTRYPOINT ["/app/docker/local/entrypoint.sh"]
CMD ["django"]
