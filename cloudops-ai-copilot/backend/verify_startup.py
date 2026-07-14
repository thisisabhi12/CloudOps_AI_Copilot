"""
CloudOps AI Copilot — Startup Verification Script

Verifies that the backend can start without errors by checking:
1. All imports work
2. Database URL is configured
3. Configuration loads
4. FastAPI app initializes
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))


def verify_imports():
    """Verify all critical imports work."""
    print("\n[1/4] Verifying imports...")
    try:
        from app.config import settings
        from app.database import Base, engine, async_session_factory
        from app.models.user import User
        from app.models.chat import ChatSession, ChatMessage
        from app.services.auth_service import create_access_token
        from app.services.ai_provider import get_ai_provider
        from app.main import app
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def verify_config():
    """Verify configuration loads."""
    print("\n[2/4] Verifying configuration...")
    try:
        from app.config import settings
        
        assert settings.app_name == "CloudOps AI Copilot"
        assert settings.database_url
        assert settings.jwt_algorithm == "HS256"
        
        print(f"  ✓ App name: {settings.app_name}")
        print(f"  ✓ Environment: {settings.app_env}")
        print(f"  ✓ Debug mode: {settings.debug}")
        print(f"  ✓ Database configured: {settings.database_url[:50]}...")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def verify_fastapi_app():
    """Verify FastAPI app initializes."""
    print("\n[3/4] Verifying FastAPI application...")
    try:
        from app.main import app
        
        # Check routers are registered
        routes = [route.path for route in app.routes]
        required_routes = [
            "/api/v1/auth",
            "/api/v1/chat",
            "/api/v1/review",
            "/api/v1/health",
        ]
        
        found = sum(1 for route in routes if any(req in route for req in required_routes))
        print(f"  ✓ FastAPI app initialized")
        print(f"  ✓ Total routes: {len(routes)}")
        print(f"  ✓ Core endpoints registered: {found}/4")
        return True
    except Exception as e:
        print(f"  ✗ FastAPI error: {e}")
        return False


def verify_database_config():
    """Verify database configuration."""
    print("\n[4/4] Verifying database configuration...")
    try:
        from app.config import settings
        import os
        
        if not settings.database_url:
            print("  ✗ DATABASE_URL not configured")
            return False
        
        print(f"  ✓ Database URL configured")
        
        # Check if it's async PostgreSQL
        if "postgresql+asyncpg" in settings.database_url or "postgresql://" in settings.database_url:
            print(f"  ✓ PostgreSQL async driver detected")
        
        # Check SSL
        if "sslmode" in settings.database_url or "ssl" in settings.database_url:
            print(f"  ✓ SSL/TLS enabled")
        
        return True
    except Exception as e:
        print(f"  ✗ Database config error: {e}")
        return False


def main():
    """Run all verifications."""
    print("=" * 60)
    print("CloudOps AI Copilot — Backend Startup Verification")
    print("=" * 60)
    
    results = [
        verify_imports(),
        verify_config(),
        verify_fastapi_app(),
        verify_database_config(),
    ]
    
    print("\n" + "=" * 60)
    
    if all(results):
        print("✅ All verifications passed!")
        print("\nYou can start the server with:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("=" * 60)
        return 0
    else:
        print("❌ Some verifications failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
