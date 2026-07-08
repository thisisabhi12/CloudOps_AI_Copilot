"""
CloudOps AI Copilot — Chat API Routes

Endpoints for AI chat with streaming responses and session management.
"""

import json
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sse_starlette.sse import EventSourceResponse

from app.api.deps import CurrentUser, DbSession
from app.schemas.chat import (
    ChatRequest,
    ChatSessionResponse,
    ChatSessionDetailResponse,
    ChatSessionListResponse,
    ChatMessageResponse,
)
from app.services.chat_service import (
    chat_stream,
    get_user_sessions,
    get_session_with_messages,
    delete_session,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("")
async def send_message(
    request: ChatRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Send a message to the AI assistant and receive a streaming response.

    Returns a Server-Sent Events (SSE) stream. Each event contains:
    - type: "chunk" (text chunk), "session" (session info), "done" (completion), "error"
    - data: The content of the event
    """
    async def event_generator():
        try:
            session_id, stream = await chat_stream(
                db=db,
                user=current_user,
                message=request.message,
                session_id=request.session_id,
                provider_name=request.provider,
            )

            # Send session ID first
            yield {
                "event": "session",
                "data": json.dumps({"session_id": str(session_id)}),
            }

            # Stream AI response chunks
            async for chunk in stream:
                yield {
                    "event": "chunk",
                    "data": json.dumps({"content": chunk}),
                }

            # Signal completion
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


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    List the current user's chat sessions.
    Returns sessions ordered by most recently updated.
    """
    sessions, total = await get_user_sessions(db, current_user, limit, offset)
    return ChatSessionListResponse(
        sessions=[ChatSessionResponse.model_validate(s) for s in sessions],
        total=total,
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
async def get_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get a specific chat session with all its messages.
    """
    session = await get_session_with_messages(db, current_user, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    return ChatSessionDetailResponse.model_validate(session)


@router.delete("/sessions/{session_id}", status_code=204)
async def remove_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Delete a chat session and all its messages.
    """
    deleted = await delete_session(db, current_user, session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
