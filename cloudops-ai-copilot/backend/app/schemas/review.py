"""
CloudOps AI Copilot — Review Schemas

Pydantic models for code review request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ReviewType(str, Enum):
    """Types of IaC / config files that can be reviewed."""
    TERRAFORM = "terraform"
    DOCKERFILE = "dockerfile"
    CLOUDFORMATION = "cloudformation"
    KUBERNETES = "kubernetes"


class Severity(str, Enum):
    """Severity levels for review findings."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    BEST_PRACTICE = "best_practice"


# ----- Requests -----

class ReviewRequest(BaseModel):
    """Submit code for AI review."""
    code: str = Field(
        min_length=1,
        max_length=100000,
        description="The code/config content to review",
    )
    filename: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional filename for context (e.g., main.tf, Dockerfile)",
    )
    provider: Optional[str] = Field(
        default=None,
        description="AI provider to use (gemini, claude, openai)",
    )


class ArchitectureRequest(BaseModel):
    """Request AWS architecture advice."""
    description: str = Field(
        min_length=10,
        max_length=10000,
        description="Description of the system/architecture",
    )
    requirements: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Specific requirements or constraints",
    )
    provider: Optional[str] = Field(
        default=None,
        description="AI provider to use",
    )


# ----- Responses -----

class ReviewFinding(BaseModel):
    """A single finding from a code review."""
    severity: Severity
    title: str
    description: str
    line_range: Optional[str] = None
    suggestion: Optional[str] = None


class ReviewResponse(BaseModel):
    """Complete review response (used for non-streaming responses)."""
    review_type: ReviewType
    filename: Optional[str] = None
    summary: str
    findings: list[ReviewFinding]
    score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Overall score 0-100",
    )
    improved_code: Optional[str] = None
