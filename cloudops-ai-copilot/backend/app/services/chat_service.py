"""
CloudOps AI Copilot — Chat Service

Orchestrates AI chat with streaming responses and history persistence.
"""

from typing import AsyncIterator, Optional
from uuid import UUID
import logging

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatSession, ChatMessage, SessionType, MessageRole
from app.models.user import User
from app.services.ai_provider import get_ai_provider

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """You are CloudOps AI Copilot, an expert DevOps and cloud infrastructure assistant.

You specialize in:
- AWS services and architecture (EC2, ECS, Lambda, RDS, S3, CloudFront, etc.)
- Infrastructure as Code (Terraform, CloudFormation, Pulumi)
- Containerization (Docker, Kubernetes, ECS)
- CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI)
- Monitoring and observability (CloudWatch, Prometheus, Grafana, Datadog)
- Security best practices (IAM, secrets management, network security)
- Cost optimization and performance tuning
- SRE practices (SLOs, SLIs, incident response)

Guidelines:
- Provide specific, actionable answers with code examples when relevant
- Reference official documentation and best practices
- Use code blocks with proper syntax highlighting
- When discussing architecture, suggest Mermaid diagrams
- Prioritize security and reliability in your recommendations
- Be concise but thorough
"""


async def get_or_create_session(
    db: AsyncSession,
    user: User,
    session_id: Optional[UUID] = None,
    session_type: SessionType = SessionType.CHAT,
) -> ChatSession:
    """
    Get an existing chat session or create a new one.

    Args:
        db: Database session
        user: The authenticated user
        session_id: Optional existing session ID
        session_type: Type of session to create

    Returns:
        A ChatSession instance
    """
    if session_id:
        result = await db.execute(
            select(ChatSession)
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == user.id,
            )
        )
        session = result.scalar_one_or_none()
        if session:
            return session

    # Create a new session
    session = ChatSession(
        user_id=user.id,
        title="New Chat",
        session_type=session_type,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    logger.info(f"Created new chat session {session.id} for user {user.username}")
    return session


async def generate_session_title(
    message: str,
    provider_name: Optional[str] = None,
) -> str:
    """Generate a concise title for a chat session based on the first message."""
    try:
        provider = get_ai_provider(provider_name)
        title_parts = []
        async for chunk in provider.generate(
            messages=[{"role": "user", "content": message}],
            system_prompt=(
                "Generate a concise title (max 6 words) for a chat that starts with "
                "the following message. Return ONLY the title, no quotes or punctuation."
            ),
            temperature=0.5,
            max_tokens=20,
        ):
            title_parts.append(chunk)
        title = "".join(title_parts).strip()[:100]
        return title if title else "New Chat"
    except Exception as e:
        logger.warning(f"Failed to generate session title: {e}")
        # Fallback: use first 50 chars of message
        return message[:50].strip() + ("..." if len(message) > 50 else "")


async def chat_stream(
    db: AsyncSession,
    user: User,
    message: str,
    session_id: Optional[UUID] = None,
    provider_name: Optional[str] = None,
) -> tuple[UUID, AsyncIterator[str]]:
    """
    Process a chat message and stream the AI response.

    Args:
        db: Database session
        user: The authenticated user
        message: The user's message
        session_id: Optional existing session ID
        provider_name: AI provider to use

    Returns:
        Tuple of (session_id, async iterator of response chunks)
    """
    # Get or create session
    session = await get_or_create_session(db, user, session_id)

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content=message,
    )
    db.add(user_msg)
    await db.flush()

    # Load conversation history for context
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    history = result.scalars().all()

    # Build messages for AI
    messages = [
        {"role": msg.role.value, "content": msg.content}
        for msg in history
        if msg.role in (MessageRole.USER, MessageRole.ASSISTANT)
    ]

    # Stream response and collect for saving
    provider = get_ai_provider(provider_name)
    response_parts: list[str] = []

    async def stream_and_save():
        async for chunk in provider.generate(
            messages=messages,
            system_prompt=CHAT_SYSTEM_PROMPT,
        ):
            response_parts.append(chunk)
            yield chunk

        # Save assistant response after streaming completes
        full_response = "".join(response_parts)
        assistant_msg = ChatMessage(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=full_response,
        )
        db.add(assistant_msg)

        # Generate title for new sessions (first message)
        if len(history) <= 1:  # Only the user message we just added
            session.title = await generate_session_title(message, provider_name)

        await db.commit()
        logger.info(
            f"Chat response saved to session {session.id} "
            f"({len(full_response)} chars)"
        )

    return session.id, stream_and_save()


async def get_user_sessions(
    db: AsyncSession,
    user: User,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[ChatSession], int]:
    """Get paginated list of chat sessions for a user."""
    # Count total
    count_result = await db.execute(
        select(func.count(ChatSession.id))
        .where(ChatSession.user_id == user.id)
    )
    total = count_result.scalar_one()

    # Fetch sessions
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user.id)
        .order_by(desc(ChatSession.updated_at))
        .limit(limit)
        .offset(offset)
    )
    sessions = result.scalars().all()

    return list(sessions), total


async def get_session_with_messages(
    db: AsyncSession,
    user: User,
    session_id: UUID,
) -> ChatSession | None:
    """Get a chat session with all its messages."""
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(
            ChatSession.id == session_id,
            ChatSession.user_id == user.id,
        )
    )
    return result.scalar_one_or_none()


async def delete_session(
    db: AsyncSession,
    user: User,
    session_id: UUID,
) -> bool:
    """Delete a chat session and all its messages."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        return False
    await db.delete(session)
    await db.flush()
    return True
