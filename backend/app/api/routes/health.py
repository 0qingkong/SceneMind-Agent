from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "scenemind-agent-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }
