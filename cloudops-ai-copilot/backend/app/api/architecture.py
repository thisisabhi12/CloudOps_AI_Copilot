"""
CloudOps AI Copilot — Architecture Advisor API Routes

Endpoint for AWS architecture recommendations with Mermaid diagrams.
"""

import json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.api.deps import CurrentUser
from app.schemas.review import ArchitectureRequest
from app.services.architecture_service import advise_architecture

router = APIRouter(prefix="/architecture", tags=["Architecture Advisor"])


@router.post("/advise")
async def get_architecture_advice(
    request: ArchitectureRequest,
    current_user: CurrentUser,
):
    """
    Get AWS architecture recommendations based on system description.

    Returns a Server-Sent Events (SSE) stream containing:
    - Architecture overview and recommendations
    - Mermaid diagram code for visualization
    - Cost estimates and optimization suggestions
    - Implementation roadmap

    Each event contains:
    - type: "chunk" (text chunk), "done" (completion), "error"
    - data: The content of the event
    """
    async def event_generator():
        try:
            async for chunk in advise_architecture(
                description=request.description,
                requirements=request.requirements,
                provider_name=request.provider,
            ):
                yield {
                    "event": "chunk",
                    "data": json.dumps({"content": chunk}),
                }

            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"}),
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())
