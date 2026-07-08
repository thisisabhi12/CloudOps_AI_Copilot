"""
CloudOps AI Copilot — Review Engine Service

Orchestrates AI-powered code reviews for Terraform, Dockerfile,
CloudFormation, and Kubernetes YAML files.
"""

from typing import AsyncIterator, Optional
import logging

from app.services.ai_provider import get_ai_provider
from app.prompts.terraform_review import TERRAFORM_REVIEW_PROMPT
from app.prompts.dockerfile_review import DOCKERFILE_REVIEW_PROMPT
from app.prompts.cloudformation_review import CLOUDFORMATION_REVIEW_PROMPT
from app.prompts.kubernetes_review import KUBERNETES_REVIEW_PROMPT

logger = logging.getLogger(__name__)

# Map review types to their system prompts
REVIEW_PROMPTS = {
    "terraform": TERRAFORM_REVIEW_PROMPT,
    "dockerfile": DOCKERFILE_REVIEW_PROMPT,
    "cloudformation": CLOUDFORMATION_REVIEW_PROMPT,
    "kubernetes": KUBERNETES_REVIEW_PROMPT,
}


async def review_code(
    review_type: str,
    code: str,
    filename: Optional[str] = None,
    provider_name: Optional[str] = None,
) -> AsyncIterator[str]:
    """
    Run an AI-powered code review.

    Args:
        review_type: Type of review (terraform, dockerfile, cloudformation, kubernetes)
        code: The code/configuration content to review
        filename: Optional filename for additional context
        provider_name: AI provider to use (defaults to server config)

    Yields:
        Text chunks of the review as they stream from the AI
    """
    system_prompt = REVIEW_PROMPTS.get(review_type)
    if not system_prompt:
        raise ValueError(f"Unknown review type: {review_type}")

    # Build user message with context
    user_message = f"Please review the following {review_type} code"
    if filename:
        user_message += f" (file: `{filename}`)"
    user_message += f":\n\n```\n{code}\n```"

    messages = [{"role": "user", "content": user_message}]

    # Get AI provider and stream the review
    provider = get_ai_provider(provider_name)
    logger.info(f"Starting {review_type} review with {provider.__class__.__name__}")

    async for chunk in provider.generate(
        messages=messages,
        system_prompt=system_prompt,
        temperature=0.3,  # Lower temperature for more consistent reviews
        max_tokens=8192,  # Reviews can be long
    ):
        yield chunk

    logger.info(f"Completed {review_type} review")
