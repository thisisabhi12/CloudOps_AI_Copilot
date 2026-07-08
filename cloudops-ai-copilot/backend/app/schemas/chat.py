"""
CloudOps AI Copilot — Chat Schemas

Pydantic models for chat request/response validation.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.models.chat import SessionType, MessageRole


# ----- Requests -----

class ChatRequest(BaseModel):
    """Send a message to the AI assistant."""
    message: str = Field(
        min_length=1,
        max_length=50000,
        description="The user's message to the AI",
    )
    session_id: Optional[UUID] = Field(
        default=None,
        description="Existing session ID to continue a conversation",
    )
    provider: Optional[str] = Field(
        default=None,
        description="AI provider to use (gemini, claude, openai). Defaults to server config.",
    )


# ----- Responses -----

class ChatMessageResponse(BaseModel):
    """A single chat message."""
    id: UUID
    role: MessageRole
    content: str
    metadata_: Optional[dict] = Field(default=None, alias="metadata_")
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class ChatSessionResponse(BaseModel):
    """A chat session summary (for listing)."""
    id: UUID
    title: str
    session_type: SessionType
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionDetailResponse(BaseModel):
    """A chat session with its messages."""
    id: UUID
    title: str
    session_type: SessionType
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse]

    model_config = {"from_attributes": True}


class ChatSessionListResponse(BaseModel):
    """Paginated list of chat sessions."""
    sessions: list[ChatSessionResponse]
    total: int
