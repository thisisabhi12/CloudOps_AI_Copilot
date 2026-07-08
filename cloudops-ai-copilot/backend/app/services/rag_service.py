"""
CloudOps AI Copilot — RAG Service

Retrieval-Augmented Generation using pgvector for semantic search.
Embeds documents, stores them in PostgreSQL, and retrieves relevant
context for AI prompts.
"""

from typing import Optional
from uuid import UUID
import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk
from app.services.ai_provider import get_ai_provider

logger = logging.getLogger(__name__)


async def embed_and_store_chunk(
    db: AsyncSession,
    content: str,
    source: str,
    metadata: Optional[dict] = None,
    provider_name: Optional[str] = None,
) -> DocumentChunk:
    """
    Embed a text chunk and store it in the database.

    Args:
        db: Database session
        content: Text content to embed
        source: Source document identifier
        metadata: Optional metadata dict
        provider_name: AI provider for embedding (must support embed())

    Returns:
        The created DocumentChunk instance
    """
    # Use Gemini by default for embeddings (best embedding support)
    embed_provider = provider_name or "gemini"
    provider = get_ai_provider(embed_provider)

    embedding = await provider.embed(content)

    chunk = DocumentChunk(
        content=content,
        source=source,
        metadata_=metadata,
        embedding=embedding,
    )
    db.add(chunk)
    await db.flush()
    await db.refresh(chunk)
    logger.info(f"Stored document chunk from {source} ({len(content)} chars)")
    return chunk


async def search_similar_chunks(
    db: AsyncSession,
    query: str,
    top_k: int = 5,
    provider_name: Optional[str] = None,
) -> list[DocumentChunk]:
    """
    Search for document chunks semantically similar to the query.

    Uses pgvector's cosine distance for similarity search.

    Args:
        db: Database session
        query: Search query text
        top_k: Number of results to return
        provider_name: AI provider for embedding the query

    Returns:
        List of most similar DocumentChunk instances
    """
    # Embed the query
    embed_provider = provider_name or "gemini"
    provider = get_ai_provider(embed_provider)
    query_embedding = await provider.embed(query)

    # Use pgvector cosine distance operator (<=>)
    embedding_str = str(query_embedding)
    result = await db.execute(
        text(
            """
            SELECT id, source, content, metadata, embedding, created_at,
                   embedding <=> :query_embedding AS distance
            FROM document_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
            """
        ).bindparams(
            query_embedding=embedding_str,
            limit=top_k,
        )
    )
    rows = result.fetchall()

    # Convert to DocumentChunk objects
    chunks = []
    for row in rows:
        chunk = DocumentChunk(
            id=row.id,
            source=row.source,
            content=row.content,
            metadata_=row.metadata,
            embedding=row.embedding,
            created_at=row.created_at,
        )
        chunks.append(chunk)

    logger.info(f"Found {len(chunks)} similar chunks for query: {query[:50]}...")
    return chunks


def build_rag_context(chunks: list[DocumentChunk]) -> str:
    """
    Build a context string from retrieved document chunks.

    Args:
        chunks: List of relevant DocumentChunk instances

    Returns:
        Formatted context string for AI prompts
    """
    if not chunks:
        return ""

    context_parts = ["## Relevant Context from Knowledge Base\n"]
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"### Source {i}: {chunk.source}\n"
            f"{chunk.content}\n"
        )
    return "\n".join(context_parts)
