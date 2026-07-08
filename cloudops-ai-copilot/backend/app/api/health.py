"""
CloudOps AI Copilot — Health Check Endpoint

Provides system health status including database connectivity
and AI provider availability.
"""

from fastapi import APIRouter
from app.config import settings
from app.database import check_db_connection

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    System health check endpoint.
    Returns application status, version, database connectivity,
    and configured AI provider.
    """
    db_connected = await check_db_connection()

    # Check which AI providers have API keys configured
    providers_configured = []
    if settings.gemini_api_key:
        providers_configured.append("gemini")
    if settings.anthropic_api_key:
        providers_configured.append("claude")
    if settings.openai_api_key:
        providers_configured.append("openai")

    return {
        "status": "healthy" if db_connected else "degraded",
        "version": settings.app_version,
        "environment": settings.app_env,
        "database": {
            "connected": db_connected,
        },
        "ai": {
            "default_provider": settings.default_ai_provider,
            "providers_configured": providers_configured,
        },
    }
