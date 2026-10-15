"""Health check endpoints, used by monitoring and container orchestrators."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health() -> dict[str, str]:
    """Report that the process is running (liveness). No database check."""
    return {"status": "ok"}
