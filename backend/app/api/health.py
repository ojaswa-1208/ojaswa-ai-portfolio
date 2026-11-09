
from fastapi import APIRouter, Request, Response

from app.config import settings
from app.core.rate_limit import limiter


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
@limiter.limit(settings.RATE_LIMIT)
async def health_check(
    request: Request,
    response: Response,
):
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "application": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
    }


@router.get("/live")
async def liveness_check():
    return {
        "success": True,
        "status": "alive",
    }


@router.get("/ready")
async def readiness_check():
    return {
        "success": True,
        "status": "ready",
    }
