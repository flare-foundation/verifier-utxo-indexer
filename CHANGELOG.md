# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# \[[v1.1.0](https://github.com/flare-foundation/verifier-utxo-indexer/tree/v1.1.0)\] - UPCOMING

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

### Fixed

- doge indexer no longer hangs forever on `Queue.join()` when a worker thread fails (e.g. node RPC errors exhausting retries); the failure is now raised from `process_block` so the process exits and can be restarted

# \[[v1.0.2](https://github.com/flare-foundation/verifier-utxo-indexer/tree/v1.0.2)\] - 2025-02-17

- started keeping changelog
