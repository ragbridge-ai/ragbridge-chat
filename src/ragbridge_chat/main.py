"""Application entry point: builds the FastAPI app."""

from importlib.metadata import version

from fastapi import FastAPI

from ragbridge_chat.api.health import router as health_router


def create_app() -> FastAPI:
    """Build and configure a FastAPI application instance.

    A factory instead of a module-level app built at import time keeps app
    creation explicit and lets tests build a fresh, isolated app each time.
    """
    app = FastAPI(title="ragbridge-chat", version=version("ragbridge-chat"))
    app.include_router(health_router)
    return app


app = create_app()
