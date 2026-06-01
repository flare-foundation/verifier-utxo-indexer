<!-- LOGO -->

<div align="center">
  <a href="https://flare.network/" target="blank">
    <img src="https://content.flare.network/Flare-2.svg" width="300" alt="Flare Logo" />
  </a>
  <br />
  Indexes UTXO chains (Bitcoin, Dogecoin) for FDC attestation verification
  <br />
  <a href="#verifier-utxo-indexer">About</a>
  ·
  <a href="CONTRIBUTING.md">Contributing</a>
  ·
  <a href="SECURITY.md">Security</a>
  ·
  <a href="CHANGELOG.md">Changelog</a>
</div>

# Verifier UTXO Indexer

Indexes UTXO-based chains (Bitcoin, Dogecoin) and exposes a verification API
used by FDC (Flare Data Connector) attestation providers.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full dev environment setup.

Quick start:

```bash
cp .env.example .env
# fill in SOURCE_NAME, NODE_RPC_URL, AUTH_USERNAME, AUTH_PASSWORD
docker compose build
docker compose up -d
```

If you have `SERVER_PROXY_PORT` set to `8000` in your `.env` file, the API is
available at <http://localhost:8000>.

## Deployment

Create a `.env` file and complete it with the necessary information for the
target source chain.

```bash
docker compose pull
docker compose up -d
```
