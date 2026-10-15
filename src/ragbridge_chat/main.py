"""Application entry point: builds the FastAPI app."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from importlib.metadata import version

from fastapi import FastAPI

from ragbridge_chat.api.health import router as health_router
from ragbridge_chat.config import get_settings
from ragbridge_chat.db.session import create_engine, create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create the database engine on startup, dispose it on shutdown.

    The engine is created here, not at import time, so importing the app module never
    opens a network connection.
    """
    engine = create_engine(get_settings())
    app.state.session_factory = create_session_factory(engine)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    """Build and configure a FastAPI application instance.

    A factory instead of a module-level app built at import time keeps app
    creation explicit and lets tests build a fresh, isolated app each time.
    """
    app = FastAPI(title="ragbridge-chat", version=version("ragbridge-chat"), lifespan=lifespan)
    app.include_router(health_router)
    return app


app = create_app()
