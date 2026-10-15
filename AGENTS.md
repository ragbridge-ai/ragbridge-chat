# AGENTS.md — ragbridge-chat

This file gives coding agents and automated contributors the context they need to work on
this repository. Read it before making any change.

## 1. What this project is

`ragbridge-chat` is the chat gateway for [ragbridge](https://github.com/ragbridge-ai/ragbridge):
a backend that holds conversations and answers end users' questions from a ragbridge
tenant's documents, and the embeddable widget that any website can add.

- GitHub organization: `ragbridge-ai`
- This repo: `ragbridge-ai/ragbridge-chat` (the gateway and the widget)
- The core: `ragbridge-ai/ragbridge` (documents, retrieval, answers). The gateway calls it over
  HTTP and **never imports its code**; a test enforces it.
- License: MIT

**The plan lives in the core repository**, not here:
[docs/plans/chat-roadmap.md](https://github.com/ragbridge-ai/ragbridge/blob/main/docs/plans/chat-roadmap.md). It holds the decisions this
repository implements, each phase's steps, and each step's detail and outcome. Read the
decisions and the step you are working on before changing anything, and do not work from
memory of them. This repository links to the plan; it does not copy it.

## 2. Tech stack

| Area | Tool |
|---|---|
| Language | Python 3.12 |
| Package and environment manager | `uv` (never plain `pip` or `requirements.txt`) |
| Web framework | FastAPI + Uvicorn |
| Settings and validation | Pydantic, pydantic-settings |
| Database | PostgreSQL (its own; no pgvector) |
| ORM and migrations | SQLAlchemy 2.x (async, psycopg) + Alembic |
| Lint and format | ruff |
| Type checking | mypy (strict) |
| Tests | pytest, httpx |
| CI | GitHub Actions |
| Local infrastructure | Docker Compose |

Only add a tool when the current step needs it. Every important choice gets a short
Architecture Decision Record in `docs/adr/`.

## 3. Project structure

```
ragbridge-chat/
├── .github/workflows/ci.yml
├── demo/site/app.py          # the stand-in host application for the demo stack
├── docs/adr/
├── migrations/               # Alembic
├── src/ragbridge_chat/
│   ├── main.py               # create_app()
│   ├── config.py             # settings with pydantic-settings
│   ├── api/                  # endpoints
│   └── db/                   # base, session
├── tests/
├── Dockerfile  docker-compose.yml  alembic.ini
├── pyproject.toml  uv.lock  .env.example
└── AGENTS.md  README.md  LICENSE
```

## 4. Coding rules

- Use the src layout. All application code lives in `src/ragbridge_chat/`.
- Use the application factory pattern (`create_app()`), so tests can build a fresh app.
- Full type hints everywhere. Code must pass `mypy --strict`.
- Code must pass `ruff check` and `ruff format --check`.
- Every new endpoint or feature needs tests. The suite uses a real PostgreSQL database and
  fakes for every model call; CI uses no network.
- Configuration comes from environment variables through pydantic-settings. Never hard-code
  secrets. Keep `.env.example` up to date; never commit `.env`.
- Never import the core's code (`ragbridge`). Call it over HTTP.
- Use Conventional Commits for commit messages (`feat:`, `fix:`, `chore:`, `docs:`,
  `test:`, `ci:`).

## 5. Commands

```bash
uv sync                      # install dependencies
uv run pytest                # run tests (needs the gateway's PostgreSQL, see the README)
uv run ruff check .          # lint
uv run ruff format .         # format
uv run mypy                  # type check
uv run alembic upgrade head  # apply migrations
docker compose up --build    # the demo stack
```

## 6. How to work on tasks

1. Work on one step at a time, as the plan numbers them. Do not jump ahead.
2. Before writing code, read the step's detail in the plan. If the code contradicts a
   decision there, stop and say so; do not work around it.
3. After changes, run tests, ruff and mypy, and make sure they pass.
4. Never commit to `main` directly. Work on one feature branch per step. Never merge, push to
   `main`, force-push, create tags, publish packages, or change repository settings.
