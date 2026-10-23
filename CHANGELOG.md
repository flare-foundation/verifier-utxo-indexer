# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# \[[v1.1.2](https://github.com/flare-foundation/verifier-utxo-indexer/tree/v1.1.2)\] - 2026-10-23

### Fixed

- the doge indexer no longer hangs when a worker thread fails, for example after node RPC errors exhaust the retries. The process exits so it can be restarted.

### Security

- node RPC connections reject TLS certificates issued under the eight compromised eMudhra (emSign) intermediate CA keys.

# \[[v1.1.1](https://github.com/flare-foundation/verifier-utxo-indexer/tree/v1.1.1)\] - 2026-06-11

### Fixed

- doge indexer workers close their database connections.

# \[[v1.1.0](https://github.com/flare-foundation/verifier-utxo-indexer/tree/v1.1.0)\] - 2026-06-01

### Changed

- bumped python from 3.11 to 3.14
- migrated dependency management to uv (`pyproject.toml` + `uv.lock`)
- migrated test runner from Django/unittest to pytest
- switched WSGI server from uWSGI to gunicorn, exposed port changed from 3030 to 8000
- restructured Dockerfile to multistage build, runs as non-root user (uid 10001)
- serve static files via whitenoise

### Added

- structured JSON logging via `LOG_FORMAT=json`
- `LOG_LEVEL` env var to control root logger level
- `DJANGO_AUTO_MIGRATE` env var to opt out of auto-migration at container start
- `GUNICORN_FLAGS` env var to override default gunicorn flags
- github release workflow triggered on `v*` tags
- `CONTRIBUTING.md`, `SECURITY.md`, `CODEOWNERS`

# \[[v1.0.2](https://github.com/flare-foundation/verifier-utxo-indexer/tree/v1.0.2)\] - 2025-02-17

- started keeping changelog
