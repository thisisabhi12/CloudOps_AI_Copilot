"""
CloudOps AI Copilot — Auth API Routes

Endpoints for user registration, login, and profile retrieval.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    request: RegisterRequest,
    db: DbSession,
):
    """
    Register a new user account.

    Returns a JWT access token and user profile on success.
    Raises 409 if email or username already exists.
    """
    user = await register_user(db, request)
    token = create_access_token(
        user_id=str(user.id),
        role=user.role.value,
    )
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: DbSession,
):
    """
    Authenticate and receive a JWT access token.

    Raises 401 on invalid credentials.
    Raises 403 if account is deactivated.
    """
    user = await authenticate_user(db, request.email, request.password)
    token = create_access_token(
        user_id=str(user.id),
        role=user.role.value,
    )
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: CurrentUser):
    """
    Get the current authenticated user's profile.

    Requires a valid JWT Bearer token.
    """
    return UserResponse.model_validate(current_user)
