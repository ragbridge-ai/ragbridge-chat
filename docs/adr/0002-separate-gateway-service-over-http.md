# 2. The gateway is a separate Python service that reaches the core over HTTP only

Date: 2026-10-15

## Status

Accepted. See decision 15 in [the plan](https://github.com/ragbridge-ai/ragbridge/blob/main/docs/plans/chat-roadmap.md).

## Context

The core is an HTTP API for other applications, and its scope is deliberately narrow. A chat
product adds things it should not own: end-user sessions, conversation storage, per-tenant
bot rules, a browser-facing surface with its own security rules, and later calls to the host
application's own API. Putting them in the core would make every core user carry them.

## Decision

1. **The gateway is its own service in its own repository**, released and deployed
   separately from the core.
2. **It is written in Python with the core's stack:** FastAPI, async SQLAlchemy with psycopg,
   Alembic, pydantic-settings, `uv`, ruff, `mypy --strict` and pytest.
3. **It has its own PostgreSQL database**, with no pgvector: it holds conversations and
   tenant settings, never documents.
4. **It calls the core over HTTP with a core API key that requires an access scope**, so a
   bug in the gateway that forgets the user's groups fails with a `403` instead of searching
   everything.
5. **It never imports the core's code.** A test fails if any module under `src/` does.
6. **It states the oldest core it works with** (1.4.0, the first release with access groups
   and keys that require a scope), and its demo builds a released core from its tag.

## Alternatives considered

- **Add it to the core.** One deployment, but every core user pays for a feature they may not
  want, and a browser-facing surface sits next to the API that holds every tenant's data.
- **Another language for the gateway** (Node or Go). The widget is JavaScript either way,
  but a second backend stack doubles the tooling to maintain for a service that is mostly
  HTTP, a database and a few checks. The core's stack is known and already in use.
- **Share the core's database.** The gateway would depend on the core's schema, and the two
  could no longer be migrated or released independently.

## Consequences

- Two databases and two services to run, and a network hop on every question.
- The core's API is the contract. A change the gateway needs goes into the core first, is
  released, and only then is used here.
- The conversation history is the gateway's. The core stays free of sessions; it only gains
  an optional field to receive the history the gateway sends.
