"""
CloudOps AI Copilot — Architecture Advisor Service

Generates AWS architecture recommendations with Mermaid diagrams.
"""

from typing import AsyncIterator, Optional
import logging

from app.services.ai_provider import get_ai_provider
from app.prompts.architecture_advisor import ARCHITECTURE_ADVISOR_PROMPT

logger = logging.getLogger(__name__)


async def advise_architecture(
    description: str,
    requirements: list[str],
    provider_name: Optional[str] = None,
) -> AsyncIterator[str]:
    """
    Generate architecture recommendations with Mermaid diagrams.

    Args:
        description: Description of the system/architecture
        requirements: List of specific requirements or constraints
        provider_name: AI provider to use

    Yields:
        Text chunks of the architecture advice as they stream
    """
    # Build user message
    user_message = f"## System Description\n{description}\n"

    if requirements:
        user_message += "\n## Requirements\n"
        for i, req in enumerate(requirements, 1):
            user_message += f"{i}. {req}\n"

    user_message += (
        "\nPlease provide a comprehensive architecture recommendation "
        "with a Mermaid diagram, cost estimates, and implementation roadmap."
    )

    messages = [{"role": "user", "content": user_message}]

    provider = get_ai_provider(provider_name)
    logger.info(f"Starting architecture advice with {provider.__class__.__name__}")

    async for chunk in provider.generate(
        messages=messages,
        system_prompt=ARCHITECTURE_ADVISOR_PROMPT,
        temperature=0.5,
        max_tokens=8192,
    ):
        yield chunk

    logger.info("Completed architecture advice")
