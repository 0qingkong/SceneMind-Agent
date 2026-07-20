from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "scenemind-agent-api",
        "version": "0.2.0",
        "analyzer": "mock-v0.2",
        "timestamp": datetime.now(UTC).isoformat(),
    }
