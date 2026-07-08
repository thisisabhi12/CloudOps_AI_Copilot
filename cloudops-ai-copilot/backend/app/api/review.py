"""
CloudOps AI Copilot — Review API Routes

Endpoints for AI-powered code review of Terraform, Dockerfile,
CloudFormation, and Kubernetes YAML.
"""

import json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.api.deps import CurrentUser
from app.schemas.review import ReviewRequest
from app.services.review_engine import review_code

router = APIRouter(prefix="/review", tags=["Code Review"])


def _create_review_endpoint(review_type: str):
    """Factory to create review endpoints for each IaC type."""

    async def review_endpoint(
        request: ReviewRequest,
        current_user: CurrentUser,
    ):
        f"""
        Submit {review_type} code for AI-powered review.

        Returns a Server-Sent Events (SSE) stream with the review results.
        Each event contains:
        - type: "chunk" (review text), "done" (completion), "error"
        - data: The content of the event
        """
        async def event_generator():
            try:
                async for chunk in review_code(
                    review_type=review_type,
                    code=request.code,
                    filename=request.filename,
                    provider_name=request.provider,
                ):
                    yield {
                        "event": "chunk",
                        "data": json.dumps({"content": chunk}),
                    }

                yield {
                    "event": "done",
                    "data": json.dumps({
                        "status": "complete",
                        "review_type": review_type,
                    }),
                }

            except Exception as e:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)}),
                }

        return EventSourceResponse(event_generator())

    return review_endpoint


# ----- Register endpoints -----

router.add_api_route(
    "/terraform",
    _create_review_endpoint("terraform"),
    methods=["POST"],
    summary="Review Terraform code",
    description="Analyze Terraform configuration for security, best practices, reliability, cost, and code quality.",
)

router.add_api_route(
    "/dockerfile",
    _create_review_endpoint("dockerfile"),
    methods=["POST"],
    summary="Review Dockerfile",
    description="Analyze Dockerfile for security, image optimization, build efficiency, and best practices.",
)

router.add_api_route(
    "/cloudformation",
    _create_review_endpoint("cloudformation"),
    methods=["POST"],
    summary="Review CloudFormation template",
    description="Analyze CloudFormation template (JSON/YAML) for security, template quality, and reliability.",
)

router.add_api_route(
    "/kubernetes",
    _create_review_endpoint("kubernetes"),
    methods=["POST"],
    summary="Review Kubernetes YAML",
    description="Analyze Kubernetes manifest(s) for security, resource management, reliability, and best practices.",
)
