# ragbridge-chat

The chat gateway for [ragbridge](https://github.com/ragbridge-ai/ragbridge): conversations
for end users, answered from a tenant's own documents, and an embeddable widget for any
website.

> **Status: under construction.** This is the skeleton: a gateway that starts and reports its
> health, its database, CI, and a demo stack. There are no tenants, tokens or chat yet. The
> plan, decision by decision and step by step, is in the core repository:
> [docs/plans/chat-roadmap.md](https://github.com/ragbridge-ai/ragbridge/blob/main/docs/plans/chat-roadmap.md).

## How it fits together

```
end user's browser ── widget (iframe served by the gateway)
                          │  short-lived session token
                          ▼
                    ragbridge-chat  ── core API key ──>  ragbridge (retrieval, answers)
```

The host application signs a token for a logged-in user; the gateway verifies it and asks the
core a question limited to that user's access groups. It needs **ragbridge 1.4.0 or later**
(access groups and API keys that require an access scope). The gateway talks to the core over
HTTP only and never imports its code.

## Try the demo stack

You need Docker and [Ollama](https://ollama.com) with `nomic-embed-text` and `llama3.2`
pulled (the core uses them, as in its own quick start).

```bash
docker compose up --build
```

| URL | What it is |
|---|---|
| http://localhost:8090 | The demo site: a public shop, and an intranet as an `hr` user and as an `engineering` user |
| http://localhost:8080/health/ready | The gateway, with its database check |
| http://localhost:8001/health | The core |

The core is built from its repository at the release tag named in `docker-compose.yml`. To try
another version, set `CORE_REF`, for example `CORE_REF=main docker compose up --build`.

## Development

You need Python 3.12 and [uv](https://docs.astral.sh/uv/), and a PostgreSQL server for the
tests. The suite creates and migrates its own `<name>_test` database on it and never touches
another:

```bash
docker run -d --name ragbridge-chat-postgres -p 5433:5432 \
  -e POSTGRES_USER=ragbridge_chat -e POSTGRES_PASSWORD=ragbridge_chat \
  -e POSTGRES_DB=ragbridge_chat postgres:17
cp .env.example .env
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check . && uv run mypy
```

## Documentation

- [Architecture decisions](docs/adr/) for this repository.
- [The plan](https://github.com/ragbridge-ai/ragbridge/blob/main/docs/plans/chat-roadmap.md), in the core repository.
- [AGENTS.md](AGENTS.md) for contributors, human or automated.

## License

MIT, see [LICENSE](LICENSE).
