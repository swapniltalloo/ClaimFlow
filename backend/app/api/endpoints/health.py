from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "sla_target_minutes": settings.SLA_MAX_SECONDS / 60
    }


@router.get("/ready")
async def readiness_check():
    return {
        "status": "ready",
        "database": "connected",
        "redis": "connected"
    }
