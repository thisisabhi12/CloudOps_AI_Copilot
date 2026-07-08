"""
CloudOps AI Copilot — AI Provider Abstraction

Pluggable adapter pattern for multiple AI providers.
Supports Google Gemini, Anthropic Claude, and OpenAI GPT.
Each provider implements generate() for streaming and embed() for RAG.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the AI model.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            system_prompt: Optional system prompt for the conversation
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens in the response

        Yields:
            Text chunks as they arrive from the model
        """
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """
        Generate an embedding vector for the given text.

        Args:
            text: The text to embed

        Returns:
            A list of floats representing the embedding vector
        """
        ...


class GeminiProvider(AIProvider):
    """Google Gemini AI provider."""

    def __init__(self):
        import google.generativeai as genai

        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        genai.configure(api_key=settings.gemini_api_key)
        self._genai = genai
        self._model = genai.GenerativeModel("gemini-2.0-flash")
        self._embed_model = "models/text-embedding-004"
        logger.info("Gemini provider initialized")

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Generate streaming response using Gemini."""
        # Build Gemini-format messages
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})

        # Configure generation
        generation_config = self._genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        # Create model with system instruction if provided
        model = self._model
        if system_prompt:
            model = self._genai.GenerativeModel(
                "gemini-2.0-flash",
                system_instruction=system_prompt,
            )

        # Stream response
        response = await model.generate_content_async(
            gemini_messages,
            generation_config=generation_config,
            stream=True,
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def embed(self, text: str) -> list[float]:
        """Generate embedding using Gemini text-embedding-004."""
        result = self._genai.embed_content(
            model=self._embed_model,
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]


class ClaudeProvider(AIProvider):
    """Anthropic Claude AI provider."""

    def __init__(self):
        from anthropic import AsyncAnthropic

        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")

        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        logger.info("Claude provider initialized")

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Generate streaming response using Claude."""
        async with self._client.messages.stream(
            model="claude-sonnet-4-20250514",
            messages=messages,
            system=system_prompt or "",
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, text: str) -> list[float]:
        """
        Claude doesn't have a native embedding model.
        Falls back to a simple hash-based embedding for compatibility.
        In production, use a dedicated embedding service.
        """
        raise NotImplementedError(
            "Claude does not provide embeddings. "
            "Use Gemini or OpenAI for embedding generation."
        )


class OpenAIProvider(AIProvider):
    """OpenAI GPT AI provider."""

    def __init__(self):
        from openai import AsyncOpenAI

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        logger.info("OpenAI provider initialized")

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Generate streaming response using OpenAI GPT."""
        openai_messages = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})
        openai_messages.extend(messages)

        stream = await self._client.chat.completions.create(
            model="gpt-4o",
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, text: str) -> list[float]:
        """Generate embedding using OpenAI text-embedding-3-small."""
        response = await self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding


# ----- Provider Factory -----

# Cache instantiated providers to avoid re-initialization
_provider_cache: dict[str, AIProvider] = {}


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Factory function to get an AI provider instance.

    Args:
        provider_name: Provider name ("gemini", "claude", "openai").
                       Defaults to settings.default_ai_provider.

    Returns:
        An AIProvider instance.

    Raises:
        ValueError: If the provider is unknown or not configured.
    """
    name = (provider_name or settings.default_ai_provider).lower().strip()

    if name in _provider_cache:
        return _provider_cache[name]

    providers = {
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
    }

    if name not in providers:
        raise ValueError(
            f"Unknown AI provider: '{name}'. "
            f"Available: {list(providers.keys())}"
        )

    try:
        provider = providers[name]()
        _provider_cache[name] = provider
        return provider
    except ValueError as e:
        raise ValueError(f"Failed to initialize {name} provider: {e}")
