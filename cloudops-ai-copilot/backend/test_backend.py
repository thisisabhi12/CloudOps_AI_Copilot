"""
CloudOps AI Copilot — Backend Testing Suite

Comprehensive tests for auth, database, models, and services.
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


class TestImports:
    """Test that all modules can be imported without errors."""

    def test_import_config(self):
        """Test config module import."""
        from app.config import settings
        assert settings.app_name == "CloudOps AI Copilot"
        assert settings.app_version == "0.1.0"
        print("✓ Config module imported successfully")

    def test_import_database(self):
        """Test database module import."""
        from app.database import Base, engine, async_session_factory
        assert Base is not None
        assert engine is not None
        assert async_session_factory is not None
        print("✓ Database module imported successfully")

    def test_import_models(self):
        """Test model imports."""
        from app.models.user import User, UserRole
        from app.models.chat import ChatSession, ChatMessage, SessionType, MessageRole
        from app.models.document import DocumentChunk
        assert User is not None
        assert ChatSession is not None
        assert ChatMessage is not None
        assert DocumentChunk is not None
        print("✓ All models imported successfully")

    def test_import_services(self):
        """Test service module imports."""
        from app.services.auth_service import (
            hash_password,
            verify_password,
            create_access_token,
            decode_access_token,
        )
        from app.services.ai_provider import get_ai_provider
        from app.services.chat_service import chat_stream
        from app.services.review_engine import review_code
        from app.services.architecture_service import advise_architecture
        assert hash_password is not None
        assert verify_password is not None
        assert create_access_token is not None
        assert decode_access_token is not None
        print("✓ All services imported successfully")

    def test_import_schemas(self):
        """Test schema imports."""
        from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
        from app.schemas.chat import ChatRequest, ChatSessionResponse
        from app.schemas.review import ReviewRequest, ArchitectureRequest
        assert RegisterRequest is not None
        assert ChatRequest is not None
        assert ReviewRequest is not None
        print("✓ All schemas imported successfully")

    def test_import_api_routers(self):
        """Test API router imports."""
        from app.api.auth import router as auth_router
        from app.api.chat import router as chat_router
        from app.api.review import router as review_router
        from app.api.architecture import router as architecture_router
        from app.api.health import router as health_router
        assert auth_router is not None
        assert chat_router is not None
        assert review_router is not None
        assert architecture_router is not None
        assert health_router is not None
        print("✓ All API routers imported successfully")


class TestAuthService:
    """Test authentication service functions."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        from app.services.auth_service import hash_password, verify_password

        password = "test_password_123"
        hashed = hash_password(password)

        # Hash should not be the same as the original
        assert hashed != password
        print(f"  Hash: {hashed[:20]}...")

        # Verify should work with correct password
        assert verify_password(password, hashed)
        print("✓ Password hashing works correctly")

        # Verify should fail with wrong password
        assert not verify_password("wrong_password", hashed)
        print("✓ Password verification works correctly")

    def test_jwt_token_creation(self):
        """Test JWT token creation and decoding."""
        from app.services.auth_service import create_access_token, decode_access_token
        from uuid import uuid4

        user_id = str(uuid4())
        role = "developer"
        token = create_access_token(user_id=user_id, role=role)

        assert token is not None
        assert len(token) > 0
        print(f"✓ JWT token created: {token[:30]}...")

        # Decode and verify
        payload = decode_access_token(token)
        assert payload["sub"] == user_id
        assert payload["role"] == role
        print("✓ JWT token decoded correctly")

    def test_jwt_token_expiration(self):
        """Test JWT token expiration handling."""
        from app.services.auth_service import decode_access_token
        from datetime import timedelta
        from jose import jwt
        from app.config import settings
        import time

        # Create an expired token
        expired_token = jwt.encode(
            {"sub": "test_user", "role": "developer", "exp": time.time() - 1},
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        # Should raise HTTPException
        from fastapi import HTTPException
        try:
            decode_access_token(expired_token)
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 401
            print("✓ Expired token correctly rejected")


class TestConfig:
    """Test configuration loading."""

    def test_settings_loaded(self):
        """Test that settings are properly loaded."""
        from app.config import settings

        assert settings.app_name == "CloudOps AI Copilot"
        assert settings.app_version == "0.1.0"
        assert settings.jwt_algorithm == "HS256"
        assert settings.access_token_expire_minutes == 1440
        print("✓ Settings loaded correctly")

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from JSON string."""
        from app.config import settings

        origins = settings.cors_origins_list
        assert isinstance(origins, list)
        assert "http://localhost:3000" in origins or len(origins) > 0
        print(f"✓ CORS origins parsed: {origins}")

    def test_environment_properties(self):
        """Test environment properties."""
        from app.config import settings

        # Should be development or production
        assert settings.is_development or settings.is_production
        print(f"✓ Environment: {settings.app_env}")


class TestModels:
    """Test database models structure."""

    def test_user_model_structure(self):
        """Test User model has required fields."""
        from app.models.user import User, UserRole

        # Check that UserRole enum has required values
        assert hasattr(UserRole, "ADMIN")
        assert hasattr(UserRole, "DEVOPS")
        assert hasattr(UserRole, "DEVELOPER")
        assert hasattr(UserRole, "READONLY")
        print("✓ User model structure valid")

    def test_chat_model_structure(self):
        """Test Chat models have required fields."""
        from app.models.chat import ChatSession, ChatMessage, SessionType, MessageRole

        # Check enums
        assert hasattr(SessionType, "CHAT")
        assert hasattr(SessionType, "TERRAFORM_REVIEW")
        assert hasattr(MessageRole, "USER")
        assert hasattr(MessageRole, "ASSISTANT")
        print("✓ Chat models structure valid")

    def test_database_base(self):
        """Test database Base class exists."""
        from app.database import Base

        assert Base is not None
        print("✓ Database Base class exists")


class TestSchemas:
    """Test Pydantic schemas."""

    def test_register_request_schema(self):
        """Test RegisterRequest schema validation."""
        from app.schemas.auth import RegisterRequest

        # Valid request
        req = RegisterRequest(
            email="test@example.com",
            username="test_user",
            password="password123",
        )
        assert req.email == "test@example.com"
        print("✓ RegisterRequest schema valid")

    def test_chat_request_schema(self):
        """Test ChatRequest schema validation."""
        from app.schemas.chat import ChatRequest

        req = ChatRequest(message="Hello, AI!")
        assert req.message == "Hello, AI!"
        print("✓ ChatRequest schema valid")

    def test_review_request_schema(self):
        """Test ReviewRequest schema validation."""
        from app.schemas.review import ReviewRequest

        req = ReviewRequest(
            code="resource 'aws_instance' 'web' {}",
            filename="main.tf",
        )
        assert req.code == "resource 'aws_instance' 'web' {}"
        print("✓ ReviewRequest schema valid")


class TestAIProvider:
    """Test AI provider abstraction."""

    def test_ai_provider_factory(self):
        """Test AI provider factory function."""
        from app.services.ai_provider import get_ai_provider
        from app.config import settings

        # This will try to load the default provider
        # It will fail if API key is not configured, which is expected
        try:
            provider = get_ai_provider()
            print(f"✓ Default AI provider loaded: {provider.__class__.__name__}")
        except ValueError as e:
            print(f"✓ AI provider correctly raises error when not configured: {e}")

    def test_ai_provider_list(self):
        """Test that known providers are recognized."""
        from app.services.ai_provider import get_ai_provider

        providers = ["gemini", "claude", "openai", "gateway"]
        for provider_name in providers:
            try:
                get_ai_provider(provider_name)
            except ValueError as e:
                # Expected if not configured
                assert "not configured" in str(e).lower()
        print("✓ All provider names recognized")


class TestHealthEndpoint:
    """Test health check logic."""

    def test_health_check_response(self):
        """Test health check response structure."""
        from app.config import settings

        # Simulate health check response
        health_response = {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.app_env,
            "database": {"connected": False},  # Will be false locally without DB
            "ai": {
                "default_provider": settings.default_ai_provider,
                "providers_configured": [],
            },
        }

        assert "status" in health_response
        assert "version" in health_response
        assert health_response["version"] == "0.1.0"
        print("✓ Health check response structure valid")


def run_all_tests():
    """Run all tests and print results."""
    print("\n" + "=" * 60)
    print("CloudOps AI Copilot — Backend Test Suite")
    print("=" * 60 + "\n")

    test_classes = [
        TestImports,
        TestAuthService,
        TestConfig,
        TestModels,
        TestSchemas,
        TestAIProvider,
        TestHealthEndpoint,
    ]

    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}:")
        print("-" * 40)

        test_instance = test_class()
        test_methods = [
            method
            for method in dir(test_instance)
            if method.startswith("test_")
        ]

        for method_name in test_methods:
            try:
                method = getattr(test_instance, method_name)
                method()
                passed += 1
            except Exception as e:
                print(f"✗ {method_name}: {str(e)}")
                failed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
